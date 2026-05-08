"""Piper provider stub.

Expected input:
- video: source clip Path
- edit_dir: output workspace Path
- api_key: retained for interface compatibility, likely unused
- language: optional language hint
- num_speakers: optional diarization hint
- verbose: logging toggle

Expected output:
- transcript JSON written to <edit_dir>/transcripts/<video_stem>.json
- a provider-generated local audio file reused by downstream steps

Future implementation outline:
1. load a Piper model and voice config from a local model directory
2. synthesize narration audio for the current clip or script segment
3. write the provider audio to the edit workspace
4. emit the same transcript JSON contract the rest of the pipeline expects

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
