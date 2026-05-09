# Project Brief

## What the App Does

`video-use-ai` is an agent-driven video editing toolkit. It lets a coding agent edit raw footage by reading transcripts and targeted visual timeline snapshots instead of manually reviewing every frame.

The workflow is:

1. Transcribe source videos with a local TTS provider route, defaulting to placeholder mode and allowing Piper when explicitly selected. The provider adapters live under `helpers/tts_providers/`.
2. Pack word-level transcripts into a compact editorial view.
3. Have the agent choose cuts from transcript timestamps and silence gaps.
4. Render an edit with ffmpeg, color grading, audio fades, optional overlays, and optional burned-in subtitles.
5. Verify cut boundaries with generated timeline views before showing the output.

It is structured as a reusable skill/toolkit rather than a hosted web app.

## Main Tech Stack

- Python 3.10+
- ffmpeg and ffprobe for audio/video extraction, rendering, grading, overlay composition, and verification
- Python dependencies from `pyproject.toml`: `librosa`, `matplotlib`, `pillow`, `numpy`
- Optional animation tooling:
  - HyperFrames
  - Remotion
  - Manim
  - PIL plus ffmpeg image/video pipelines
- Optional `yt-dlp` for downloading online source videos

## How to Run Locally

Install dependencies from the repo root:

```bash
cd ~/Documents/video-use-ai
uv sync
```

If `uv` is unavailable:

```bash
pip install -e .
```

Install required video tools:

```bash
brew install ffmpeg
```

Optional, only if downloading source videos from URLs:

```bash
brew install yt-dlp
```

Daily usage is meant to happen from a footage folder, not from inside the repo:

```bash
cd /path/to/your/videos
codex
```

Then ask the agent to inventory the takes or edit them into a video. Outputs are expected under:

```text
<videos_dir>/edit/
```

Useful helper commands:

```bash
python ~/Documents/video-use-ai/helpers/transcribe_batch.py /path/to/videos
python ~/Documents/video-use-ai/helpers/pack_transcripts.py --edit-dir /path/to/videos/edit
python ~/Documents/video-use-ai/helpers/timeline_view.py /path/to/video.mp4 0 10
python ~/Documents/video-use-ai/helpers/render.py /path/to/videos/edit/edl.json -o /path/to/videos/edit/final.mp4
```

## Important Folders and Files

- `README.md` - product overview, installation notes, and high-level workflow.
- `install.md` - first-time setup instructions for agents, ffmpeg, dependencies, and local-only provider setup.
- `SKILL.md` - core editing rules, production workflow, helper descriptions, EDL format, subtitle rules, grading guidance, and animation guidance.
- `helpers/` - executable Python helper scripts:
  - `transcribe.py` - provider router for placeholder or Piper transcription.
  - `tts_providers/` - provider adapters for placeholder and Piper.
  - `transcribe_batch.py` - transcribes a folder of videos in parallel.
  - `pack_transcripts.py` - turns raw transcript JSON into compact markdown.
  - `timeline_view.py` - creates filmstrip, waveform, word-label, and silence-gap PNG views.
  - `render.py` - renders an EDL to preview or final video.
  - `grade.py` - applies or analyzes ffmpeg color grades.
  - `timeline_view.py` and `grade.py` are key inspection/customization helpers.
- `skills/manim-video/` - vendored Manim animation skill and references for technical or diagrammatic animations.
- `static/` - repo images used by the README and documentation.
- `pyproject.toml` - Python package metadata and dependency list.

## Required Env Variables

None for the local provider workflow.

The transcription helper accepts:

```bash
--tts-provider placeholder
--tts-provider piper
--piper-voice en_US-lessac-low
--piper-data-dir /path/to/piper_data
--pause-profile tight|natural|dramatic
--pause-ms 220
```

`placeholder` is the default. `piper` is optional and only works when Piper is installed in the current Python environment.

Verified Piper install and model download commands:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 -m pip install piper-tts
.venv/bin/python3.11 -m piper.download_voices en_US-lessac-low --data-dir ./models/piper
```

Model location convention:

```text
./models/piper
```

The local-first architecture keeps provider selection inside `helpers/transcribe.py` and provider behavior inside `helpers/tts_providers/`, so future local engines can be added without changing the transcript contract.
TravelBuddy uses `--pause-profile natural` as the documented default for daily/social rhythm; use `tight` for fast news or quick-hit content and `dramatic` for motivational or emphasis reels.
The flagship daily command is `--travelbuddy-reel`, which layers the social-ready stack with Piper narration, `cinematic_916`, `cinematic_gold`, natural pacing, and mentor_pitch routing.
Deterministic creator modes add another light routing layer:

- `motivational`
- `breaking_news`
- `luxury`
- `airport_intel`
- `ai_marketing`
- `mentor_story`

Mode examples:

```bash
./travelbuddy reel "AI is replacing average marketing." --mode ai_marketing
./travelbuddy reel "Your next paycheck could come from an airport." --mode airport_intel
./travelbuddy reel "Stop applying. Start building." --mode motivational
./travelbuddy reel "Luxury travel feels calm." --mode luxury
./travelbuddy reel "Breaking: travel demand is shifting." --mode breaking_news
./travelbuddy reel "The best mentor stories sound simple." --mode mentor_story
```

For creator batching, `--topics-file` turns a plain text list into multiple reel runs and writes each result into `edit/batch/reel_###/`.
The batch runner also writes `edit/batch/batch_manifest.json` and `edit/batch/batch_manifest.md` so the run can be reviewed after the fact.
`examples/topics_daily.txt` is the recommended 10-topic starter list for daily batching.
Creator-facing copies are also exported to `outputs/single/` for single reels and `outputs/batch/` for batch reels so the polished deliverables are easy to find after the run.
The repo also includes a thin `./travelbuddy` wrapper for creator use: `./travelbuddy reel "<topic>"` and `./travelbuddy batch examples/topics_daily.txt`.
It adds the TravelBuddy reel preset and `--open-output` automatically, while still forwarding extra args for manual overrides.

