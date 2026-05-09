#!/usr/bin/env python3
"""One-command TravelBuddy demo workflow.

This is orchestration only. It reuses the existing helper scripts and does not
change the core editing engine.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

from helpers.caption_styles import CaptionStyle, get_caption_style
from helpers.export_presets import ExportPreset, get_export_preset
from helpers.script_engine import generate_script_stub, get_routing_hint, normalize_content_type


REPO_ROOT = Path(__file__).resolve().parent
HELPER_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3.11"
DEFAULT_BRAND = "TRAVELBUDDY"
DEFAULT_STYLE = "cinematic"
DEFAULT_EXPORT_PRESET = "cinematic_916"
DEFAULT_CAPTION_STYLE = "cinematic_gold"
DEFAULT_CONTENT_TYPE = "mentor_pitch"
BRANDING_ROOT = REPO_ROOT / "branding"
BRANDING_ASSETS = BRANDING_ROOT / "assets"
PAUSE_PROFILE_DEFAULT = "natural"
PAUSE_PROFILE_MS = {
    "tight": 120,
    "natural": 220,
    "dramatic": 380,
}


@dataclass(frozen=True)
class BrandingHooks:
    active: bool
    brand: str
    style: str
    watermark_path: Path | None
    endcard_path: Path | None
    subtitle_style: str


@dataclass(frozen=True)
class WatermarkSettings:
    scale: float
    opacity: float
    margin: int


@dataclass(frozen=True)
class DemoContentMetadata:
    export_preset: ExportPreset
    caption_style: CaptionStyle
    content_type: str
    script_stub: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "export_preset": self.export_preset.name,
            "export_preset_details": asdict(self.export_preset),
            "caption_style": self.caption_style.name,
            "caption_style_details": asdict(self.caption_style),
            "content_type": self.content_type,
            "script_stub": self.script_stub,
        }


def write_generated_script(edit_dir: Path, script: dict[str, object]) -> Path:
    out_path = edit_dir / "generated_script.json"
    out_path.write_text(json.dumps(script, indent=2))
    return out_path


def augment_transcript_with_script(transcript_path: Path, script: dict[str, object]) -> None:
    transcript = json.loads(transcript_path.read_text())
    transcript["voice_chunks"] = script.get("voice_chunks", [])
    transcript["suggested_pause_ms"] = script.get("suggested_pause_ms")
    transcript["pause_profile"] = script.get("pause_profile")
    transcript["applied_pause_ms"] = script.get("applied_pause_ms")
    transcript["caption_groups"] = script.get("caption_groups", [])
    transcript["emphasis_words"] = script.get("emphasis_words", [])
    transcript["emphasis_pop_ms"] = script.get("emphasis_pop_ms")
    transcript["script_style"] = script.get("script_style")
    transcript["generated_script_path"] = str(transcript_path.parent.parent / "generated_script.json")
    transcript_path.write_text(json.dumps(transcript, indent=2))


def log(step: int, total: int, message: str) -> None:
    print(f"[{step}/{total}] {message}", flush=True)


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def helper_python() -> str:
    return str(HELPER_PYTHON if HELPER_PYTHON.exists() else Path(sys.executable))


def require_tools(names: list[str]) -> None:
    missing = [name for name in names if shutil.which(name) is None]
    if missing:
        raise SystemExit(f"missing required tools on PATH: {', '.join(missing)}")


def probe_duration(video_path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def probe_dimensions(video_path: Path) -> tuple[int, int]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    width_str, height_str = result.stdout.strip().split("x", 1)
    return int(width_str), int(height_str)


def ass_timestamp(seconds: float) -> str:
    total_cs = int(round(max(0.0, seconds) * 100))
    hours, rem = divmod(total_cs, 360000)
    minutes, rem = divmod(rem, 6000)
    secs, centis = divmod(rem, 100)
    return f"{hours:d}:{minutes:02d}:{secs:02d}.{centis:02d}"


def escape_ass_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def generate_demo_video(video_path: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "testsrc=size=320x180:rate=24:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2:sample_rate=48000",
            "-shortest",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(video_path),
        ]
    )


def copy_input(input_path: Path, dest_path: Path) -> None:
    shutil.copy2(input_path, dest_path)


def resolve_branding_hooks(brand: str, style: str) -> BrandingHooks:
    brand_name = brand.strip().upper() or DEFAULT_BRAND
    style_name = style.strip().lower() or DEFAULT_STYLE
    active = brand_name == DEFAULT_BRAND

    if not active:
        return BrandingHooks(
            active=False,
            brand=brand_name,
            style=style_name,
            watermark_path=None,
            endcard_path=None,
            subtitle_style="default",
        )

    watermark_path = BRANDING_ASSETS / "watermarks" / "travelbuddy_lion_watermark.png"
    endcard_path = BRANDING_ASSETS / "endcards" / "travelbuddy_luxury_endcard.png"
    subtitle_style_map = {
        "cinematic": "travelbuddy_cinematic",
        "luxury": "travelbuddy_luxury",
        "luxury travel": "travelbuddy_luxury",
        "breaking news": "travelbuddy_breaking_news",
        "ai mentor": "travelbuddy_ai_mentor",
        "documentary": "travelbuddy_documentary",
        "hype reel": "travelbuddy_hype_reel",
    }
    subtitle_style = subtitle_style_map.get(style_name, "travelbuddy_default")

    return BrandingHooks(
        active=True,
        brand=brand_name,
        style=style_name,
        watermark_path=watermark_path,
        endcard_path=endcard_path,
        subtitle_style=subtitle_style,
    )


def resolve_export_preset(name: str) -> ExportPreset:
    return get_export_preset(name)


def resolve_caption_style(name: str) -> CaptionStyle:
    return get_caption_style(name)


def resolve_social_ready_options(args: argparse.Namespace) -> argparse.Namespace:
    args.brand = args.brand or DEFAULT_BRAND
    args.style = args.style or DEFAULT_STYLE
    args.export_preset = args.export_preset or DEFAULT_EXPORT_PRESET
    args.caption_style = args.caption_style or DEFAULT_CAPTION_STYLE
    args.content_type = args.content_type or DEFAULT_CONTENT_TYPE
    args.tts_provider = args.tts_provider or "placeholder"
    args.pause_profile = args.pause_profile or PAUSE_PROFILE_DEFAULT
    return args


def resolve_travelbuddy_reel_options(args: argparse.Namespace) -> argparse.Namespace:
    args.social_ready = True
    args.brand = args.brand or DEFAULT_BRAND
    args.style = args.style or DEFAULT_STYLE
    args.export_preset = args.export_preset or DEFAULT_EXPORT_PRESET
    args.caption_style = args.caption_style or DEFAULT_CAPTION_STYLE
    args.content_type = args.content_type or DEFAULT_CONTENT_TYPE
    args.tts_provider = args.tts_provider or "piper"
    args.pause_profile = args.pause_profile or PAUSE_PROFILE_DEFAULT
    args.piper_voice = args.piper_voice or "en_US-lessac-low"
    return args


def resolve_travelbuddy_reel_options(args: argparse.Namespace) -> argparse.Namespace:
    args.social_ready = True
    args.brand = args.brand or DEFAULT_BRAND
    args.style = args.style or DEFAULT_STYLE
    args.export_preset = args.export_preset or DEFAULT_EXPORT_PRESET
    args.caption_style = args.caption_style or DEFAULT_CAPTION_STYLE
    args.content_type = args.content_type or DEFAULT_CONTENT_TYPE
    args.tts_provider = args.tts_provider or "piper"
    args.pause_profile = args.pause_profile or PAUSE_PROFILE_DEFAULT
    args.piper_voice = args.piper_voice or "en_US-lessac-low"
    return args


def resolve_pause_ms(pause_profile: str, pause_ms: int | None) -> int:
    if pause_ms is not None and pause_ms >= 0:
        return int(pause_ms)
    profile = (pause_profile or PAUSE_PROFILE_DEFAULT).strip().lower()
    return int(PAUSE_PROFILE_MS.get(profile, PAUSE_PROFILE_MS[PAUSE_PROFILE_DEFAULT]))


def preset_dimensions(preset: ExportPreset) -> tuple[int, int]:
    width_str, height_str = preset.resolution.lower().split("x", 1)
    return int(width_str), int(height_str)


def log_preset_metadata(preset: ExportPreset) -> None:
    print(f"  export preset: {preset.name} -> {preset.resolution} ({preset.aspect_ratio})", flush=True)
    print(f"  subtitle safe zone: {preset.subtitle_safe_zone}", flush=True)
    print(f"  watermark safe zone: {preset.watermark_safe_zone}", flush=True)
    print(f"  end card safe zone: {preset.end_card_safe_zone}", flush=True)
    print(f"  output suffix: {preset.output_suffix}", flush=True)


def ass_color_from_hex(hex_color: str) -> str:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        return "&H00FFFFFF"
    r = value[0:2]
    g = value[2:4]
    b = value[4:6]
    return f"&H00{b.upper()}{g.upper()}{r.upper()}"


def normalize_emphasis_words(words: object) -> set[str]:
    result: set[str] = set()
    if not isinstance(words, list):
        return result
    for word in words:
        if not isinstance(word, str):
            continue
        cleaned = re.sub(r"^[^\w']+|[^\w']+$", "", word.strip().lower())
        if cleaned:
            result.add(cleaned)
    return result


def matched_emphasis_words(text: str, emphasis_set: set[str]) -> list[str]:
    words = [
        re.sub(r"^[^\w']+|[^\w']+$", "", piece.strip().lower())
        for piece in text.split()
    ]
    matches: list[str] = []
    for word in words:
        if word and word in emphasis_set and word not in matches:
            matches.append(word)
    return matches


def lighten_hex_color(hex_color: str, ratio: float = 0.25) -> tuple[int, int, int, int]:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        return (245, 225, 135, 255)
    base = [int(value[i : i + 2], 16) for i in (0, 2, 4)]
    mixed = []
    for channel in base:
        mixed.append(int(round(channel + (255 - channel) * max(0.0, min(1.0, ratio)))))
    return tuple(mixed) + (255,)


def build_caption_cues(transcript: dict, total_duration: float | None = None) -> list[tuple[float, float, str]]:
    caption_groups = transcript.get("caption_groups")
    if isinstance(caption_groups, list) and caption_groups:
        cleaned_groups: list[str] = []
        for group in caption_groups:
            if isinstance(group, str):
                text = " ".join(group.strip().split())
            elif isinstance(group, dict):
                text = " ".join(str(group.get("text", "")).strip().split())
            else:
                continue
            if text:
                cleaned_groups.append(text)

        if cleaned_groups:
            duration = total_duration
            if duration is None:
                duration = float(transcript.get("source_duration") or len(cleaned_groups) * 1.2)
            duration = max(0.45, float(duration))
            group_span = duration / max(1, len(cleaned_groups))
            cues: list[tuple[float, float, str]] = []
            for idx, text in enumerate(cleaned_groups):
                start = idx * group_span
                end = duration if idx == len(cleaned_groups) - 1 else min(duration, start + group_span * 0.92)
                if end <= start:
                    end = start + 0.45
                cues.append((float(start), float(end), text.upper()))
            return cues

    words = [
        w
        for w in transcript.get("words", [])
        if w.get("type") == "word" and (w.get("text") or "").strip()
    ]
    if not words:
        text = (transcript.get("text") or "").strip()
        if not text:
            return []
        return [(0.0, 1.0, text.upper())]

    cues: list[tuple[float, float, str]] = []
    chunk: list[dict] = []
    for word in words:
        chunk.append(word)
        text = (word.get("text") or "").strip()
        ends_in_punct = bool(text) and text[-1] in ".,!?;:"
        if len(chunk) >= 2 or ends_in_punct:
            start = chunk[0].get("start")
            end = chunk[-1].get("end")
            if start is None:
                start = cues[-1][1] if cues else 0.0
            if end is None or end <= start:
                end = float(start) + 0.45
            cue_text = " ".join((w.get("text") or "").strip() for w in chunk).strip()
            cue_text = cue_text.rstrip(",;:")
            cues.append((float(start), float(end), cue_text.upper()))
            chunk = []

    if chunk:
        start = chunk[0].get("start")
        end = chunk[-1].get("end")
        if start is None:
            start = cues[-1][1] if cues else 0.0
        if end is None or end <= start:
            end = float(start) + 0.45
        cue_text = " ".join((w.get("text") or "").strip() for w in chunk).strip()
        cue_text = cue_text.rstrip(",;:")
        cues.append((float(start), float(end), cue_text.upper()))

    return cues


def parse_resolution(resolution: str) -> tuple[int, int]:
    width_str, height_str = resolution.lower().split("x", 1)
    return int(width_str), int(height_str)


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def resolve_font_path(font_name: str) -> Path:
    fallback_candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Helvetica.ttc"),
        Path("/Library/Fonts/Arial Bold.ttf"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for candidate in fallback_candidates:
        if candidate.exists():
            return candidate

    try:
        from matplotlib import font_manager
        from matplotlib.font_manager import FontProperties

        return Path(font_manager.findfont(FontProperties(family="DejaVu Sans"), fallback_to_default=True))
    except Exception:
        return Path()


def wrap_caption_lines(text: str, font, max_width: int, max_lines: int) -> list[str]:
    words = [word for word in text.split() if word]
    if not words:
        return []

    def measure(candidate: str) -> int:
        bbox = font.getbbox(candidate)
        return bbox[2] - bbox[0]

    lines: list[str] = []
    current = ""
    for idx, word in enumerate(words):
        trial = word if not current else f"{current} {word}"
        if not current or measure(trial) <= max_width:
            current = trial
            continue

        lines.append(current)
        current = word
        if len(lines) >= max_lines - 1:
            remainder = " ".join([current] + words[idx + 1 :])
            lines.append(remainder)
            return lines[:max_lines]

    if current:
        lines.append(current)

    if len(lines) > max_lines:
        merged = [" ".join(lines[: max_lines - 1]), lines[max_lines - 1]]
        return merged
    return lines


def render_caption_overlay(
    text: str,
    width: int,
    height: int,
    style: CaptionStyle,
    preset: ExportPreset,
    out_path: Path,
    emphasis_words: object | None = None,
    emphasis_boost: bool = False,
) -> None:
    from PIL import Image, ImageDraw, ImageFont

    font_path = resolve_font_path(style.font_placeholder)
    font_size = int(style.font_size)
    scale_boost = 1.0
    if emphasis_boost:
        scale_boost = 1.04
    font = ImageFont.truetype(str(font_path), int(round(font_size * scale_boost))) if font_path.exists() else ImageFont.load_default()
    highlight_size = int(round((font_size + 6) * scale_boost))
    highlight_font = ImageFont.truetype(str(font_path), highlight_size) if font_path.exists() else font
    emphasis_set = normalize_emphasis_words(emphasis_words)

    safe_zone = preset.subtitle_safe_zone
    position = style.subtitle_positioning
    max_lines = int(position.get("max_lines", 2))
    max_text_width = int(width * float(safe_zone.get("w", 0.84)))

    lines = wrap_caption_lines(text.strip().upper(), font, max_text_width, max_lines)
    if not lines:
        raise ValueError("empty caption text")

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    line_spacing = 10 if not emphasis_boost else 11
    word_spacing = 10 if not emphasis_boost else 11

    line_layouts: list[dict[str, object]] = []
    for line in lines:
        words = [piece for piece in line.split() if piece]
        segments: list[dict[str, object]] = []
        line_w = 0
        line_h = 0
        for idx, word in enumerate(words):
            cleaned = re.sub(r"^[^\w']+|[^\w']+$", "", word.strip().lower())
            emphasized = cleaned in emphasis_set
            word_font = highlight_font if emphasized else font
            bbox = draw.textbbox((0, 0), word, font=word_font, stroke_width=4)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            segments.append(
                {
                    "word": word,
                    "font": word_font,
                    "emphasized": emphasized,
                    "width": w,
                    "height": h,
                }
            )
            line_w += w
            if idx < len(words) - 1:
                line_w += word_spacing
            line_h = max(line_h, h)
        line_layouts.append({"segments": segments, "width": line_w, "height": line_h})

    text_w = max(int(layout["width"]) for layout in line_layouts)
    text_h = sum(int(layout["height"]) for layout in line_layouts) + line_spacing * (len(line_layouts) - 1)

    safe_top = int(height * float(safe_zone.get("y", 0.70)))
    safe_h = int(height * float(safe_zone.get("h", 0.18)))
    anchor_y = safe_top + int(safe_h * 0.34)
    x = (width - text_w) // 2
    y = clamp(anchor_y - (text_h // 2), safe_top, max(safe_top, safe_top + safe_h - text_h))

    shadow_color = (0, 0, 0, 180)
    gold_hex = style.emphasis_color.strip().lstrip("#")
    if len(gold_hex) == 6:
        fill = tuple(int(gold_hex[i : i + 2], 16) for i in (0, 2, 4)) + (255,)
    else:
        fill = (212, 175, 55, 255)
    highlight_fill = lighten_hex_color(style.emphasis_color, 0.32)

    current_y = y
    for layout in line_layouts:
        line_width = int(layout["width"])
        line_height = int(layout["height"])
        current_x = (width - line_width) // 2
        for segment in layout["segments"]:
            word = str(segment["word"])
            word_font = segment["font"]
            emphasized = bool(segment["emphasized"])
            word_fill = highlight_fill if emphasized else fill
            if emphasis_boost and emphasized:
                word_fill = lighten_hex_color(style.emphasis_color, 0.48)
            shadow_offset = 5 if (emphasis_boost and emphasized) else (4 if emphasized else 3)
            stroke_width = 7 if (emphasis_boost and emphasized) else (6 if emphasized else 4)
            stroke_fill = (0, 0, 0, 240 if emphasized else 220)
            draw.text(
                (current_x + shadow_offset, current_y + shadow_offset),
                word,
                font=word_font,
                fill=shadow_color,
                stroke_width=stroke_width,
                stroke_fill=shadow_color,
            )
            draw.text(
                (current_x, current_y),
                word,
                font=word_font,
                fill=word_fill,
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
            )
            bbox = draw.textbbox((0, 0), word, font=word_font, stroke_width=stroke_width)
            current_x += (bbox[2] - bbox[0]) + word_spacing
        current_y += line_height + line_spacing
    image.save(out_path)


def compute_emphasis_windows(
    transcript: dict,
    cue_start: float,
    cue_end: float,
    cue_text: str,
    emphasis_set: set[str],
    emphasis_pop_ms: int,
) -> list[tuple[float, float]]:
    if not emphasis_set:
        return []

    words = [
        word
        for word in transcript.get("words", [])
        if word.get("type") == "word" and (word.get("text") or "").strip()
    ]
    windows: list[tuple[float, float]] = []
    for word in words:
        word_start = word.get("start")
        word_end = word.get("end")
        if word_start is None or word_end is None:
            continue
        if float(word_end) < cue_start or float(word_start) > cue_end:
            continue
        cleaned = re.sub(r"^[^\w']+|[^\w']+$", "", str(word.get("text", "")).strip().lower())
        if cleaned not in emphasis_set:
            continue
        pop_seconds = max(0.12, min(0.32, float(emphasis_pop_ms) / 1000.0))
        start = max(cue_start, float(word_start) - min(0.05, pop_seconds * 0.22))
        end = min(cue_end, float(word_end) + min(0.09, pop_seconds * 0.38))
        if end <= start:
            end = min(cue_end, start + pop_seconds)
        windows.append((start, end))
        if len(windows) >= 2:
            break

    if windows:
        return windows

    matches = matched_emphasis_words(cue_text, emphasis_set)
    if not matches:
        return []

    cue_span = max(0.18, min(0.32, max((cue_end - cue_start) * 0.34, float(emphasis_pop_ms) / 1000.0)))
    midpoint = cue_start + max(0.08, min((cue_end - cue_start) / 2.0, cue_end - cue_start - 0.08))
    start = max(cue_start, midpoint - cue_span / 2.0)
    end = min(cue_end, start + cue_span)
    if end <= start:
        end = min(cue_end, start + 0.18)
    return [(start, end)]


def build_caption_overlay_assets(
    transcript: dict,
    style: CaptionStyle,
    preset: ExportPreset,
    asset_dir: Path,
    total_duration: float | None = None,
) -> list[tuple[float, float, Path]]:
    cues = build_caption_cues(transcript, total_duration=total_duration)
    if not cues:
        raise ValueError("no usable caption cues")

    width, height = parse_resolution(preset.resolution)
    asset_dir.mkdir(parents=True, exist_ok=True)
    overlays: list[tuple[float, float, Path]] = []
    emphasis_words = transcript.get("emphasis_words")
    emphasis_set = normalize_emphasis_words(emphasis_words)
    emphasis_pop_ms = int(transcript.get("emphasis_pop_ms") or 180)
    for idx, (start, end, text) in enumerate(cues):
        overlay_path = asset_dir / f"caption_{idx:02d}.png"
        render_caption_overlay(text, width, height, style, preset, overlay_path, emphasis_words=emphasis_words)
        overlays.append((start, end, overlay_path))
        if emphasis_set:
            for emphasis_idx, (pop_start, pop_end) in enumerate(
                compute_emphasis_windows(transcript, start, end, text, emphasis_set, emphasis_pop_ms)
            ):
                emphasis_path = asset_dir / f"caption_{idx:02d}_emphasis_{emphasis_idx:02d}.png"
                render_caption_overlay(
                    text,
                    width,
                    height,
                    style,
                    preset,
                    emphasis_path,
                    emphasis_words=emphasis_words,
                    emphasis_boost=True,
                )
                overlays.append((pop_start, pop_end, emphasis_path))
    return overlays


def build_ass_captions(transcript: dict, style: CaptionStyle, out_path: Path) -> Path:
    cues = build_caption_cues(transcript)
    if not cues:
        raise ValueError("no usable caption cues")

    position = style.subtitle_positioning
    margin_v = int(position.get("margin_v", 120))
    font_size = int(style.font_size)
    font_name = style.font_placeholder or "Helvetica"
    primary = ass_color_from_hex(style.emphasis_color)
    outline = ass_color_from_hex("#000000")

    header = "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "WrapStyle: 2",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
            (
                "Style: Default,"
                f"{font_name},{font_size},{primary},{primary},{outline},&H00000000,"
                "1,0,0,0,100,100,0,0,1,3,1,2,60,60,"
                f"{margin_v},1"
            ),
            "",
            "[Events]",
            "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
        ]
    )
    lines = [header]
    for start, end, text in cues:
        lines.append(
            "Dialogue: 0,"
            f"{ass_timestamp(start)},"
            f"{ass_timestamp(end)},"
            "Default,,0,0,0,,"
            f"{escape_ass_text(text)}"
        )
    out_path.write_text("\n".join(lines) + "\n")
    return out_path


def build_content_metadata(
    export_preset: ExportPreset,
    caption_style: CaptionStyle,
    content_type: str,
    brand: str,
    topic: str | None = None,
) -> DemoContentMetadata:
    if topic:
        script_stub = generate_script_stub(
            topic,
            content_type,
            brand=brand,
            export_preset=export_preset.name,
            caption_style=caption_style.name,
        )
    else:
        content_key = normalize_content_type(str(content_type))
        script_stub = {
            "brand": brand.strip().upper() or DEFAULT_BRAND,
            "content_type": content_key,
            "export_preset": export_preset.name,
            "caption_style": caption_style.name,
            "routing_hint": get_routing_hint(content_key),
            "notes": [
                "future LLM call site",
                "keep transcript contract unchanged",
                "route content type into travel-specific script prompts",
            ],
        }
    return DemoContentMetadata(
        export_preset=export_preset,
        caption_style=caption_style,
        content_type=str(script_stub["content_type"]),
        script_stub=script_stub,
    )


def write_edl(
    edit_dir: Path,
    source_name: str,
    source_path: Path,
    duration: float,
    metadata: dict[str, object] | None = None,
) -> Path:
    segment_end = min(duration, 1.0)
    if segment_end <= 0.0:
        segment_end = duration

    edl = {
        "version": 1,
        "sources": {source_name: str(source_path.resolve())},
        "ranges": [
            {
                "source": source_name,
                "start": 0.0,
                "end": segment_end,
                "beat": "PLACEHOLDER",
                "quote": "placeholder",
                "reason": "TravelBuddy demo orchestration.",
            }
        ],
        "grade": "none",
        "overlays": [],
        "total_duration_s": segment_end,
    }
    if metadata:
        edl["metadata"] = metadata

    edl_path = edit_dir / "edl.json"
    edl_path.write_text(json.dumps(edl, indent=2))
    return edl_path


def gather_generated_files(workspace: Path) -> list[Path]:
    files = [p for p in workspace.rglob("*") if p.is_file()]
    return sorted(files)


def asset_exists(path: Path | None) -> bool:
    return path is not None and path.exists()


def has_audio_stream(video_path: Path) -> bool:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(result.stdout.strip())


def build_branded_preview(
    preview_path: Path,
    branded_path: Path,
    hooks: BrandingHooks,
    watermark: WatermarkSettings,
) -> bool:
    if not hooks.active:
        print("Branding disabled; skipping branded preview", flush=True)
        return False

    if not asset_exists(hooks.watermark_path):
        print(f"Branding asset missing, skipping watermark: {hooks.watermark_path}", flush=True)
        return False

    if not asset_exists(hooks.endcard_path):
        print(f"Branding asset missing, skipping end card: {hooks.endcard_path}", flush=True)
        return False

    with tempfile.TemporaryDirectory(prefix="travelbuddy_brand_") as tmp:
        tmpdir = Path(tmp)
        watermarked = tmpdir / "preview_watermarked.mp4"
        endcard_clip = tmpdir / "endcard.mp4"
        preview_width, preview_height = probe_dimensions(preview_path)
        preview_has_audio = has_audio_stream(preview_path)

        if preview_has_audio:
            print("Audio detected; preserving preview audio during branded export", flush=True)
        else:
            print("No audio detected; using video-only branded export", flush=True)

        print("Applying TravelBuddy watermark and end card...", flush=True)
        watermark_filter = (
            f"[1:v]format=rgba,colorchannelmixer=aa={watermark.opacity:.3f},"
            f"scale=iw*{watermark.scale:.3f}:-1[wm];"
            f"[0:v][wm]overlay=W-w-{watermark.margin}:H-h-{watermark.margin}:format=auto[outv]"
        )
        watermark_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(preview_path),
            "-i",
            str(hooks.watermark_path),
            "-filter_complex",
            watermark_filter,
            "-map",
            "[outv]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
        ]
        if preview_has_audio:
            watermark_cmd.extend(["-map", "0:a", "-c:a", "copy"])
        watermark_cmd.append(str(watermarked))
        run(watermark_cmd)

        endcard_cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-t",
            "2",
            "-i",
            str(hooks.endcard_path),
            "-f",
            "lavfi",
            "-t",
            "2",
            "-i",
            "anullsrc=channel_layout=mono:sample_rate=48000",
            "-filter_complex",
            (
                f"[0:v]scale={preview_width}:{preview_height}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={preview_width}:{preview_height}:(ow-iw)/2:(oh-ih)/2,"
                "setsar=1,format=yuv420p[v]"
            ),
            "-map",
            "[v]",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "24",
            "-movflags",
            "+faststart",
        ]
        if preview_has_audio:
            endcard_cmd.extend(
                [
                    "-map",
                    "1:a",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-ar",
                    "48000",
                    "-shortest",
                ]
            )
        endcard_cmd.append(str(endcard_clip))
        run(endcard_cmd)

        concat_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(watermarked),
            "-i",
            str(endcard_clip),
        ]
        if preview_has_audio:
            concat_cmd.extend(
                [
                    "-filter_complex",
                    "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
                    "-map",
                    "[v]",
                    "-map",
                    "[a]",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                ]
            )
        else:
            concat_cmd.extend(
                [
                    "-filter_complex",
                    "[0:v][1:v]concat=n=2:v=1:a=0[v]",
                    "-map",
                    "[v]",
                ]
            )
        concat_cmd.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(branded_path),
            ]
        )
        run(concat_cmd)

    return True


def build_vertical_export(
    branded_path: Path,
    out_path: Path,
    preset: ExportPreset,
) -> bool:
    if preset.name != "cinematic_916":
        print(f"Vertical export preset metadata only: {preset.name}", flush=True)
        return False

    width, height = preset_dimensions(preset)
    has_audio = has_audio_stream(branded_path)
    print("Building vertical social export from branded preview...", flush=True)
    print(f"  target resolution: {width}x{height}", flush=True)
    log_preset_metadata(preset)
    print(f"  output path: {out_path}", flush=True)

    filter_complex = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(branded_path),
        "-vf",
        filter_complex,
        "-map",
        "0:v:0",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
    ]
    if has_audio:
        cmd.extend(["-map", "0:a", "-c:a", "copy"])
    cmd.append(str(out_path))
    run(cmd)
    return True


def build_captioned_vertical_export(
    vertical_path: Path,
    transcript_path: Path | None,
    out_path: Path,
    caption_style: CaptionStyle,
    preset: ExportPreset,
) -> bool:
    if preset.name != "cinematic_916" or caption_style.name != "cinematic_gold":
        print(f"Caption rendering metadata only: preset={preset.name} style={caption_style.name}", flush=True)
        return False

    print("Building captioned vertical export...", flush=True)
    print(f"  caption style selected: {caption_style.name}", flush=True)
    print(f"  transcript source: {transcript_path if transcript_path is not None else 'missing'}", flush=True)
    print(f"  caption output path: {out_path}", flush=True)
    print(f"  subtitle safe-zone metadata: {caption_style.subtitle_positioning}", flush=True)
    print("  caption rendering method: image overlays via Pillow", flush=True)
    if transcript_path is None:
        print("  warning: transcript JSON missing; copying vertical export without captions", flush=True)
        shutil.copy2(vertical_path, out_path)
        return True
    if not transcript_path.exists():
        print(f"  warning: transcript JSON missing; copying vertical export without captions ({transcript_path})", flush=True)
        shutil.copy2(vertical_path, out_path)
        return True

    transcript = json.loads(transcript_path.read_text())
    vertical_duration = probe_duration(vertical_path)
    cues = build_caption_cues(transcript, total_duration=vertical_duration)
    if not cues:
        print("  warning: transcript timings incomplete; copying vertical export without captions", flush=True)
        shutil.copy2(vertical_path, out_path)
        return True

    asset_dir = out_path.parent / "caption_overlays" / preset.name / caption_style.name
    caption_groups = transcript.get("caption_groups")
    if isinstance(caption_groups, list) and caption_groups:
        print(f"  caption groups: {len(caption_groups)}", flush=True)
    emphasis_words = transcript.get("emphasis_words")
    if isinstance(emphasis_words, list) and emphasis_words:
        print(f"  emphasis words: {len(emphasis_words)}", flush=True)
        print("  emphasis timing enabled: subtle timed pop overlays", flush=True)
        print(f"  emphasis pop hint: {transcript.get('emphasis_pop_ms', 'default')} ms", flush=True)
    try:
        overlays = build_caption_overlay_assets(
            transcript,
            caption_style,
            preset,
            asset_dir,
            total_duration=vertical_duration,
        )
        if isinstance(emphasis_words, list) and emphasis_words:
            print(f"  emphasis render path: {asset_dir}", flush=True)
    except ValueError:
        print("  warning: caption cues unavailable; copying vertical export without captions", flush=True)
        shutil.copy2(vertical_path, out_path)
        return True

    has_audio = has_audio_stream(vertical_path)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(vertical_path),
    ]
    for _, _, overlay_path in overlays:
        cmd.extend(["-i", str(overlay_path)])

    filter_parts: list[str] = []
    prev_label = "[0:v]"
    for idx, (start, end, _) in enumerate(overlays, start=1):
        out_label = f"[v{idx}]"
        filter_parts.append(
            f"{prev_label}[{idx}:v]overlay=0:0:enable='between(t,{start:.3f},{end:.3f})'{out_label}"
        )
        prev_label = out_label

    cmd.extend(["-filter_complex", ";".join(filter_parts)])
    cmd.extend(["-map", prev_label])
    if has_audio:
        cmd.extend(["-map", "0:a", "-c:a", "copy"])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(out_path),
        ]
    )
    run(cmd)
    return True


def choose_final_social_output(
    edit_dir: Path,
    captioned_path: Path | None,
    branded_916_path: Path | None,
    branded_path: Path | None,
) -> Path | None:
    final_path = edit_dir / "final_social.mp4"
    source_path: Path | None = None

    if captioned_path is not None and captioned_path.exists():
        source_path = captioned_path
    elif branded_916_path is not None and branded_916_path.exists():
        source_path = branded_916_path
    elif branded_path is not None and branded_path.exists():
        source_path = branded_path

    if source_path is None:
        print("  warning: social-ready final export could not be resolved", flush=True)
        return None

    shutil.copy2(source_path, final_path)
    print(f"Final social export path: {final_path}", flush=True)
    if source_path != captioned_path:
        print(f"  note: final social export fell back to {source_path.name}", flush=True)
    return final_path


def print_social_ready_banner(final_path: Path, preset: ExportPreset, caption_style: CaptionStyle, tts_provider: str) -> None:
    print()
    print("==================================================", flush=True)
    print("TRAVELBUDDY FINAL SOCIAL EXPORT READY", flush=True)
    print("==================================================", flush=True)
    print("Output:", flush=True)
    print(f"edit/{final_path.name}", flush=True)
    print("", flush=True)
    print("Preset:", flush=True)
    print(preset.name, flush=True)
    print("", flush=True)
    print("Caption Style:", flush=True)
    print(caption_style.name, flush=True)
    print("", flush=True)
    print("TTS Provider:", flush=True)
    print(tts_provider, flush=True)
    print("", flush=True)
    print("==================================================", flush=True)


def print_travelbuddy_reel_banner(topic: str, final_path: Path) -> None:
    print()
    print("==================================================", flush=True)
    print("TRAVELBUDDY REEL READY", flush=True)
    print("==================================================", flush=True)
    print("Topic:", flush=True)
    print(topic or "Untitled idea", flush=True)
    print("", flush=True)
    print("Final Output:", flush=True)
    print(f"edit/{final_path.name}", flush=True)
    print("", flush=True)
    print("Preset Stack:", flush=True)
    print("- cinematic_916", flush=True)
    print("- cinematic_gold", flush=True)
    print(f"- {PAUSE_PROFILE_DEFAULT} pacing", flush=True)
    print("- Piper narration", flush=True)
    print("", flush=True)
    print("==================================================", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the TravelBuddy placeholder demo workflow")
    ap.add_argument(
        "--travelbuddy-reel",
        action="store_true",
        help="Enable the flagship TravelBuddy reel preset stack",
    )
    ap.add_argument(
        "--social-ready",
        action="store_true",
        help="Enable the TravelBuddy final social export preset",
    )
    ap.add_argument("--input", type=Path, default=None, help="Optional input video path")
    ap.add_argument("--brand", type=str, default=None, help="Brand label placeholder")
    ap.add_argument("--style", type=str, default=None, help="Render style placeholder")
    ap.add_argument(
        "--export-preset",
        type=str,
        default=None,
        help="Export preset metadata name (default: cinematic_916)",
    )
    ap.add_argument(
        "--caption-style",
        type=str,
        default=None,
        help="Caption style metadata name (default: cinematic_gold)",
    )
    ap.add_argument(
        "--content-type",
        type=str,
        default=None,
        help="Content type metadata name (default: mentor_pitch)",
    )
    ap.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Optional topic to generate a lightweight script",
    )
    ap.add_argument(
        "--pause-profile",
        type=str,
        default=None,
        choices=["tight", "natural", "dramatic"],
        help="Pause profile used between generated narration chunks",
    )
    ap.add_argument(
        "--pause-ms",
        type=int,
        default=None,
        help="Override pause length between generated narration chunks in milliseconds",
    )
    ap.add_argument(
        "--tts-provider",
        type=str,
        default=None,
        choices=["placeholder", "piper"],
        help="TTS provider selection (default: placeholder)",
    )
    ap.add_argument(
        "--piper-voice",
        type=str,
        default="en_US-lessac-low",
        help="Piper voice name (default: en_US-lessac-low)",
    )
    ap.add_argument(
        "--piper-data-dir",
        type=Path,
        default=None,
        help="Piper data directory (default: <workspace>/edit/piper_data)",
    )
    ap.add_argument(
        "--watermark-scale",
        type=float,
        default=0.22,
        help="TravelBuddy watermark scale multiplier",
    )
    ap.add_argument(
        "--watermark-opacity",
        type=float,
        default=0.85,
        help="TravelBuddy watermark opacity multiplier",
    )
    ap.add_argument(
        "--watermark-margin",
        type=int,
        default=32,
        help="TravelBuddy watermark margin in pixels",
    )
    args = ap.parse_args()

    if args.travelbuddy_reel:
        args = resolve_travelbuddy_reel_options(args)
    if args.social_ready:
        args = resolve_social_ready_options(args)
    else:
        args.brand = args.brand or DEFAULT_BRAND
        args.style = args.style or DEFAULT_STYLE
        args.export_preset = args.export_preset or DEFAULT_EXPORT_PRESET
        args.caption_style = args.caption_style or DEFAULT_CAPTION_STYLE
        args.content_type = args.content_type or DEFAULT_CONTENT_TYPE
        args.tts_provider = args.tts_provider or "placeholder"
        args.pause_profile = args.pause_profile or PAUSE_PROFILE_DEFAULT

    require_tools(["ffmpeg", "ffprobe"])
    hooks = resolve_branding_hooks(args.brand, args.style)
    try:
        export_preset = resolve_export_preset(args.export_preset)
        caption_style = resolve_caption_style(args.caption_style)
    except KeyError as exc:
        raise SystemExit(str(exc)) from exc
    content_metadata = build_content_metadata(
        export_preset=export_preset,
        caption_style=caption_style,
        content_type=args.content_type,
        brand=args.brand,
        topic=args.topic,
    )
    applied_pause_ms = resolve_pause_ms(args.pause_profile, args.pause_ms)
    content_metadata.script_stub["pause_profile"] = args.pause_profile
    content_metadata.script_stub["applied_pause_ms"] = applied_pause_ms
    watermark = WatermarkSettings(
        scale=args.watermark_scale,
        opacity=args.watermark_opacity,
        margin=args.watermark_margin,
    )

    workspace = Path(tempfile.mkdtemp(prefix="travelbuddy_demo_")).resolve()
    edit_dir = workspace / "edit"
    verify_dir = edit_dir / "verify"
    edit_dir.mkdir(parents=True, exist_ok=True)
    verify_dir.mkdir(parents=True, exist_ok=True)

    source_name = "demo_sample.mp4"
    source_path = workspace / source_name

    log(1, 5, "Generating demo video..." if args.input is None else "Preparing input video...")
    if args.input is None:
        generate_demo_video(source_path)
    else:
        input_path = args.input.resolve()
        if not input_path.exists():
            raise SystemExit(f"input video not found: {input_path}")
        source_name = input_path.name
        source_path = workspace / source_name
        copy_input(input_path, source_path)

    duration = probe_duration(source_path)

    log(2, 5, f"Running transcript pipeline... [brand={args.brand}] [style={args.style}]")
    if hooks.active:
        print("TravelBuddy branding mode active", flush=True)
        print(f"  watermark hook: {hooks.watermark_path}", flush=True)
        print(f"  end card hook: {hooks.endcard_path}", flush=True)
        print(f"  subtitle style: {hooks.subtitle_style}", flush=True)
        print(
            "  watermark tuning: "
            f"scale={watermark.scale:.3f} opacity={watermark.opacity:.3f} margin={watermark.margin}",
            flush=True,
        )
        log_preset_metadata(export_preset)
        print(
            "  caption style: "
            f"{caption_style.name} / content type: {content_metadata.content_type}",
            flush=True,
        )
        print(
            f"  narration pause profile: {args.pause_profile} / {applied_pause_ms} ms",
            flush=True,
        )
        print(f"  script routing: {content_metadata.script_stub['routing_hint']}", flush=True)
        if args.travelbuddy_reel:
            print("  flagship reel preset: enabled", flush=True)
    else:
        print("Branding mode inactive; using default placeholders", flush=True)
    generated_script_path: Path | None = None
    narration_text: str | None = None
    narration_chunks: list[str] | None = None
    if args.topic:
        generated_script_path = write_generated_script(edit_dir, content_metadata.script_stub)
        narration_text = str(content_metadata.script_stub.get("voice_text", "")).strip() or None
        narration_chunks = [
            str(chunk).strip()
            for chunk in content_metadata.script_stub.get("voice_chunks", [])
            if str(chunk).strip()
        ]
        print(f"  topic: {args.topic}", flush=True)
        print(f"  generated headline: {content_metadata.script_stub.get('headline', '')}", flush=True)
        print(f"  content type: {content_metadata.content_type}", flush=True)
        print(f"  narration length: {len(narration_text or '')} chars", flush=True)
        print(f"  applied pause: {applied_pause_ms} ms", flush=True)
        print(f"  generated script path: {generated_script_path}", flush=True)
    transcribe_cmd = [
        helper_python(),
        str(REPO_ROOT / "helpers" / "transcribe_batch.py"),
        str(workspace),
        "--workers",
        "1",
        "--tts-provider",
        args.tts_provider,
        "--piper-voice",
        args.piper_voice,
    ]
    if args.piper_data_dir is not None:
        # Insert as a separate subprocess arg only when explicitly set.
        # This keeps the default workspace layout unchanged.
        transcribe_cmd.extend(["--piper-data-dir", str(args.piper_data_dir)])
    if narration_text:
        transcribe_cmd.extend(["--narration-text", narration_text])
    for chunk in narration_chunks or []:
        transcribe_cmd.extend(["--narration-chunk", chunk])
    transcribe_cmd.extend(["--pause-profile", args.pause_profile, "--pause-ms", str(applied_pause_ms)])
    try:
        run(transcribe_cmd, cwd=REPO_ROOT)
    except subprocess.CalledProcessError as exc:
        if args.tts_provider == "piper":
            print("Piper narration failed. Install guidance:", flush=True)
            print("  python3.11 -m pip install piper-tts", flush=True)
            print("  python3.11 -m piper.download_voices en_US-lessac-low --data-dir ./models/piper", flush=True)
        raise SystemExit(exc.returncode) from exc

    if generated_script_path is not None:
        transcript_path = edit_dir / "transcripts" / f"{Path(source_name).stem}.json"
        if transcript_path.exists():
            augment_transcript_with_script(transcript_path, content_metadata.script_stub)

    log(3, 5, "Packing transcripts...")
    run(
        [
            helper_python(),
            str(REPO_ROOT / "helpers" / "pack_transcripts.py"),
            "--edit-dir",
            str(edit_dir),
        ],
        cwd=REPO_ROOT,
    )

    log(4, 5, "Generating timeline preview...")
    timeline_end = min(max(duration - 0.1, 0.1), 0.9 if duration > 0.9 else duration)
    timeline_png = verify_dir / f"{Path(source_name).stem}_timeline.png"
    run(
        [
            helper_python(),
            str(REPO_ROOT / "helpers" / "timeline_view.py"),
            str(source_path),
            "0",
            f"{timeline_end:.3f}",
            "--transcript",
            str(edit_dir / "transcripts" / f"{Path(source_name).stem}.json"),
            "-o",
            str(timeline_png),
        ],
        cwd=REPO_ROOT,
    )

    log(5, 5, "Rendering preview...")
    edl_path = write_edl(
        edit_dir,
        Path(source_name).stem,
        source_path,
        duration,
        metadata={
            "brand": hooks.brand if hooks.active else args.brand,
            "style": hooks.style if hooks.active else args.style,
            **content_metadata.to_dict(),
        },
    )
    if hooks.active:
        edl = json.loads(edl_path.read_text())
        edl["branding"] = {
            "brand": hooks.brand,
            "style": hooks.style,
            "watermark_path": str(hooks.watermark_path),
            "endcard_path": str(hooks.endcard_path),
            "subtitle_style": hooks.subtitle_style,
            "watermark_scale": watermark.scale,
            "watermark_opacity": watermark.opacity,
            "watermark_margin": watermark.margin,
        }
        if generated_script_path is not None:
            edl["generated_script_path"] = str(generated_script_path)
            edl.setdefault("metadata", {})["topic"] = args.topic
            edl.setdefault("metadata", {})["voice_chunks"] = content_metadata.script_stub.get("voice_chunks", [])
            edl.setdefault("metadata", {})["caption_groups"] = content_metadata.script_stub.get("caption_groups", [])
            edl.setdefault("metadata", {})["emphasis_words"] = content_metadata.script_stub.get("emphasis_words", [])
            edl.setdefault("metadata", {})["emphasis_pop_ms"] = content_metadata.script_stub.get("emphasis_pop_ms")
            edl.setdefault("metadata", {})["pause_profile"] = content_metadata.script_stub.get("pause_profile")
            edl.setdefault("metadata", {})["applied_pause_ms"] = content_metadata.script_stub.get("applied_pause_ms")
        edl_path.write_text(json.dumps(edl, indent=2))
    preview_path = edit_dir / "preview.mp4"
    run(
        [
            helper_python(),
            str(REPO_ROOT / "helpers" / "render.py"),
            str(edl_path),
            "-o",
            str(preview_path),
            "--preview",
            "--no-subtitles",
            "--no-loudnorm",
        ],
        cwd=REPO_ROOT,
    )

    branded_path = edit_dir / "preview_branded.mp4"
    branded_generated = False
    if hooks.active:
        branded_generated = build_branded_preview(preview_path, branded_path, hooks, watermark)
        if branded_generated:
            print(f"Branded preview path: {branded_path}", flush=True)
            if export_preset.name == "cinematic_916":
                branded_916_path = edit_dir / "preview_branded_916.mp4"
                vertical_generated = build_vertical_export(branded_path, branded_916_path, export_preset)
                if vertical_generated:
                    print(f"Branded 9:16 preview path: {branded_916_path}", flush=True)
                    captioned_916_path = edit_dir / "preview_branded_916_captioned.mp4"
                    transcript_path = edit_dir / "transcripts" / f"{Path(source_name).stem}.json"
                    captioned_generated = build_captioned_vertical_export(
                        branded_916_path,
                        transcript_path,
                        captioned_916_path,
                        caption_style,
                        export_preset,
                    )
                    if captioned_generated:
                        print(f"Captioned 9:16 preview path: {captioned_916_path}", flush=True)
                    if args.social_ready:
                        final_social_path = choose_final_social_output(
                            edit_dir,
                            captioned_916_path if captioned_generated else None,
                            branded_916_path,
                            branded_path,
                        )
                        if final_social_path is not None:
                            print_social_ready_banner(
                                final_social_path,
                                export_preset,
                                caption_style,
                                args.tts_provider,
                            )
                            if args.travelbuddy_reel:
                                print_travelbuddy_reel_banner(args.topic or "Untitled idea", final_social_path)
        else:
            print("Branding hooks were present but no branded export was generated", flush=True)
    else:
        print("Branding mode inactive; skipping branded export", flush=True)

    generated_files = gather_generated_files(workspace)
    print()
    print(f"Workspace: {workspace}")
    print(f"Output directory: {edit_dir}")
    print(f"Preview video path: {preview_path}")
    if branded_generated:
        print(f"Branded preview video path: {branded_path}")
    if args.social_ready:
        final_social_path = edit_dir / "final_social.mp4"
        if final_social_path.exists():
            print(f"Final social video path: {final_social_path}")
    if generated_script_path is not None:
        print(f"Generated script path: {generated_script_path}")
    print(f"Branding mode: {'active' if hooks.active else 'inactive'}")
    print("Generated files:")
    for path in generated_files:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
