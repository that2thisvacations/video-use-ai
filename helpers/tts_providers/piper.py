"""Optional Piper provider adapter.

Expected input:
- video: source clip Path
- edit_dir: output workspace Path
- language: optional language hint, currently unused
- num_speakers: optional diarization hint, currently unused
- piper_voice: Piper model name such as ``en_US-lessac-low``
- piper_data_dir: directory where Piper voices are stored or downloaded
- narration_text: optional text to synthesize, when supplied
- verbose: logging toggle

Expected output:
- transcript JSON written to <edit_dir>/transcripts/<video_stem>.json
- a generated WAV under <edit_dir>/piper_audio/ reused by downstream steps

Future implementation outline:
1. keep the CLI flags and routing boundary stable
2. load or download the selected Piper voice into the configured data dir
3. synthesize a short WAV using the documented ``-- 'text'`` invocation
4. write the same transcript JSON contract used by placeholder mode for now
5. when a topic-generated narration string is provided, synthesize that text

If Piper is not installed in the current Python environment, this module raises
a clear error with install guidance instead of changing the default provider.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from transcribe import build_placeholder_payload


PIPER_DEFAULT_VOICE = "en_US-lessac-low"
PIPER_INSTALL_GUIDANCE = (
    "Piper is not installed in this environment. Install it with "
    "`python3.11 -m pip install piper-tts`, then download a voice with "
    "`python3.11 -m piper.download_voices en_US-lessac-low --data-dir <dir>`."
)


def is_piper_available() -> bool:
    return importlib.util.find_spec("piper") is not None


def ensure_piper_available() -> None:
    if not is_piper_available():
        raise RuntimeError(PIPER_INSTALL_GUIDANCE)


def run_checked(cmd: list[str], label: str) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        stderr = (result.stderr or result.stdout or "").strip()
        if stderr:
            raise RuntimeError(f"{label} failed: {stderr}")
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")


def download_voice(voice: str, data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    model_path = data_dir / f"{voice}.onnx"
    config_path = data_dir / f"{voice}.onnx.json"
    if model_path.exists() and config_path.exists():
        return
    run_checked(
        [sys.executable, "-m", "piper.download_voices", voice, "--data-dir", str(data_dir)],
        f"downloading Piper voice {voice}",
    )


def synthesize_wav(voice: str, data_dir: Path, out_wav: Path, text: str) -> None:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    run_checked(
        [
            sys.executable,
            "-m",
            "piper",
            "-m",
            voice,
            "-f",
            str(out_wav),
            "--data-dir",
            str(data_dir),
            "--",
            text,
        ],
        f"synthesizing Piper audio with {voice}",
    )


def transcribe(
    video: Path,
    edit_dir: Path,
    language: str | None = None,
    num_speakers: int | None = None,
    piper_voice: str | None = None,
    piper_data_dir: Path | None = None,
    narration_text: str | None = None,
    verbose: bool = True,
) -> Path:
    transcripts_dir = edit_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    out_path = transcripts_dir / f"{video.stem}.json"

    if out_path.exists():
        if verbose:
            print(f"cached: {out_path.name}")
        return out_path

    ensure_piper_available()

    voice = (piper_voice or PIPER_DEFAULT_VOICE).strip() or PIPER_DEFAULT_VOICE
    data_dir = (piper_data_dir or (edit_dir / "piper_data")).resolve()
    audio_path = (edit_dir / "piper_audio" / f"{video.stem}.wav").resolve()
    script_text = (narration_text or "placeholder transcript").strip() or "placeholder transcript"

    if verbose:
        print(f"  using Piper voice: {voice}", flush=True)
        print(f"  Piper data dir: {data_dir}", flush=True)
        print(f"  Piper audio path: {audio_path}", flush=True)
        print(f"  Piper narration length: {len(script_text)} chars", flush=True)

    download_voice(voice, data_dir)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        synthesize_wav(voice, data_dir, audio_path, script_text)

    payload = build_placeholder_payload(
        video,
        edit_dir,
        audio_path=audio_path,
        placeholder_reason=f"Piper generated placeholder transcript ({voice})",
        transcript_text=script_text,
    )
    out_path.write_text(json.dumps(payload, indent=2))

    if verbose:
        kb = out_path.stat().st_size / 1024
        print(f"  saved Piper transcript: {out_path.name} ({kb:.1f} KB)")
        print(f"    audio: {payload['placeholder_audio']}")

    return out_path
