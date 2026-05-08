"""Piper provider stub.

Expected future inputs:
- video: source clip Path
- edit_dir: output workspace Path
- api_key: retained for interface compatibility, likely unused
- language: optional language hint
- num_speakers: optional diarization hint
- verbose: logging toggle

Expected future outputs:
- transcript JSON written to <edit_dir>/transcripts/<video_stem>.json
- a provider-generated local audio file reused by downstream steps

This stub is intentionally dependency-free until Piper is installed and wired.
"""

from __future__ import annotations

from pathlib import Path


def transcribe(
    video: Path,
    edit_dir: Path,
    api_key: str,
    language: str | None = None,
    num_speakers: int | None = None,
    verbose: bool = True,
) -> Path:
    raise NotImplementedError(
        "Piper provider is not wired yet. Install Piper and implement "
        "helpers/tts_providers/piper.py before selecting --tts-provider piper."
    )

