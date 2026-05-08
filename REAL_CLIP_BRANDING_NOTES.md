# Real Clip Branding Notes

Tested with a generated 6-second cinematic-style input clip because no existing sample video was present in the repo.

## Sample Clip Used

- Input: `/var/folders/yq/kp4zp89s37s0f12dfb_y6fv80000gn/T/tmp.jSDaBVvoYI/travelbuddy_cinematic_sample.mp4`
- Branded output: `/private/var/folders/yq/kp4zp89s37s0f12dfb_y6fv80000gn/T/travelbuddy_demo_3fxt4tlg/edit/preview_branded.mp4`
- Duration: `3.008000s`

## Visual Findings

- The TravelBuddy lion watermark is visible in the lower-right corner and reads as a brand mark rather than a foreground element.
- Watermark sizing is conservative and fits cleanly inside the frame.
- On the test clip, the watermark is slightly subtle against brighter sections of footage, but still readable.
- The end card fills the frame cleanly and is centered.
- The transition into the end card is a hard cut, not a dissolve.

## Watermark Placement Notes

- Lower-right placement is correct for this brand pass.
- The current padding feels safe for most footage.
- If the brand should read more strongly on bright or busy travel shots, the first adjustment should be a small size increase rather than changing position.

## Opacity / Size Notes

- The watermark asset itself is already dark/gold and low-key.
- I would not increase opacity aggressively.
- If anything, a modest size bump would help before changing color treatment.

## End Card Timing Notes

- The branded output appends a 2-second end card.
- That timing works, but it is brisk.
- A slightly longer outro or a very short fade into the end card would feel more polished.

## Cinematic Polish Recommendations

- Keep the watermark in the lower-right.
- Add a short crossfade or dip-to-black before the end card in a later pass.
- Test the same branding settings on one more clip with slower motion and darker tones.
- Revisit subtitle styling after the visual layer is stable.

## Safest Next Visual Upgrade

Add a short transition into the end card, then verify the same branded path on one additional real-world travel clip before changing watermark size or opacity.