The code looks for provider assets in the repo and in the edit workspace. Do not commit generated audio or temporary model downloads.
The workflow assumes `ffmpeg` and `ffprobe` are available on `PATH`; the system `ffprobe` binary is fine.

Phase A metadata modules:

- `helpers/export_presets.py` for social export aspect ratios, safe zones, and output suffix metadata
- `helpers/caption_styles.py` for subtitle style metadata and future caption treatment hints
- `helpers/script_engine.py` for deterministic topic-to-script generation, script-style routing, and future script-generation hooks

Verified vertical export behavior:

- `cinematic_916` now produces `edit/preview_branded_916.mp4`
- the vertical export is 1080x1920 and is built from the branded preview with a safe center-crop
- the stable 16:9 `preview.mp4` and `preview_branded.mp4` outputs remain unchanged

Verified caption rendering behavior:

- `cinematic_gold` now produces `edit/preview_branded_916_captioned.mp4`
- captions are rendered as lightweight Python-generated overlay plates and composited with ffmpeg
- topic-driven scripts can now provide `script_style`, `voice_chunks`, `suggested_pause_ms`, and `caption_groups` for cleaner rhythm
- topic-driven scripts also provide `emphasis_words`, and `cinematic_gold` highlights those words with brighter gold and slightly larger type
- the same `cinematic_gold` path now adds a subtle timed pop window around emphasized words instead of using a heavy animation engine
- topic-driven scripts also carry an `emphasis_pop_ms` hint so the pop window stays deterministic and lightweight
- pause timing can be tuned with `pause_profile` and `applied_pause_ms` for more natural narration gaps
- if transcript JSON is missing or incomplete, the pipeline copies the vertical export forward instead of failing
- `--social-ready` produces `edit/final_social.mp4` as a convenience alias for the polished vertical output
- `outputs/single/` stores timestamped single-reel deliverables and script JSON copies
- `outputs/batch/` stores timestamped batch reel deliverables plus batch manifests
- `--open-output` opens the matching creator export folder in Finder on macOS, or prints the path if Finder is unavailable
- `--travelbuddy-reel` is the recommended daily creator shortcut and still preserves manual overrides
- `./travelbuddy` is the fastest creator-facing entrypoint for single reels and batch runs
- `--topics-file` batches multiple reels from a plain text topic list
- `edit/batch/batch_manifest.json` and `edit/batch/batch_manifest.md` summarize batch runs with probe metadata and per-reel status
- `examples/topics_daily.txt` is the starter file for daily batch sessions
- `--topic` produces `edit/generated_script.json` and can feed chunked Piper narration plus caption grouping

## Placeholder Audio Mode

For local setup or demos without a real provider, transcription falls back to placeholder mode when `--tts-provider placeholder` is selected.

In placeholder mode, the helper does not synthesize speech. It writes a reusable local silent WAV under `<videos_dir>/edit/placeholder_audio/` and creates a minimal placeholder transcript JSON so downstream packing and editing steps can continue. The helper logs the saved placeholder transcript path and placeholder audio path.

## Best Next Customization Path for TravelBuddy Branding

Start by customizing the agent-facing editing guidance before changing rendering code.

Recommended order:

1. Add a TravelBuddy brand section to `SKILL.md` or a separate companion brief that defines tone, pacing, visual style, color palette, subtitle style, and common video formats.
2. Create a TravelBuddy sample EDL and brand preset documentation for common outputs such as trip recap, destination teaser, itinerary walkthrough, and testimonial.
3. Add a TravelBuddy-specific color grade preset in `helpers/grade.py` only after reviewing real TravelBuddy footage, because color grading depends heavily on source cameras, lighting, and destinations.
4. Add TravelBuddy subtitle and overlay defaults in `helpers/render.py` after the brand direction is confirmed.
5. Add reusable TravelBuddy animation templates under a new brand-specific folder only if repeated overlays are needed.

The safest first step is documentation and prompt-level branding. That gives the agent consistent editorial direction without risking regressions in the ffmpeg render pipeline.

## Local-First Architecture Note

The repo now assumes local-first transcription. Placeholder is the default, Piper is the optional real local provider, and the rest of the pipeline continues to work from the same transcript JSON contract.

Generated models, audio, and video should not be committed.

Future content pipeline notes:

- export presets and caption styles are metadata only for now
- `travelbuddy_demo.py` writes the selected preset/style/content metadata into `edit/edl.json`
- script generation now has a deterministic local topic-to-script path in `edit/generated_script.json`
- Piper can narrate the generated `voice_chunks` when `--topic` is provided, with `voice_text` as fallback
- Piper can insert configurable silence between chunked narration beats
- caption rendering prefers `caption_groups` when they are available in the transcript JSON
- `script_style` captures whether the writing should feel punchy, cinematic, urgent, luxury, or mentor-led
- `pause_profile` defaults to `natural`; `tight` is for fast news or quick-hit content and `dramatic` is for motivational or emphasis reels
- `emphasis_words` lets `cinematic_gold` brighten important words without changing the caption engine
- `emphasis_pop_ms` gives the caption renderer a small deterministic pop duration for those emphasized words
- the emphasis timing stays lightweight: no GPU, no new service, no full animation stack
- the first real preset behavior should stay additive and isolated to `cinematic_916`
- the first caption behavior should stay additive and isolated to `cinematic_gold`
- the social-ready wrapper should remain additive and should not replace the manual preset path
