# Project Brief

## What the App Does

`video-use-ai` is an agent-driven video editing toolkit. It lets a coding agent edit raw footage by reading transcripts and targeted visual timeline snapshots instead of manually reviewing every frame.

The workflow is:

1. Transcribe source videos with a selectable TTS provider route, defaulting to placeholder mode and using ElevenLabs Scribe only when explicitly selected.
2. Pack word-level transcripts into a compact editorial view.
3. Have the agent choose cuts from transcript timestamps and silence gaps.
4. Render an edit with ffmpeg, color grading, audio fades, optional overlays, and optional burned-in subtitles.
5. Verify cut boundaries with generated timeline views before showing the output.

It is structured as a reusable skill/toolkit rather than a hosted web app.

## Main Tech Stack

- Python 3.10+
- ffmpeg and ffprobe for audio/video extraction, rendering, grading, subtitles, and verification
- ElevenLabs Scribe API for word-level transcription and speaker diarization
- Python dependencies from `pyproject.toml`: `requests`, `librosa`, `matplotlib`, `pillow`, `numpy`
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

Create a local `.env` from the example and add the ElevenLabs API key:

```bash
cp .env.example .env
```

Then edit `.env` so it contains:

```bash
ELEVENLABS_API_KEY=your_key_here
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
- `install.md` - first-time setup instructions for agents, ffmpeg, dependencies, and API key setup.
- `SKILL.md` - core editing rules, production workflow, helper descriptions, EDL format, subtitle rules, grading guidance, and animation guidance.
- `helpers/` - executable Python helper scripts:
  - `transcribe.py` - transcribes one video with a provider flag for placeholder or ElevenLabs Scribe.
  - `transcribe_batch.py` - transcribes a folder of videos in parallel.
  - `pack_transcripts.py` - turns raw transcript JSON into compact markdown.
  - `timeline_view.py` - creates filmstrip, waveform, word-label, and silence-gap PNG views.
  - `render.py` - renders an EDL to preview or final video.
  - `grade.py` - applies or analyzes ffmpeg color grades.
  - `timeline_view.py` and `grade.py` are key inspection/customization helpers.
- `skills/manim-video/` - vendored Manim animation skill and references for technical or diagrammatic animations.
- `static/` - repo images used by the README and documentation.
- `.env.example` - documents the required environment variable name.
- `pyproject.toml` - Python package metadata and dependency list.

## Required Env Variables

Required for transcription:

```bash
ELEVENLABS_API_KEY=
```

The transcription helper also accepts:

```bash
--tts-provider placeholder
--tts-provider elevenlabs
```

`placeholder` is the default. `elevenlabs` only uses the live API when a real
`ELEVENLABS_API_KEY` is present; otherwise it falls back to placeholder mode
and prints a warning.

The TravelBuddy demo wrapper also forwards `--tts-provider` into the
transcription helper so the full demo workflow can be switched without changing
render logic.

The code looks for this key in either:

1. `.env` at the `video-use-ai` repo root
2. `.env` in the current working directory
3. The process environment

Do not commit `.env`. The repo currently includes only `.env.example`.

### Placeholder Audio Mode

For local setup or demos without a real ElevenLabs key, transcription falls back to placeholder mode when `ELEVENLABS_API_KEY` is missing or set to `placeholder`, `dummy`, or `test`.

In placeholder mode, the helper does not call ElevenLabs. It writes a reusable local silent WAV under `<videos_dir>/edit/placeholder_audio/` and creates a minimal placeholder transcript JSON so downstream packing and editing steps can continue. The console warning is:

```text
Using placeholder audio because ELEVENLABS_API_KEY is not configured.
```

Switch back to real transcription by setting `ELEVENLABS_API_KEY` to a valid ElevenLabs API key in `.env` or the process environment and deleting any cached placeholder transcript JSON files that should be regenerated.

## Best Next Customization Path for TravelBuddy Branding

Start by customizing the agent-facing editing guidance before changing rendering code.

Recommended order:

1. Add a TravelBuddy brand section to `SKILL.md` or a separate companion brief that defines tone, pacing, visual style, color palette, subtitle style, and common video formats.
2. Create a TravelBuddy sample EDL and brand preset documentation for common outputs such as trip recap, destination teaser, itinerary walkthrough, and testimonial.
3. Add a TravelBuddy-specific color grade preset in `helpers/grade.py` only after reviewing real TravelBuddy footage, because color grading depends heavily on source cameras, lighting, and destinations.
4. Add TravelBuddy subtitle and overlay defaults in `helpers/render.py` after the brand direction is confirmed.
5. Add reusable TravelBuddy animation templates under a new brand-specific folder only if repeated overlays are needed.

The safest first step is documentation and prompt-level branding. That gives the agent consistent editorial direction without risking regressions in the ffmpeg render pipeline.
