# First Real Local Social Render Review

Run command:

```bash
cd ~/Documents/video-use-ai
.venv/bin/python3.11 travelbuddy_demo.py \
  --social-ready \
  --tts-provider piper \
  --piper-voice en_US-lessac-low \
  --piper-data-dir ./models/piper \
  --topic "Stop applying. Start building. Travel is the new freedom."
```

## Generated Outputs

- `edit/generated_script.json`
- `edit/preview_branded.mp4`
- `edit/preview_branded_916.mp4`
- `edit/preview_branded_916_captioned.mp4`
- `edit/final_social.mp4`

## ffprobe Summary

`final_social.mp4`

- duration: `3.041667s`
- video: `h264`
- video dimensions: `1080x1920`
- audio: `aac`

## Review Notes

### Piper Voice Quality

- The Piper read is clean and understandable.
- It is functional for a first pass, but it still sounds synthetic and slightly flat.
- For short social edits, the voice is acceptable; it does not yet carry a strong branded identity.

### Pacing

- The generated narration is concise and keeps the edit moving.
- The overall pacing is short-form friendly, but the delivery is still a little uniform.
- The script currently reads like a structured pitch rather than a tightly timed social script.

### Subtitle Readability

- Captions are readable on a mobile-sized frame.
- Gold styling has enough contrast for this clip.
- The bottom safe-zone placement is appropriate and does not fight the main image.

### Watermark Visibility

- The TravelBuddy watermark is visible in the lower-right corner.
- It is present without dominating the frame.
- On this clip, the mark feels appropriately restrained.

### End Card Timing

- The end card lands cleanly as the outro.
- The 2-second outro is usable, though it feels a little abrupt for a more polished social finish.

### Cinematic Feel

- The vertical export and caption pass make the output feel much closer to a social-ready asset.
- The result is stable and coherent, but not yet distinctly premium in motion design.

### Caption Placement

- The caption placement stays low and centered, which fits the current style.
- The current treatment is readable, but static.
- The output would benefit from a little more visual hierarchy in longer captions.

### Mobile Readability

- The vertical export works well on mobile dimensions.
- The caption scale is viable for phone viewing.
- The overall framing is strong enough for a first release pass.

### Export Quality

- `preview_branded_916.mp4` and `preview_branded_916_captioned.mp4` both probe cleanly at `1080x1920`.
- Audio is preserved through the branded social export.
- The final output is technically solid.

## Weaknesses

- Piper narration is serviceable, but not yet expressive.
- The script reads like one block of guidance; it does not yet have stronger beat-to-beat timing.
- Captions are static and do not add motion energy.
- The end card could use a slightly softer transition or more deliberate timing.

## Highest ROI Next Upgrade

Improve script timing and narration chunking before adding heavier visual effects.

The most useful next step is to break the generated `voice_text` into better-paced segments so:

- the narration sounds more intentional
- caption breaks are more natural
- social pacing feels less flat

## Safest Next Lightweight Upgrades

- subtitle emphasis within the existing caption pass
- better narration chunking in the script engine
- small pacing adjustments in the generated `voice_text`
- lighter caption animation once the static baseline is approved
- scene sequencing tweaks in the topic template, not the render engine
