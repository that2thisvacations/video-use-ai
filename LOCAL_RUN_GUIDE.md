# Local Run Guide

This project is a local agent skill/toolkit, not a hosted web app. The normal run flow is:

1. Keep this repo in a stable path.
2. Put source videos in a separate footage folder.
3. Run helper scripts from this repo against that footage folder.
4. Let the agent read `takes_packed.md`, propose an edit strategy, then create and render an EDL.
5. Find all outputs in the footage folder's `edit/` directory.

The commands below use placeholder mode only:

```bash
ELEVENLABS_API_KEY=placeholder
```

Placeholder mode does not call ElevenLabs. It writes a local silent WAV plus a minimal placeholder transcript so the transcript/packing workflow can run without a real API key.

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
requests
librosa
matplotlib
pillow
numpy
```

Install them from the repo root with Python 3.11. This avoids `llvmlite` building from source under an incompatible Python:

```bash
cd ~/Documents/video-use-ai
python3.11 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

If `llvmlite` starts building from source, stop and install compatible pinned versions explicitly:

```bash
cd ~/Documents/video-use-ai
.venv/bin/pip install "numba==0.60.0" "llvmlite==0.43.0"
.venv/bin/pip install -e .
```

Verify the dependency fix:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 - <<'PY'
import numba, llvmlite
print("numba", numba.__version__)
print("llvmlite", llvmlite.__version__)
PY
```

Required video tools for real video processing:

```bash
brew install ffmpeg
```

This must put both of these on `PATH`:

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

## Environment Setup

For placeholder mode in the current shell:

```bash
export ELEVENLABS_API_KEY=placeholder
```

Alternatively, from the repo root:

```bash
cd ~/Documents/video-use-ai
cp .env.example .env
printf 'ELEVENLABS_API_KEY=placeholder\n' > .env
```

Accepted placeholder values are:

```text
placeholder
dummy
test
```

Missing `ELEVENLABS_API_KEY` also activates placeholder mode.

Expected warning:

```text
Using placeholder audio because ELEVENLABS_API_KEY is not configured.
```

## Verified Placeholder Demo

This demo verifies placeholder transcript generation, transcript packing, timeline PNG generation, EDL rendering, and preview output.

Run from the repo root:

```bash
cd ~/Documents/video-use-ai
DEMO_DIR=$(mktemp -d)
ffmpeg -y \
  -f lavfi -i testsrc=size=320x180:rate=24:duration=2 \
  -f lavfi -i sine=frequency=440:duration=2:sample_rate=48000 \
  -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac \
  "$DEMO_DIR/sample.mp4"

ELEVENLABS_API_KEY=placeholder .venv/bin/python3.11 helpers/transcribe_batch.py "$DEMO_DIR" --workers 1
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

Expected packed transcript content:

```text
## sample  (duration: 1.0s, 1 phrases)
  [000.00-001.00] S0 placeholder
```

## Processing a Real Sample Video

Use this with the Python 3.11 venv and `ffmpeg` / `ffprobe` installed.

Create a footage folder outside the repo:

```bash
mkdir -p ~/Documents/video-use-demo
```

Put a real `.mp4`, `.mov`, `.mkv`, `.avi`, or `.m4v` file in that folder. Then run:

```bash
cd ~/Documents/video-use-ai
ELEVENLABS_API_KEY=placeholder .venv/bin/python3.11 helpers/transcribe_batch.py ~/Documents/video-use-demo --workers 1
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
      "end": 1.0,
      "beat": "PLACEHOLDER",
      "quote": "placeholder",
      "reason": "Local placeholder smoke test."
    }
  ],
  "grade": "none",
  "overlays": [],
  "total_duration_s": 1.0
}
```

Render a preview:

```bash
.venv/bin/python3.11 ~/Documents/video-use-ai/helpers/render.py ~/Documents/video-use-demo/edit/edl.json -o ~/Documents/video-use-demo/edit/preview.mp4 --preview --no-subtitles --no-loudnorm
```

Render a final:

```bash
.venv/bin/python3.11 ~/Documents/video-use-ai/helpers/render.py ~/Documents/video-use-demo/edit/edl.json -o ~/Documents/video-use-demo/edit/final.mp4 --no-subtitles
```

Rendering requires:

- `ffmpeg`
- `ffprobe`
- a real readable source video
- Python dependencies installed

## Expected Output Folders and Files

