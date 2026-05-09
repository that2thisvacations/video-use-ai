# TRAVELBUDDY QUICKSTART

## A) Setup
```bash
cd ~/Documents/video-use-ai
python3.11 -m venv .venv
./.venv/bin/pip install -r requirements.txt
brew install ffmpeg
```

Optional Piper voice download:
```bash
./.venv/bin/python3.11 -m piper.download_voices en_US-lessac-low --data-dir ./models/piper
```

## B) Single Reel
```bash
./travelbuddy reel "Travel is the new freedom."
```

## C) Dramatic Reel
```bash
./travelbuddy reel "Stop applying. Start building." --pause-profile dramatic
```

## D) Batch Reels
```bash
./travelbuddy batch examples/topics_daily.txt
```

## E) Output Locations
- `outputs/single/`
- `outputs/batch/`
- `edit/`

## F) Common Flags
- `--pause-profile`
- `--content-type`
- `--caption-style`
- `--open-output`

## G) Troubleshooting
- Piper missing: install `piper-tts` in `.venv`, then download a voice model.
- ffmpeg missing: install with `brew install ffmpeg`.
- ffprobe missing: use the system ffprobe that ships with ffmpeg.
- Finder open issues: rerun without `--open-output`, then open the folder manually.

## H) Recommended Daily Creator Workflow
```bash
./travelbuddy reel "Travel is the new freedom."
./travelbuddy reel "Stop applying. Start building." --pause-profile dramatic
./travelbuddy batch examples/topics_daily.txt
```
