# Piper Local Validation

This document records a standalone, non-destructive Piper validation on macOS.
It does not wire Piper into the repo runtime. The repo now has optional Piper
support, but the default provider remains `placeholder`.

## Environment Detected

- Python: `Python 3.11.15`
- Architecture: `x86_64`
- ffmpeg: available at `/usr/local/bin/ffmpeg`
- ffprobe: system binary at `/usr/local/bin/ffprobe` works for validation
- Repo virtualenv: `.venv` exists and uses `Python 3.11.15`
- Repo virtualenv Piper availability: installed successfully for verification

## Safest Mac Install Method

The lowest-risk validation path is a throwaway virtual environment outside the
repo:

```bash
python3 -m venv /tmp/piper-check
source /tmp/piper-check/bin/activate
pip install -U pip setuptools wheel
pip install piper-tts
```

This keeps the repo runtime untouched and makes rollback trivial. The optional
repo path later is:

```bash
cd ~/Documents/video-use-ai
.venv/bin/pip install piper-tts
```

The repo venv path was also verified successfully:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 -m pip install piper-tts
.venv/bin/python3.11 -m piper.download_voices en_US-lessac-low --data-dir ./models/piper
```

## Recommended Lightweight English Voice Model

Use the lightweight U.S. English Lessac model:

```text
en_US-lessac-low
```

The model is hosted by the Piper voices repository and is a compact English
voice suitable for first-pass validation.

## Expected Model Storage Path

Keep voice assets outside the repo. A simple local path is:

```text
/tmp/piper-check/piper_data/
```

For a persistent user-level path, use something like:

```text
~/Library/Application Support/video-use-ai/piper/
```

The provider adapter reads the model path from the `--piper-data-dir` CLI flag.

## Standalone CLI Test Commands

The exact standalone validation flow that succeeded was:

```bash
workdir=$(mktemp -d)
python3 -m venv "$workdir/venv"
"$workdir/venv/bin/pip" install -U pip setuptools wheel
"$workdir/venv/bin/pip" install piper-tts

voice_dir="$workdir/piper_data"
out="$workdir/piper_test.wav"
mkdir -p "$voice_dir"

"$workdir/venv/bin/python" -m piper.download_voices en_US-lessac-low --data-dir "$voice_dir"
"$workdir/venv/bin/python" -m piper -m en_US-lessac-low -f "$out" --data-dir "$voice_dir" -- 'Hello from TravelBuddy.'
```

The first attempt using stdin failed with:

```text
wave.Error: # channels not specified
```

The documented `-- 'text'` form worked.

For the repo runtime, the missing-Piper path should now fail gracefully with a
clear install message instead of changing the default provider:

```bash
.venv/bin/python3.11 helpers/transcribe.py /tmp/test_clip.mp4 --tts-provider piper
```

## Verified Repo Demo Workflow

The local repo venv workflow also succeeded with the branded TravelBuddy demo:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 -m piper.download_voices en_US-lessac-low --data-dir ./models/piper
.venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --tts-provider piper --piper-voice en_US-lessac-low --piper-data-dir ./models/piper
```

Verified outputs:

- `edit/piper_audio/demo_sample.wav`
- `edit/transcripts/demo_sample.json`
- `edit/preview.mp4`
- `edit/preview_branded.mp4`

Model location convention used here:

```text
./models/piper
```

Generated models, audio, and video should not be committed.

## Expected WAV Output

Successful validation produced:

```text
/var/folders/yq/kp4zp89s37s0f12dfb_y6fv80000gn/T/tmp.imTRL0O2vv/piper_test.wav
```

Observed output:

```text
RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 16000 Hz
```

## Rollback and Removal

Rollback is straightforward:

1. delete the throwaway temp venv and temp working directory
2. remove any downloaded voice models if they were stored in a persistent
   folder
3. leave the repo runtime unchanged
4. continue using `placeholder` in the existing provider routing if Piper is
   removed or unavailable

## Validation Result

Standalone Piper installation succeeded in a throwaway temp venv and generated
a short WAV file without modifying the repo runtime.
