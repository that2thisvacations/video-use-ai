# Demo Workflow

`travelbuddy_demo.py` is a thin orchestration wrapper around the existing verified local workflow.

## Exact Command

Run from the repo root:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic
```

Explicit provider selection:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --tts-provider placeholder
```

Optional Piper path:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --tts-provider piper --piper-voice en_US-lessac-low --piper-data-dir ~/Library/Application\ Support/video-use-ai/piper
```

Optional input video:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --input /path/to/video.mp4 --brand TRAVELBUDDY --style cinematic
```

Watermark tuning example:

```bash
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --watermark-opacity 0.95
```

## What It Does

The script runs the existing workflow in order:

1. Creates a temporary workspace.
2. Uses the provided input video, or generates a tiny demo MP4 with `ffmpeg`.
3. Runs the selected transcription provider. Placeholder remains the default, and Piper can be selected explicitly when installed.
4. Packs transcripts into `takes_packed.md`.
5. Generates a timeline preview PNG.
6. Builds an EDL and renders a preview MP4.

It prints progress logs like:

```text
[1/5] Generating demo video...
[2/5] Running transcript pipeline...
[3/5] Packing transcripts...
[4/5] Generating timeline preview...
[5/5] Rendering preview...
```

## Placeholder Mode

This workflow is designed to run with the placeholder provider.

Accepted values:

```text
placeholder
```

The demo wrapper forwards `--tts-provider`, `--piper-voice`, and `--piper-data-dir` into the transcription helper.

## Expected Outputs

The script prints the workspace path at the end. The output directory is the workspace `edit/` folder.

Expected files:

- `edit/transcripts/<source>.json`
- `edit/takes_packed.md`
- `edit/verify/<source>_timeline.png`
- `edit/edl.json`
- `edit/clips_preview/seg_00_<source>.mp4`
- `edit/base_preview.mp4`
- `edit/preview.mp4`
- `edit/placeholder_audio/placeholder.wav`
- `edit/preview_branded.mp4` when TravelBuddy branding is active and assets are present

The script also prints:

- output directory
- preview video path
- generated files

TravelBuddy branding can be tuned with:

- `--watermark-scale`
- `--watermark-opacity`
- `--watermark-margin`

## Future Extension Ideas

- Map `--brand` to a real TravelBuddy prompt pack.
- Map `--style` to concrete grading and subtitle presets.
- Add a real brand manifest file for TravelBuddy-specific defaults.
- Add a second command mode for ingesting a folder of source videos.
- Add a provider selector for additional local transcription backends.
- Add an export mode that copies the preview into a named shareable folder.

## Notes

- The wrapper does not change the core render engine.
- It uses the same helper scripts that are already verified in this repo.
- The workflow still depends on `ffmpeg` and `ffprobe` being available on `PATH`.

