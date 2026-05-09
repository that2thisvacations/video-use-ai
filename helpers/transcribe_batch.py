"""Batch-transcribe every video in a directory with parallel workers.

Walks <videos_dir> for common video extensions, runs the selected local TTS
provider on each, and writes transcripts to
<videos_dir>/edit/transcripts/<name>.json.

Cached per-file: any source that already has a transcript is skipped.

Usage:
    python helpers/transcribe_batch.py <videos_dir>
    python helpers/transcribe_batch.py <videos_dir> --workers 4
    python helpers/transcribe_batch.py <videos_dir> --num-speakers 2
    python helpers/transcribe_batch.py <videos_dir> --edit-dir /custom/edit
    python helpers/transcribe_batch.py <videos_dir> --tts-provider piper --piper-voice en_US-lessac-low
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from transcribe import transcribe_one


VIDEO_EXTS = {".mp4", ".MP4", ".mov", ".MOV", ".mkv", ".MKV", ".avi", ".AVI", ".m4v"}


def find_videos(videos_dir: Path) -> list[Path]:
    videos = sorted(
        p for p in videos_dir.iterdir()
        if p.is_file() and p.suffix in VIDEO_EXTS
    )
    return videos


def main() -> None:
    ap = argparse.ArgumentParser(description="Parallel batch transcription of a videos directory")
    ap.add_argument("videos_dir", type=Path, help="Directory containing source videos")
    ap.add_argument(
        "--edit-dir",
        type=Path,
        default=None,
        help="Edit output directory (default: <videos_dir>/edit)",
    )
    ap.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    ap.add_argument(
        "--language",
        type=str,
        default=None,
        help="Optional ISO language code. Omit to auto-detect per file.",
    )
    ap.add_argument(
        "--num-speakers",
        type=int,
        default=None,
        help="Optional number of speakers. Improves diarization when known.",
    )
    ap.add_argument(
        "--tts-provider",
        type=str,
        default="placeholder",
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
        help="Piper data directory (default: <edit-dir>/piper_data)",
    )
    ap.add_argument(
        "--narration-text",
        type=str,
        default=None,
        help="Optional narration text override used by Piper",
    )
    ap.add_argument(
        "--narration-chunk",
        action="append",
        default=None,
        help="Optional narration chunk override used by Piper (repeatable)",
    )
    ap.add_argument(
        "--pause-profile",
        type=str,
        default="natural",
        choices=["tight", "natural", "dramatic"],
        help="Pause profile used by Piper chunk narration (default: natural)",
    )
    ap.add_argument(
        "--pause-ms",
        type=int,
        default=None,
        help="Override pause length between Piper narration chunks in milliseconds",
    )
    args = ap.parse_args()

    videos_dir = args.videos_dir.resolve()
    if not videos_dir.is_dir():
        sys.exit(f"not a directory: {videos_dir}")

    edit_dir = (args.edit_dir or (videos_dir / "edit")).resolve()
    (edit_dir / "transcripts").mkdir(parents=True, exist_ok=True)

    videos = find_videos(videos_dir)
    if not videos:
        sys.exit(f"no videos found in {videos_dir}")

    already_cached = [v for v in videos if (edit_dir / "transcripts" / f"{v.stem}.json").exists()]
    pending = [v for v in videos if v not in already_cached]

    print(f"found {len(videos)} videos ({len(already_cached)} cached, {len(pending)} to transcribe)")
    if not pending:
        print("nothing to do")
        return

    print(f"transcribing {len(pending)} files with {args.workers} parallel workers")
    t0 = time.time()

    errors: list[tuple[Path, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                transcribe_one,
                video=v,
                edit_dir=edit_dir,
                tts_provider=args.tts_provider,
                language=args.language,
                num_speakers=args.num_speakers,
                piper_voice=args.piper_voice,
                piper_data_dir=args.piper_data_dir,
                narration_text=args.narration_text,
                narration_chunks=args.narration_chunk,
                pause_profile=args.pause_profile,
                pause_ms=args.pause_ms,
                verbose=False,
            ): v
            for v in pending
        }
        for fut in as_completed(futures):
            v = futures[fut]
            try:
                out = fut.result()
                print(f"  + {v.stem}  →  {out.name}")
            except Exception as e:
                errors.append((v, str(e)))
                print(f"  x {v.stem}  FAILED: {e}")

    dt = time.time() - t0
    print(f"\ndone in {dt:.1f}s")
    if errors:
        print(f"{len(errors)} failures:")
        for v, msg in errors:
            print(f"  {v.name}: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
