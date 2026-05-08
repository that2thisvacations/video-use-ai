# Branding Integration

This document explains how TravelBuddy branding can be wired into the demo workflow later without changing the core render engine yet.

## How Branding Will Integrate Later

The first integration layer should live in the demo wrapper, then fan out into render hooks only after the visual direction is settled.

Suggested progression:

1. Demo wrapper resolves brand pack metadata.
2. Wrapper selects watermark, end card, and subtitle style hooks.
3. Wrapper generates a branded export alongside the base preview.
4. Render pipeline consumes those hooks when the brand implementation is ready.
5. Core helper behavior stays unchanged until brand assets are stable.

## Overlay Architecture

TravelBuddy overlays should be treated as optional layers above the existing base render.

Possible overlay types:

- watermark overlay in a corner
- branded end card at the tail
- subtitle style presets for theme-specific caption treatment
- short stings or motion accents for transitions

Overlay order should remain explicit and predictable:

1. base render
2. overlays
3. subtitles
4. final preview/export

## Required Asset Paths

Canonical assets expected by the demo wrapper:

- `branding/assets/watermarks/travelbuddy_lion_watermark.png`
- `branding/assets/endcards/travelbuddy_luxury_endcard.png`

Optional future hook:

- `branding/assets/watermarks/travelbuddy_circle_founder_mark.png`

## Render Hook Locations

Future hook points should start in these areas:

- `travelbuddy_demo.py` for demo-time brand selection
- `helpers/render.py` for final overlay and subtitle application
- `helpers/grade.py` for theme-specific look presets
- `poster.html` for branding previews
- `branding/` for asset and pack metadata

Branded output path in the demo workflow:

- `edit/preview_branded.mp4`

## Future Automation Ideas

- load a TravelBuddy brand pack from `branding/`
- auto-select watermark and end card assets by theme
- map `--style` to a grade preset and subtitle template
- add a brand manifest file for reusable pack definitions
- add a folder bootstrap command for new TravelBuddy projects
- add a branded export command that shares the same base render but swaps in a finished brand layer

## Command Example

```bash
ELEVENLABS_API_KEY=placeholder .venv/bin/python3.11 travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic
```

If the canonical assets are present, the wrapper should:

- keep `edit/preview.mp4` unchanged
- generate `edit/preview_branded.mp4`
- overlay the lion watermark in the lower-right corner
- append the luxury end card as a 2-second outro

If the preview has audio, the branded export should preserve it. If the
preview has no audio, the branded export should still complete as a
video-only output instead of failing.

## Fallback Behavior

If the branding assets are missing:

- skip branded export safely
- keep the base preview flow intact
- print a clear message naming the missing asset
- do not fail the demo workflow

If the preview has no audio:

- print a clear message that video-only branded export is being used
- continue generating `edit/preview_branded.mp4`
- keep `edit/preview.mp4` unchanged

## Safest Next Implementation Step

Keep the next change small:

1. wire `travelbuddy_demo.py` to read brand metadata only
2. keep placeholder paths for watermark, end card, and subtitle style
3. confirm the wrapper still runs end to end
4. only then map those hooks into render code

That keeps the branding layer reversible and avoids coupling it to the current ffmpeg pipeline too early.
