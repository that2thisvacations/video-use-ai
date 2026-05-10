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

## E) Seedance 2.0 Production Config
Supported durations:
`5 6 7 8 9 10 11 12 13 14 15`

Supported resolutions:
`480p 720p 1080p`

Supported aspect ratios:
`1:1 9:16 16:9 3:4 4:3`

Defaults:
- duration: `10`
- resolution: `1080p`
- aspect ratio: `9:16`

Examples:
```bash
./travelbuddy reel "Travel is the new freedom." --duration 10 --resolution 1080p --aspect-ratio 9:16
./travelbuddy reel "Luxury travel sells the lifestyle." --duration 15 --resolution 720p --aspect-ratio 16:9
./travelbuddy batch examples/topics_daily.txt --duration 8 --resolution 1080p --aspect-ratio 9:16
```

## F) Batch Reels
```bash
./travelbuddy batch examples/topics_daily.txt
```

## G) Output Locations
- `outputs/single/`
- `outputs/batch/`
- `edit/`

## H) Common Flags
- `--pause-profile`
- `--content-type`
- `--mode`
- `--duration`
- `--resolution`
- `--aspect-ratio`
- `--caption-style`
- `--open-output`

## I) Troubleshooting
- Piper missing: install `piper-tts` in `.venv`, then download a voice model.
- ffmpeg missing: install with `brew install ffmpeg`.
- ffprobe missing: use the system ffprobe that ships with ffmpeg.
- Finder open issues: rerun without `--open-output`, then open the folder manually.

## J) Recommended Daily Creator Workflow
```bash
./travelbuddy reel "Travel is the new freedom."
./travelbuddy reel "Stop applying. Start building." --pause-profile dramatic
./travelbuddy reel "AI is replacing average marketing." --mode ai_marketing
./travelbuddy reel "Travel is the new freedom." --duration 10 --resolution 1080p --aspect-ratio 9:16
./travelbuddy batch examples/topics_daily.txt
```
