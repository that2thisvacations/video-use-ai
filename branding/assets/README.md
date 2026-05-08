# TravelBuddy Branding Assets

This folder is the landing zone for future TravelBuddy artwork and font references.

Supported placeholder asset types:

- transparent PNG for watermarks
- transparent PNG or short MP4 for end cards
- font files or font references for branded typography

Recommended formats:

- Watermarks: transparent PNG, ideally with alpha and a tight bounding box
- End cards: transparent PNG for static cards, MP4 or WebM for animated cards
- Fonts: OTF or TTF, stored only if licensing allows local packaging

Design notes:

- keep watermarks small and unobtrusive
- prefer transparent PNGs when the art needs to float over video
- use clean edges and avoid baked-in backgrounds for overlays
- keep end cards readable on mobile and desktop

## Final PNG Placement

Place finished TravelBuddy PNG assets here:

- `branding/assets/watermarks/travelbuddy_lion_watermark.png`
- `branding/assets/watermarks/travelbuddy_circle_founder_mark.png`
- `branding/assets/endcards/travelbuddy_luxury_endcard.png`

## Recommended Dimensions

- Watermarks: `512x512` or smaller, with alpha and a transparent background
- Founder mark: `512x512` to `1024x1024`, transparent PNG, tight crop
- End card: `1920x1080` or `1080x1920` depending on delivery format, transparent PNG if it must overlay footage

## Asset Usage

- `travelbuddy_lion_watermark.png`: primary watermark for branded exports and preview protection
- `travelbuddy_circle_founder_mark.png`: alternate watermark or avatar-style brand mark for smaller UI placements
- `travelbuddy_luxury_endcard.png`: closing card for premium or luxury-themed TravelBuddy demos

## Background Guidance

- keep all final PNG assets transparent unless they are intentionally full-frame cards
- avoid flat white or opaque backgrounds for floating overlays
- prefer a tight crop with alpha so the asset scales cleanly across preview and final exports
