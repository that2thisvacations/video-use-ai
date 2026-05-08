# Local Run Guide

This project is a local agent skill/toolkit, not a hosted web app. The normal run flow is:

1. Keep this repo in a stable path.
2. Put source videos in a separate footage folder.
3. Run helper scripts from this repo against that footage folder.
4. Let the agent read `takes_packed.md`, propose an edit strategy, then create and render an EDL.
5. Find all outputs in the footage folder's `edit/` directory.

## Repository Location

Run repo-level setup and helper commands from:

```bash
cd ~/Documents/video-use-ai
```

## Required Dependencies

Minimum Python for the verified local runtime:

```bash
python3.11 --version
```

On this machine, the working interpreter is the repo virtualenv:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 --version
```

Python package dependencies are listed in `pyproject.toml`:

```text
librosa
matplotlib
pillow
numpy
```

Install them from the repo root with Python 3.11.

Required video tools for real video processing:

```bash
ffmpeg -version
ffprobe -version
```

Optional dependency for downloading online videos:

```bash
brew install yt-dlp
```

Do not install optional animation dependencies unless a project actually needs them:

- HyperFrames
- Remotion
- Manim
- Node.js/npm for HyperFrames or Remotion slots
- LaTeX for Manim-heavy workflows

## Placeholder Workflow

The default provider is placeholder mode. It writes a local silent WAV plus a minimal placeholder transcript so the transcript/packing workflow can run without any external API.

Run from the repo root:

```bash
cd ~/Documents/video-use-ai
DEMO_DIR=$(mktemp -d)
ffmpeg -y \
  -f lavfi -i testsrc=size=320x180:rate=24:duration=2 \
  -f lavfi -i sine=frequency=440:duration=2:sample_rate=48000 \
  -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac \
  "$DEMO_DIR/sample.mp4"

.venv/bin/python3.11 helpers/transcribe_batch.py "$DEMO_DIR" --workers 1
.venv/bin/python3.11 helpers/pack_transcripts.py --edit-dir "$DEMO_DIR/edit"
.venv/bin/python3.11 helpers/timeline_view.py "$DEMO_DIR/sample.mp4" 0 0.9 --transcript "$DEMO_DIR/edit/transcripts/sample.json" -o "$DEMO_DIR/edit/verify/sample_0_0_9.png"

cat > "$DEMO_DIR/edit/edl.json" <<EOF
{
  "version": 1,
  "sources": {
    "sample": "$DEMO_DIR/sample.mp4"
  },
  "ranges": [
    {
      "source": "sample",
      "start": 0.0,
      "end": 1.0,
      "beat": "PLACEHOLDER",
      "quote": "placeholder",
      "reason": "Local placeholder runtime verification."
    }
  ],
  "grade": "none",
  "overlays": [],
  "total_duration_s": 1.0
}
EOF

.venv/bin/python3.11 helpers/render.py "$DEMO_DIR/edit/edl.json" -o "$DEMO_DIR/edit/preview.mp4" --preview --no-subtitles --no-loudnorm
find "$DEMO_DIR" -maxdepth 4 -type f | sort
sed -n '1,40p' "$DEMO_DIR/edit/takes_packed.md"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$DEMO_DIR/edit/preview.mp4"
```

Expected files:

```text
<demo_dir>/sample.mp4
<demo_dir>/edit/placeholder_audio/placeholder.wav
<demo_dir>/edit/transcripts/sample.json
<demo_dir>/edit/takes_packed.md
<demo_dir>/edit/verify/sample_0_0_9.png
<demo_dir>/edit/edl.json
<demo_dir>/edit/clips_preview/seg_00_sample.mp4
<demo_dir>/edit/base_preview.mp4
<demo_dir>/edit/preview.mp4
```

## Piper Workflow

Piper is optional. If installed in the repo environment, use it explicitly:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 helpers/transcribe_batch.py ~/Documents/video-use-demo --workers 1 --tts-provider piper --piper-voice en_US-lessac-low
```

If Piper is missing, the helper fails gracefully with install guidance and the placeholder provider remains the default.

## Processing a Real Sample Video

Use this with the Python 3.11 venv and `ffmpeg` / `ffprobe` installed.

Create a footage folder outside the repo:

```bash
mkdir -p ~/Documents/video-use-demo
```

Put a real `.mp4`, `.mov`, `.mkv`, `.avi`, or `.m4v` file in that folder. Then run:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 helpers/transcribe_batch.py ~/Documents/video-use-demo --workers 1
.venv/bin/python3.11 helpers/pack_transcripts.py --edit-dir ~/Documents/video-use-demo/edit
```

Inspect the packed transcript:

```bash
sed -n '1,120p' ~/Documents/video-use-demo/edit/takes_packed.md
```

Optional visual inspection for a real video:

```bash
.venv/bin/python3.11 ~/Documents/video-use-ai/helpers/timeline_view.py ~/Documents/video-use-demo/sample.mp4 0 10 -o ~/Documents/video-use-demo/edit/verify/sample_0_10.png
```

That command requires:

- `ffmpeg`
- Pillow (`pillow`)
- NumPy (`numpy`)

## Rendering Flow

Rendering requires a valid EDL at:

```text
<videos_dir>/edit/edl.json
```

EDL shape:

```json
{
  "version": 1,
  "sources": {
    "sample": "/absolute/path/to/sample.mp4"
  },
  "ranges": [
    {
      "source": "sample",
      "start": 0.0,
      "end": 10.0,
      "beat": "HOOK",
      "quote": "..." ,
      "reason": "..."
    }
  ],
  "grade": "none",
  "overlays": [],
  "total_duration_s": 10.0
}
```

Render:

```bash
.venv/bin/python3.11 helpers/render.py ~/Documents/video-use-demo/edit/edl.json -o ~/Documents/video-use-demo/edit/final.mp4
```

## Expected Output Folders

- `<videos_dir>/edit/transcripts/`
- `<videos_dir>/edit/takes_packed.md`
- `<videos_dir>/edit/edl.json`
- `<videos_dir>/edit/clips_preview/`
- `<videos_dir>/edit/preview.mp4`
- `<videos_dir>/edit/preview_branded.mp4` when TravelBuddy branding is active
- `<videos_dir>/edit/verify/`

## Known Blockers / Issues

- Missing `ffmpeg` or `ffprobe` blocks render and inspection.
- Missing Piper blocks the Piper provider only; placeholder remains available.
- `yt-dlp` is optional and only needed for URL downloads.

## Recommended Next Step

Start with placeholder mode, then add Piper only if the user explicitly wants local TTS instead of placeholder transcripts.

