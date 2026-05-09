"""Optional Piper provider adapter.

Expected input:
- video: source clip Path
- edit_dir: output workspace Path
- language: optional language hint, currently unused
- num_speakers: optional diarization hint, currently unused
- piper_voice: Piper model name such as ``en_US-lessac-low``
- piper_data_dir: directory where Piper voices are stored or downloaded
- narration_text: optional text to synthesize, when supplied
- pause_profile: profile name controlling chunk gap feel when chunked narration exists
- pause_ms: explicit chunk gap override in milliseconds
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
6. when chunked narration is available, synthesize each chunk and insert silence
   between chunks using the selected pause profile

If Piper is not installed in the current Python environment, this module raises
a clear error with install guidance instead of changing the default provider.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import wave
from tempfile import TemporaryDirectory
from pathlib import Path

from transcribe import build_placeholder_payload


PIPER_DEFAULT_VOICE = "en_US-lessac-low"
PIPER_DEFAULT_PAUSE_PROFILE = "natural"
PIPER_PAUSE_PROFILE_MS = {
    "tight": 120,
    "natural": 220,
    "dramatic": 380,
}
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


def resolve_pause_profile(pause_profile: str | None) -> str:
    profile = (pause_profile or PIPER_DEFAULT_PAUSE_PROFILE).strip().lower()
    return profile if profile in PIPER_PAUSE_PROFILE_MS else PIPER_DEFAULT_PAUSE_PROFILE


def resolve_pause_ms(pause_profile: str | None, pause_ms: int | None) -> int:
    if pause_ms is not None and pause_ms >= 0:
        return int(pause_ms)
    profile = resolve_pause_profile(pause_profile)
    return int(PIPER_PAUSE_PROFILE_MS.get(profile, PIPER_PAUSE_PROFILE_MS[PIPER_DEFAULT_PAUSE_PROFILE]))


def join_narration_chunks(chunks: list[str], pause_profile: str | None = None) -> str:
    normalized = [chunk.strip().rstrip(".!?") for chunk in chunks if chunk and chunk.strip()]
    if not normalized:
        return ""
    profile = resolve_pause_profile(pause_profile)
    separator = {
        "tight": ". ",
        "natural": ". ",
        "dramatic": "... ",
    }.get(profile, ". ")
    return separator.join(normalized).strip()


def chunk_silence_frames(sample_rate: int, channels: int, sample_width: int, pause_ms: int) -> bytes:
    if pause_ms <= 0:
        return b""
    frames = int(round(sample_rate * (pause_ms / 1000.0)))
    if frames <= 0:
        return b""
    return b"\x00" * frames * channels * sample_width


def combine_wavs_with_pauses(chunk_paths: list[Path], out_wav: Path, pause_ms: int) -> None:
    if not chunk_paths:
        raise RuntimeError("no chunk audio generated")

    with wave.open(str(chunk_paths[0]), "rb") as first:
        params = first.getparams()
        sample_rate = first.getframerate()
        channels = first.getnchannels()
        sample_width = first.getsampwidth()
        frames_by_chunk = [first.readframes(first.getnframes())]

    for path in chunk_paths[1:]:
        with wave.open(str(path), "rb") as wav:
            if (
                wav.getnchannels() != params.nchannels
                or wav.getsampwidth() != params.sampwidth
                or wav.getframerate() != params.framerate
                or wav.getcomptype() != params.comptype
            ):
                raise RuntimeError("Piper chunk audio parameters do not match")
            frames_by_chunk.append(wav.readframes(wav.getnframes()))

    silence = chunk_silence_frames(sample_rate, channels, sample_width, pause_ms)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as out:
        out.setparams(params)
        for index, frames in enumerate(frames_by_chunk):
            out.writeframes(frames)
            if index != len(frames_by_chunk) - 1 and silence:
                out.writeframes(silence)


def synthesize_chunked_wav(
    voice: str,
    data_dir: Path,
    out_wav: Path,
    chunks: list[str],
    pause_profile: str | None = None,
    pause_ms: int | None = None,
) -> tuple[int, int]:
    profile = resolve_pause_profile(pause_profile)
    pause_gap_ms = resolve_pause_ms(profile, pause_ms)
    with TemporaryDirectory(prefix="piper_chunks_") as temp_dir:
        temp_root = Path(temp_dir)
        chunk_paths: list[Path] = []
        for idx, chunk in enumerate(chunks):
            chunk_path = temp_root / f"chunk_{idx:02d}.wav"
            synthesize_wav(voice, data_dir, chunk_path, chunk)
            chunk_paths.append(chunk_path)
        combine_wavs_with_pauses(chunk_paths, out_wav, pause_gap_ms)
    return len(chunks), pause_gap_ms


def transcribe(
    video: Path,
    edit_dir: Path,
    language: str | None = None,
    num_speakers: int | None = None,
    piper_voice: str | None = None,
    piper_data_dir: Path | None = None,
    narration_text: str | None = None,
    narration_chunks: list[str] | None = None,
    pause_profile: str | None = None,
    pause_ms: int | None = None,
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
    chunk_text = join_narration_chunks(narration_chunks or [], pause_profile=pause_profile)
    script_text = chunk_text or (narration_text or "placeholder transcript").strip() or "placeholder transcript"
    applied_pause_ms = resolve_pause_ms(pause_profile, pause_ms)
    pause_profile_name = resolve_pause_profile(pause_profile)

    if verbose:
        print(f"  using Piper voice: {voice}", flush=True)
        print(f"  Piper data dir: {data_dir}", flush=True)
        print(f"  Piper audio path: {audio_path}", flush=True)
        print(f"  Piper narration length: {len(script_text)} chars", flush=True)
        print(f"  Piper pause profile: {pause_profile_name} ({applied_pause_ms} ms)", flush=True)
        if chunk_text:
            print(f"  Piper narration chunks: {len(narration_chunks or [])}", flush=True)

    download_voice(voice, data_dir)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        if narration_chunks:
            chunk_count, pause_gap_ms = synthesize_chunked_wav(
                voice,
                data_dir,
                audio_path,
                [str(chunk).strip() for chunk in narration_chunks if str(chunk).strip()],
                pause_profile=pause_profile_name,
                pause_ms=pause_ms,
            )
            applied_pause_ms = pause_gap_ms
            if verbose:
                print(
                    f"  Piper chunked audio: {chunk_count} chunks with {applied_pause_ms} ms pauses",
                    flush=True,
                )
        else:
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
