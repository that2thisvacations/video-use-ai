"""Transcribe a video with a local TTS provider.

This helper keeps the transcript JSON contract unchanged while routing to a
provider module under `helpers/tts_providers/`.

Supported providers:
- placeholder: writes a reusable silent WAV plus a minimal transcript JSON
- piper: optionally synthesizes a local WAV when Piper is installed

Cached: if the output file already exists, the provider step is skipped.

Usage:
    python helpers/transcribe.py <video_path>
    python helpers/transcribe.py <video_path> --edit-dir /custom/edit
    python helpers/transcribe.py <video_path> --language en
    python helpers/transcribe.py <video_path> --num-speakers 2
    python helpers/transcribe.py <video_path> --tts-provider piper --piper-voice en_US-lessac-low
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path


TTS_PROVIDER_PLACEHOLDER = "placeholder"
TTS_PROVIDER_PIPER = "piper"
TTS_PROVIDER_MODULES = {
    TTS_PROVIDER_PLACEHOLDER: "placeholder",
    TTS_PROVIDER_PIPER: "piper",
}


def load_tts_provider_module(provider_name: str):
    module_name = TTS_PROVIDER_MODULES.get(provider_name)
    if module_name is None:
        raise ValueError(f"unsupported tts provider: {provider_name}")
    return importlib.import_module(f"tts_providers.{module_name}")


def get_video_duration(video: Path) -> float:
    try:
        out = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return max(0.0, float(out.stdout.strip()))
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return 1.0


def ensure_placeholder_audio(edit_dir: Path) -> Path:
    placeholder_dir = edit_dir / "placeholder_audio"
    placeholder_dir.mkdir(parents=True, exist_ok=True)
    audio_path = placeholder_dir / "placeholder.wav"
    if audio_path.exists():
        return audio_path

    sample_rate = 16000
    duration_seconds = 1
    with wave.open(str(audio_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * sample_rate * duration_seconds)
    return audio_path


def build_placeholder_payload(
    video: Path,
    edit_dir: Path,
    *,
    audio_path: Path | None = None,
    placeholder_reason: str = "placeholder mode active",
    transcript_text: str = "placeholder transcript",
) -> dict:
    if audio_path is None:
        audio_path = ensure_placeholder_audio(edit_dir)
    duration = max(0.1, get_video_duration(video))
    end = min(duration, 1.0)
    return {
        "text": transcript_text,
        "language_code": "en",
        "language_probability": 0.0,
        "placeholder": True,
        "placeholder_reason": placeholder_reason,
        "placeholder_audio": str(audio_path),
        "source_duration": duration,
        "words": [
            {
                "text": "placeholder",
                "type": "word",
                "start": 0.0,
                "end": end,
                "speaker_id": "speaker_0",
            }
        ],
    }


def transcribe_one(
    video: Path,
    edit_dir: Path,
    tts_provider: str,
    language: str | None = None,
    num_speakers: int | None = None,
    piper_voice: str | None = None,
    piper_data_dir: Path | None = None,
    verbose: bool = True,
) -> Path:
    """Transcribe a single video. Returns path to transcript JSON."""
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"

    if out_path.exists():
        if verbose:
            print(f"cached: {out_path.name}")
        return out_path

    provider = (tts_provider.strip().lower() or TTS_PROVIDER_PLACEHOLDER)
    provider_module = load_tts_provider_module(provider)
    return provider_module.transcribe(
        video=video,
        edit_dir=edit_dir,
        language=language,
        num_speakers=num_speakers,
        piper_voice=piper_voice,
        piper_data_dir=piper_data_dir,
        verbose=verbose,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video with a local TTS provider")
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument(
        "--edit-dir",
        type=Path,
        default=None,
        help="Edit output directory (default: <video_parent>/edit)",
    )
    ap.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional ISO language code (e.g., 'en'). Omit to auto-detect.",
    )
    ap.add_argument(
        "--num-speakers",
        type=int,
        default=None,
        help="Optional number of speakers when known. Improves diarization accuracy.",
    )
    ap.add_argument(
        "--tts-provider",
        type=str,
        default=TTS_PROVIDER_PLACEHOLDER,
        choices=[TTS_PROVIDER_PLACEHOLDER, TTS_PROVIDER_PIPER],
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
        help="Piper data directory (default: <edit-dir>/piper_data)",
    )
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")

    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()
    transcribe_one(
        video=video,
        edit_dir=edit_dir,
        tts_provider=args.tts_provider,
        language=args.language,
        num_speakers=args.num_speakers,
        piper_voice=args.piper_voice,
        piper_data_dir=args.piper_data_dir,
    )


if __name__ == "__main__":
    main()

