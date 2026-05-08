# Branding Integration

This document explains how TravelBuddy branding can be wired into the demo workflow later without changing the core render engine yet.

## How Branding Will Integrate Later

The first integration layer should live in the demo wrapper, then fan out into render hooks only after the visual direction is settled.

Suggested progression:

1. Demo wrapper resolves brand pack metadata.
2. Wrapper selects placeholder watermark, end card, and subtitle style hooks.
3. Render pipeline consumes those hooks when the brand implementation is ready.
4. Core helper behavior stays unchanged until brand assets are stable.

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

## Render Hook Locations

Future hook points should start in these areas:

- `travelbuddy_demo.py` for demo-time brand selection
- `helpers/render.py` for final overlay and subtitle application
- `helpers/grade.py` for theme-specific look presets
- `poster.html` for branding previews
- `branding/` for asset and pack metadata

## Future Automation Ideas

- load a TravelBuddy brand pack from `branding/`
- auto-select watermark and end card assets by theme
- map `--style` to a grade preset and subtitle template
- add a brand manifest file for reusable pack definitions
- add a folder bootstrap command for new TravelBuddy projects

## Safest Next Implementation Step

Keep the next change small:

1. wire `travelbuddy_demo.py` to read brand metadata only
2. keep placeholder paths for watermark, end card, and subtitle style
3. confirm the wrapper still runs end to end
4. only then map those hooks into render code

That keeps the branding layer reversible and avoids coupling it to the current ffmpeg pipeline too early.
