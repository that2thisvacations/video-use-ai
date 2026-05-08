#!/usr/bin/env python3
"""One-command TravelBuddy demo workflow.

This is orchestration only. It reuses the existing helper scripts and does not
change the core editing engine.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
HELPER_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3.11"
DEFAULT_BRAND = "TRAVELBUDDY"
DEFAULT_STYLE = "cinematic"
BRANDING_ROOT = REPO_ROOT / "branding"
BRANDING_ASSETS = BRANDING_ROOT / "assets"


@dataclass(frozen=True)
class BrandingHooks:
    active: bool
    brand: str
    style: str
    watermark_path: Path | None
    endcard_path: Path | None
    subtitle_style: str


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


def write_edl(edit_dir: Path, source_name: str, source_path: Path, duration: float) -> Path:
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
        watermark_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(preview_path),
            "-i",
            str(hooks.watermark_path),
            "-filter_complex",
            (
                "[1:v]scale=iw*0.22:-1[wm];"
                "[0:v][wm]overlay=W-w-32:H-h-32:format=auto[outv]"
            ),
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


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the TravelBuddy placeholder demo workflow")
    ap.add_argument("--input", type=Path, default=None, help="Optional input video path")
    ap.add_argument("--brand", type=str, default=DEFAULT_BRAND, help="Brand label placeholder")
    ap.add_argument("--style", type=str, default=DEFAULT_STYLE, help="Render style placeholder")
    args = ap.parse_args()

    require_tools(["ffmpeg", "ffprobe"])
    hooks = resolve_branding_hooks(args.brand, args.style)

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
    else:
        print("Branding mode inactive; using default placeholders", flush=True)
    run(
        [
            helper_python(),
            str(REPO_ROOT / "helpers" / "transcribe_batch.py"),
            str(workspace),
            "--workers",
            "1",
        ],
        cwd=REPO_ROOT,
    )

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
    edl_path = write_edl(edit_dir, Path(source_name).stem, source_path, duration)
    if hooks.active:
        edl = json.loads(edl_path.read_text())
        edl["branding"] = {
            "brand": hooks.brand,
            "style": hooks.style,
            "watermark_path": str(hooks.watermark_path),
            "endcard_path": str(hooks.endcard_path),
            "subtitle_style": hooks.subtitle_style,
        }
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
        branded_generated = build_branded_preview(preview_path, branded_path, hooks)
        if branded_generated:
            print(f"Branded preview path: {branded_path}", flush=True)
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
    print(f"Branding mode: {'active' if hooks.active else 'inactive'}")
    print("Generated files:")
    for path in generated_files:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
