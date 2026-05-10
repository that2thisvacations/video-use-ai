# Seedance Payload Reference

`helpers/seedance_payload.py` builds a production-ready JSON handoff payload for TravelBuddy reels. It does not call any API and does not change the local render engine.

## Payload schema

```json
{
  "model": "seedance_2_0",
  "generation_mode": "production",
  "topic": "Travel is the new freedom.",
  "prompt": "...",
  "duration_seconds": 10,
  "resolution": "1080p",
  "aspect_ratio": "9:16",
  "style": "...",
  "camera_direction": "...",
  "motion_profile": "...",
  "visual_energy": "...",
  "caption_style": "cinematic_gold",
  "branding": {
    "watermark": true,
    "endcard": true
  },
  "output_intent": "social_video"
}
```

The payload also carries TravelBuddy metadata for later handoff:
- `mode`
- `mode_description`
- `pacing_profile`
- `export_preset`
- `content_type`
- `script_style`
- `voice_chunks`

## Mode mappings

- `motivational`: cinematic motivation, emotional momentum, heroic camera movement
- `airport_intel`: fast airport motion, departure-board emphasis, travel urgency
- `luxury`: cinematic luxury lifestyle, slow camera movement, premium lighting
- `ai_marketing`: futuristic UI, AI overlays, digital motion energy
- `breaking_news`: urgency, zoom cuts, high tension pacing
- `mentor_story`: emotional realism, documentary tone, cinematic storytelling

## Supported generation controls

- Durations: `5` through `15` seconds
- Resolutions: `480p`, `720p`, `1080p`
- Aspect ratios: `1:1`, `9:16`, `16:9`, `3:4`, `4:3`

Defaults:
- duration: `10`
- resolution: `1080p`
- aspect ratio: `9:16`

## Batch workflow

Single reel payloads are written to:

```text
edit/seedance_payload.json
```

Batch payloads are written per reel:

```text
edit/batch/reel_001/seedance_payload.json
edit/batch/reel_002/seedance_payload.json
```

Batch runs also record payload paths in:
- `edit/batch/batch_manifest.json`
- `edit/batch/batch_manifest.md`

## Future API handoff notes

The future API call site should send the payload as-is and keep the transcript contract stable. The next integration layer can replace the local-only export step without changing the prompt builder or mode mapping logic.

## Production readiness checklist

- Validate duration, resolution, and aspect ratio before request dispatch
- Confirm caption and branding metadata are present
- Verify the final payload path is written alongside the generated script
- Keep local render and production payload generation separate
- Preserve batch manifests for review and retry handling