All session outputs are generated under the footage folder, not inside this repo:

```text
<videos_dir>/edit/
  placeholder_audio/placeholder.wav
  transcripts/<source>.json
  takes_packed.md
  edl.json
  clips_preview/
  clips_graded/
  base_preview.mp4
  base.mp4
  master.srt
  preview.mp4
  final.mp4
  verify/
  project.md
```

Only the files needed for the commands you run will exist. For the verified full placeholder demo, `placeholder_audio/`, `transcripts/`, `takes_packed.md`, `verify/`, `edl.json`, `clips_preview/`, `base_preview.mp4`, and `preview.mp4` are expected.

## Agent Startup Workflow

After setup, run the agent from the footage folder:

```bash
cd ~/Documents/video-use-demo
export ELEVENLABS_API_KEY=placeholder
codex
```

Good first prompts:

```text
Inventory these takes and propose an edit strategy.
```

```text
Edit these into a short TravelBuddy recap. Use placeholder mode for now.
```

The agent should:

1. Read `~/Documents/video-use-ai/SKILL.md`.
2. Run transcription helpers against the footage folder.
3. Read `edit/takes_packed.md`.
4. Ask for or propose an editing strategy.
5. Wait for confirmation before rendering.
6. Write all generated files to `<videos_dir>/edit/`.

## Local Runtime Verification

Current local checks found:

- Default `/usr/bin/python3` is still Python 3.9.6 and should not be used for this project.
- Python 3.11 is available at `/usr/local/bin/python3.11`.
- The working project runtime is `.venv/bin/python3.11`.
- `numba==0.60.0` imports successfully.
- `llvmlite==0.43.0` imports successfully.
- `librosa==0.11.0` imports successfully.
- `matplotlib==3.10.9` imports successfully.
- `pillow==12.2.0` imports successfully.
- `requests==2.33.1` imports successfully.
- `numpy==2.0.2` imports successfully.
- `ffmpeg` and `ffprobe` are available at version 8.1.1.
- `uv` was not found on `PATH`; the verified install path uses Python 3.11 plus pip.
- `yt-dlp` was not found on `PATH`; it is optional and only needed for downloading online sources.

The verified placeholder runtime generated a synthetic sample video, placeholder audio, placeholder transcript JSON, packed transcript markdown, timeline PNG with waveform, EDL, preview segment, base preview, and `preview.mp4`.

Known limitations:

- Placeholder mode is only a pipeline smoke test. It does not produce real speech transcription, real word timing, speaker diarization, or audio-event tags.
- With very short generated clips, do not ask `timeline_view.py` to sample exactly at the media end timestamp. Use an end time slightly inside the clip, such as `0.9` for a 1-second range.
- The verified render command uses `--no-subtitles --no-loudnorm` to keep the local smoke test minimal. Full production renders can enable subtitle generation and loudness normalization after real transcripts and source footage are available.

## Tested Commands

Run from `~/Documents/video-use-ai`:

```bash
git status --short --branch
.venv/bin/python3.11 helpers/transcribe.py --help
.venv/bin/python3.11 helpers/pack_transcripts.py --help
.venv/bin/python3.11 helpers/render.py --help
ffmpeg -version
ffprobe -version
.venv/bin/python3.11 - <<'PY'
import librosa, matplotlib, PIL, numba, llvmlite
print("librosa", librosa.__version__)
print("matplotlib", matplotlib.__version__)
print("pillow", PIL.__version__)
print("numba", numba.__version__)
print("llvmlite", llvmlite.__version__)
PY
```

Run from `~/Documents/video-use-ai`, creating a temporary footage folder:

```bash
DEMO_DIR=$(mktemp -d)
ffmpeg -y -f lavfi -i testsrc=size=320x180:rate=24:duration=2 -f lavfi -i sine=frequency=440:duration=2:sample_rate=48000 -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac "$DEMO_DIR/sample.mp4"
ELEVENLABS_API_KEY=placeholder .venv/bin/python3.11 helpers/transcribe_batch.py "$DEMO_DIR" --workers 1
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
      "reason": "Full local placeholder workflow verification."
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

Result: passed. It generated placeholder audio, a placeholder transcript JSON, `takes_packed.md`, a timeline PNG with waveform, `edl.json`, `clips_preview/seg_00_sample.mp4`, `base_preview.mp4`, and `preview.mp4`.
