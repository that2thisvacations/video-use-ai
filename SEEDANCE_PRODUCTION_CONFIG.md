# Seedance 2.0 Production Config

This document defines the production generation settings layer for Seedance 2.0.
It is configuration-only and does not change the local TravelBuddy render flow.

## Supported Durations

```text
5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15
```

## Supported Resolutions

```text
480p, 720p, 1080p
```

## Supported Aspect Ratios

```text
1:1, 9:16, 16:9, 3:4, 4:3
```

## Default Settings

- duration: `10`
- resolution: `1080p`
- aspect ratio: `9:16`
- model: `seedance_2_0`
- generation mode: `production`
- output intent: `social_video`

## Example CLI Usage

```bash
./travelbuddy reel "Travel is the new freedom." --duration 10 --resolution 1080p --aspect-ratio 9:16
./travelbuddy reel "Luxury travel sells the lifestyle." --duration 15 --resolution 720p --aspect-ratio 16:9
./travelbuddy batch examples/topics_daily.txt --duration 8 --resolution 1080p --aspect-ratio 9:16
```

## Future API Handoff Payload

The CLI should eventually hand off a profile like this to a real generation API:

```json
{
  "prompt": "Travel is the new freedom.",
  "duration_seconds": 10,
  "resolution": "1080p",
  "aspect_ratio": "9:16",
  "model": "seedance_2_0",
  "generation_mode": "production",
  "output_intent": "social_video"
}
```

## Batch Generation Notes

- `--topics-file` should reuse the same production config for each topic unless a future scheduler overrides it.
- Batch manifests should record the production Seedance profile for every reel.
- `generated_script.json` should also carry the same production metadata so downstream automation can hand off cleanly.
- This layer does not create synthetic clips or placeholder video assets.

## Production Readiness Checklist

- [x] CLI validation for duration, resolution, and aspect ratio
- [x] Seedance profile written into generated script JSON
- [x] Seedance profile written into batch manifests
- [x] Defaults documented
- [x] Handoff payload documented
- [x] No fake Seedance clips introduced
- [x] Local render workflow remains separate
