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

Verified Piper path:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 -m piper.download_voices en_US-lessac-low --data-dir ./models/piper
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --tts-provider piper --piper-voice en_US-lessac-low --piper-data-dir ./models/piper
```

Optional input video:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --input /path/to/video.mp4 --brand TRAVELBUDDY --style cinematic
```

Social-ready shortcut:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --social-ready --tts-provider placeholder
```

With Piper:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --social-ready --tts-provider piper --piper-voice en_US-lessac-low --piper-data-dir ./models/piper
```

Topic-driven social-ready shortcut:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py --social-ready --tts-provider placeholder --topic "Stop applying. Start building."
```

Phase A metadata example:

```bash
.venv/bin/python3.11 travelbuddy_demo.py \
  --brand TRAVELBUDDY \
  --style cinematic \
  --export-preset cinematic_916 \
  --caption-style cinematic_gold \
  --content-type mentor_pitch
```

Verified vertical export behavior:

```bash
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --tts-provider placeholder --export-preset cinematic_916
```

This produces:

- `edit/preview.mp4`
- `edit/preview_branded.mp4`
- `edit/preview_branded_916.mp4`
- `edit/preview_branded_916_captioned.mp4` when `--caption-style cinematic_gold` is selected

`preview_branded_916.mp4` is a real 1080x1920 center-cropped export built from the branded preview. The stable 16:9 outputs remain unchanged.
`preview_branded_916_captioned.mp4` adds the first visible caption rendering pass on top of the vertical export. The current implementation renders caption plates in Python and composites them with ffmpeg overlays, so it stays available even when subtitle video filters are missing from the local ffmpeg build.

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
- `edit/piper_audio/<source>.wav` when Piper is selected and installed
- `edit/preview_branded.mp4` when TravelBuddy branding is active and assets are present
- `edit/preview_branded_916.mp4` when `--export-preset cinematic_916` is selected
- `edit/preview_branded_916_captioned.mp4` when `--export-preset cinematic_916` and `--caption-style cinematic_gold` are selected
- `edit/final_social.mp4` when `--social-ready` is selected
- `edit/generated_script.json` when `--topic` is selected
- `edit/edl.json` includes the selected export preset, caption style, and content-type metadata
- `edit/generated_script.json` also carries `voice_chunks`, `suggested_pause_ms`, and `caption_groups` for local pacing and subtitle grouping

The script also prints:

- output directory
- preview video path
- generated files

`final_social.mp4` is the convenience alias for the polished social-ready result. It copies the best available 9:16 social export, normally `preview_branded_916_captioned.mp4`.

When `--topic` is provided, the wrapper generates a deterministic topic script and saves it to `edit/generated_script.json`. The `voice_chunks` field drives chunked Piper narration, `caption_groups` drives the first caption grouping pass, and `voice_text` remains the fallback narration string.

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
- Add content-type routing for future AI script generation and caption presets.
- Add richer topic-to-script templates or a real AI-backed generator later, behind the same `generated_script.json` contract.
- Add better narration chunk timing and caption emphasis once the static rhythm pass is approved.
- Expand caption styles into animated subtitle treatments after the static overlay pass is validated.
- Add an export mode that copies the preview into a named shareable folder.

## Notes

- The wrapper does not change the core render engine.
- It uses the same helper scripts that are already verified in this repo.
- The workflow still depends on `ffmpeg` and `ffprobe` being available on `PATH`.
- The system `ffprobe` binary is fine; it does not need to live inside the repo virtualenv.
- Generated models, audio, and video should not be committed.
