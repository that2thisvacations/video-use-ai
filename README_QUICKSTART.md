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

## D) Creator Modes
```bash
./travelbuddy reel "AI is replacing average marketing." --mode ai_marketing
./travelbuddy reel "Your next paycheck could come from an airport." --mode airport_intel
./travelbuddy reel "Stop applying. Start building." --mode motivational
./travelbuddy reel "Breaking: travel demand is shifting." --mode breaking_news
./travelbuddy reel "Luxury travel feels calm." --mode luxury
./travelbuddy reel "The best mentor stories sound simple." --mode mentor_story
```

## E) Batch Reels
```bash
./travelbuddy batch examples/topics_daily.txt
```

## F) Output Locations
- `outputs/single/`
- `outputs/batch/`
- `edit/`

## G) Common Flags
- `--pause-profile`
- `--content-type`
- `--mode`
- `--caption-style`
- `--open-output`

## H) Troubleshooting
- Piper missing: install `piper-tts` in `.venv`, then download a voice model.
- ffmpeg missing: install with `brew install ffmpeg`.
- ffprobe missing: use the system ffprobe that ships with ffmpeg.
- Finder open issues: rerun without `--open-output`, then open the folder manually.

## I) Recommended Daily Creator Workflow
```bash
./travelbuddy reel "Travel is the new freedom."
./travelbuddy reel "Stop applying. Start building." --pause-profile dramatic
./travelbuddy reel "AI is replacing average marketing." --mode ai_marketing
./travelbuddy batch examples/topics_daily.txt
```
