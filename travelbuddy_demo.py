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
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
HELPER_PYTHON = REPO_ROOT / ".venv" / "bin" / "python3.11"
DEFAULT_BRAND = "TRAVELBUDDY"
DEFAULT_STYLE = "cinematic"


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


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the TravelBuddy placeholder demo workflow")
    ap.add_argument("--input", type=Path, default=None, help="Optional input video path")
    ap.add_argument("--brand", type=str, default=DEFAULT_BRAND, help="Brand label placeholder")
    ap.add_argument("--style", type=str, default=DEFAULT_STYLE, help="Render style placeholder")
    args = ap.parse_args()

    require_tools(["ffmpeg", "ffprobe"])

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

    generated_files = gather_generated_files(workspace)
    print()
    print(f"Workspace: {workspace}")
    print(f"Output directory: {edit_dir}")
    print(f"Preview video path: {preview_path}")
    print("Generated files:")
    for path in generated_files:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
