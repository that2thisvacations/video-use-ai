"""Placeholder TTS provider.

This keeps the local smoke-test path intact and preserves the transcript JSON
contract used by the rest of the pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

from transcribe import build_placeholder_payload


def transcribe(
    video: Path,
    edit_dir: Path,
    language: str | None = None,
    num_speakers: int | None = None,
    piper_voice: str | None = None,
    piper_data_dir: Path | None = None,
    narration_text: str | None = None,
    narration_chunks: list[str] | None = None,
    verbose: bool = True,
) -> Path:
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"

    if out_path.exists():
        if verbose:
            print(f"cached: {out_path.name}")
        return out_path

    payload = build_placeholder_payload(video, edit_dir)
    out_path.write_text(json.dumps(payload, indent=2))
    if verbose:
        print(f"  saved placeholder transcript: {out_path.name}")
        print(f"    placeholder audio: {payload['placeholder_audio']}")
    return out_path
