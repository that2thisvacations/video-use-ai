# Post-Phrasing Render Review

This review compares the current local-first Piper social render against:

- `FIRST_REAL_RENDER_REVIEW.md`
- `POST_CHUNKING_RENDER_REVIEW.md`

Test command:

```bash
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

## ffprobe Summary

`edit/final_social.mp4`

- duration: `3.041667s`
- dimensions: `1080x1920`
- video codec: `h264`
- audio codec: `aac`

## Comparison Notes

### Against `FIRST_REAL_RENDER_REVIEW.md`

- Narration flow is more structured now.
- The script no longer reads like one continuous block.
- Captions break in cleaner places, which improves mobile scan speed.
- The CTA lands with a little more shape instead of arriving as a single flat line.

### Against `POST_CHUNKING_RENDER_REVIEW.md`

- Pacing is a little better because the phrasing layer now controls hooks and CTAs more intentionally.
- Chunk rhythm is cleaner and the subtitle grouping feels less generic.
- The overall rhythm still depends heavily on the Piper voice model, which remains the main limitation.

## Quality Observations

- Narration flow: improved, more deliberate, and less monotone in structure.
- Pacing: better than the previous reviews, especially around the hook and CTA.
- Chunk rhythm: shorter beats help the short-form feel.
- CTA landing: stronger than before, but still not fully natural.
- Piper realism: understandable and stable, but still synthetic and slightly flat.
- Subtitle readability: solid on the vertical frame.
- Emotional cadence: better than the earlier pass, but still modest.
- Social retention feel: improved because the script now moves faster between ideas.
- Mobile readability: good; the caption blocks are legible at the current size and placement.
- Overall polish: technically strong, but the narration delivery is still the bottleneck.

## What Improved

- The topic script now has more purposeful sentence rhythm.
- Hooks are less repetitive and more aligned to the content type.
- Captions are easier to scan because the grouping is cleaner.
- The final export still holds up at 1080x1920 with audio preserved.

## What Still Feels Weak

- Piper still sounds synthetic and slightly restrained.
- Some phrase joins are still awkward in spots.
- The outro remains functional but still ends a little abruptly.

## Biggest Remaining Bottleneck

The voice model, not the render pipeline.

The current system is now good enough structurally. The next quality jump will come from better narration timing or a better local TTS model, not from adding more ffmpeg complexity.

## Highest ROI Next Upgrade

Improve narration timing before adding more visual complexity.

Safest next step:

- refine chunk timing for topic scripts
- add a better pause strategy around hooks and CTAs
- keep the same transcript contract and output filenames

That keeps the pipeline stable while moving the perceived quality forward.
