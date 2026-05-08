"""Transcribe a video with a selectable TTS provider.

Extracts mono 16kHz audio via ffmpeg, uploads to Scribe with verbatim +
diarize + audio events + word-level timestamps, writes the full response
to <edit_dir>/transcripts/<video_stem>.json.

If ELEVENLABS_API_KEY is missing or set to a local placeholder value, writes
a minimal placeholder transcript and a reusable silent WAV without calling
ElevenLabs. The provider-specific behavior now lives behind
helpers/tts_providers/ so the current placeholder default stays intact while
future local engines can be added with minimal pipeline churn.

Cached: if the output file already exists, the upload is skipped.

Usage:
    python helpers/transcribe.py <video_path>
    python helpers/transcribe.py <video_path> --edit-dir /custom/edit
    python helpers/transcribe.py <video_path> --language en
    python helpers/transcribe.py <video_path> --num-speakers 2
    python helpers/transcribe.py <video_path> --tts-provider elevenlabs
    python helpers/transcribe.py <video_path> --tts-provider piper --piper-voice en_US-lessac-low
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
import wave
import tempfile
import time
from pathlib import Path

import requests


SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
PLACEHOLDER_KEYS = {"", "placeholder", "dummy", "test"}
PLACEHOLDER_WARNING = "Using placeholder audio because ELEVENLABS_API_KEY is not configured."
TTS_PROVIDER_PLACEHOLDER = "placeholder"
TTS_PROVIDER_ELEVENLABS = "elevenlabs"
TTS_PROVIDER_PIPER = "piper"
TTS_PROVIDER_MODULES = {
    TTS_PROVIDER_PLACEHOLDER: "placeholder",
    TTS_PROVIDER_ELEVENLABS: "elevenlabs",
    TTS_PROVIDER_PIPER: "piper",
}


def load_api_key() -> str:
    for candidate in [Path(__file__).resolve().parent.parent / ".env", Path(".env")]:
        if candidate.exists():
            for line in candidate.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "ELEVENLABS_API_KEY":
                    return v.strip().strip('"').strip("'")
    return os.environ.get("ELEVENLABS_API_KEY", "").strip().strip('"').strip("'")


def is_placeholder_key(api_key: str) -> bool:
    return api_key.strip().lower() in PLACEHOLDER_KEYS


def resolve_tts_provider(requested_provider: str, api_key: str) -> tuple[str, bool]:
    provider = requested_provider.strip().lower() or TTS_PROVIDER_PLACEHOLDER
    if provider == TTS_PROVIDER_PLACEHOLDER:
        if is_placeholder_key(api_key):
            print(PLACEHOLDER_WARNING, file=sys.stderr, flush=True)
        return provider, True
    if provider == TTS_PROVIDER_PIPER:
        return provider, False
    if provider == TTS_PROVIDER_ELEVENLABS and not is_placeholder_key(api_key):
        return provider, False
    print(PLACEHOLDER_WARNING, file=sys.stderr, flush=True)
    if provider == TTS_PROVIDER_ELEVENLABS:
        print(
            "Requested tts provider 'elevenlabs' but no real ELEVENLABS_API_KEY was found; "
            "using placeholder mode instead.",
            file=sys.stderr,
            flush=True,
        )
    return TTS_PROVIDER_PLACEHOLDER, True


def load_tts_provider_module(provider_name: str):
    module_name = TTS_PROVIDER_MODULES.get(provider_name)
    if module_name is None:
        raise ValueError(f"unsupported tts provider: {provider_name}")
    return importlib.import_module(f"tts_providers.{module_name}")


def get_video_duration(video: Path) -> float:
    try:
        out = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
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
    placeholder_reason: str = "ELEVENLABS_API_KEY is not configured",
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


def extract_audio(video_path: Path, dest: Path) -> None:
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def call_scribe(
    audio_path: Path,
    api_key: str,
    language: str | None = None,
    num_speakers: int | None = None,
) -> dict:
    data: dict[str, str] = {
        "model_id": "scribe_v1",
        "diarize": "true",
        "tag_audio_events": "true",
        "timestamps_granularity": "word",
    }
    if language:
        data["language_code"] = language
    if num_speakers:
        data["num_speakers"] = str(num_speakers)

    with open(audio_path, "rb") as f:
        resp = requests.post(
            SCRIBE_URL,
            headers={"xi-api-key": api_key},
            files={"file": (audio_path.name, f, "audio/wav")},
            data=data,
            timeout=1800,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"Scribe returned {resp.status_code}: {resp.text[:500]}")

    return resp.json()


def transcribe_one(
    video: Path,
    edit_dir: Path,
    api_key: str,
    tts_provider: str,
    language: str | None = None,
    num_speakers: int | None = None,
    piper_voice: str | None = None,
    piper_data_dir: Path | None = None,
    verbose: bool = True,
) -> Path:
    """Transcribe a single video. Returns path to transcript JSON.

    Cached: returns existing path immediately if the transcript already exists.
    """
    effective_provider, _use_placeholder = resolve_tts_provider(tts_provider, api_key)
    provider_module = load_tts_provider_module(effective_provider)
    return provider_module.transcribe(
        video=video,
        edit_dir=edit_dir,
        api_key=api_key,
        language=language,
        num_speakers=num_speakers,
        piper_voice=piper_voice,
        piper_data_dir=piper_data_dir,
        verbose=verbose,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Transcribe a video with ElevenLabs Scribe")
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
        choices=[TTS_PROVIDER_PLACEHOLDER, TTS_PROVIDER_ELEVENLABS, TTS_PROVIDER_PIPER],
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
    api_key = load_api_key()

    try:
        transcribe_one(
            video=video,
            edit_dir=edit_dir,
            api_key=api_key,
            tts_provider=args.tts_provider,
            language=args.language,
            num_speakers=args.num_speakers,
            piper_voice=args.piper_voice,
            piper_data_dir=args.piper_data_dir,
        )
    except Exception as exc:
        sys.exit(str(exc))


if __name__ == "__main__":
    main()
