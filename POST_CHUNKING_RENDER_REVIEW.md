# Post-Chunking Render Review

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

## Verified Outputs

- `edit/generated_script.json`
- `edit/preview_branded_916_captioned.mp4`
- `edit/final_social.mp4`

## Script Structure Check

The generated script now includes:

- `voice_chunks`
- `caption_groups`
- `suggested_pause_ms`

The chunked structure is working as intended. The script is no longer a single flat narration blob.

## ffprobe Summary

`edit/final_social.mp4`

- duration: `3.041667s`
- dimensions: `1080x1920`
- video codec: `h264`
- audio codec: `aac`

## Comparison to `FIRST_REAL_RENDER_REVIEW.md`

### Pacing

Improved. The narration now has cleaner chunk boundaries, and the generated captions follow those groupings instead of reading like one continuous block.

### Captions

Improved. The caption groups are easier to scan on mobile, and the breaks feel more deliberate than the first review pass.

### Voice Quality

Still flat. Piper is clean and understandable, but it remains synthetic and does not yet sound especially branded or expressive.

### Outro Timing

Still somewhat abrupt. The end card works, but the transition still feels like a hard cutoff rather than a more polished finish.

### Overall Quality

This is a better social render than the first review. The rhythm is clearer, the captions are more readable, and the output feels less blocky.

## Review Highlights

- The chunked script makes the spoken rhythm feel more intentional.
- Caption grouping is a real visual improvement over the first pass.
- The watermark remains restrained and visible.
- The final render still looks technically solid at `1080x1920`.
- The big remaining limitation is voice expressiveness, not export quality.

## Best Next Upgrade

Improve narration timing and voice phrasing before adding more visual motion.

The highest-value next step is to make the chunked script read more naturally at the voice level, then revisit caption emphasis or subtle subtitle motion after that.
