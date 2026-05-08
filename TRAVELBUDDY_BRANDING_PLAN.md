# TravelBuddy Branding Plan

This document defines the first branding layer for the media engine without changing render behavior yet. It is an architecture and sequencing guide, not an implementation spec.

## 1. Brand Visual Direction

### Colors

Start with a restrained travel-editor palette that can flex across premium, documentary, and high-energy modes:

- Primary dark: charcoal, graphite, deep slate
- Surface neutral: warm stone, sand, fog white
- Accent warm: coral, amber, sunset orange
- Accent cool: ocean blue, teal, horizon blue
- Utility: success green for approvals, muted red for cut warnings

Recommended design rule:

- one dark base
- one warm accent
- one cool accent
- one neutral text color

This keeps the brand from collapsing into a monochrome dashboard or a saturated gimmick.

### Typography

Use a two-font system:

- display: a strong sans serif for hero headings and section labels
- mono: a technical mono font for timestamps, clip labels, diagnostics, and workflow metadata

Current repo precedent already leans toward `Inter` and `JetBrains Mono`. TravelBuddy can keep that structure initially, then evolve if the brand needs more luxury or editorial character.

### Motion Style

Motion should feel like travel media, not app chrome:

- eased, confident, cinematic
- slow in, clean settle, no bouncy micro-interactions
- use motion to reveal structure, not decorate empty space
- prefer deliberate cuts and wipes over flashy transitions

The brand should suggest guided movement, destination discovery, and polished editorial rhythm.

### Cinematic Tone

TravelBuddy should feel:

- polished
- modern
- location-aware
- editorial
- not stock-travel generic

The visual tone should support:

- destination recaps
- itinerary explainers
- trip highlights
- travel stories
- premium travel marketing

### Subtitle Styling

Subtitle treatment should be a brand element, not a default renderer artifact.

Potential directions:

- cinematic lower-third captions for premium travel
- compact uppercase captions for social highlight reels
- sentence-case captions for documentary or guided narration
- subtitling with warm outline and controlled bottom margin for mobile-safe presentation

Initial rule:

- subtitle style should vary by render theme, but all styles should remain readable and stable.

### Overlays

Overlay language should support travel storytelling:

- location cards
- trip stats
- route lines
- day-by-day chapter markers
- mileage, date, and destination labels
- map-like or itinerary-like data overlays

Overlays should feel informative first and decorative second.

### Watermark Concepts

TravelBuddy watermark ideas:

- small lower-right logotype lockup
- faint corner badge for unbranded preview exports
- slim top-right brand tag for social cuts
- subtle outline mark integrated into overlay cards

Rules:

- watermark should never dominate the footage
- use it only where it helps provenance, preview protection, or social sharing
- keep it optional and theme-aware

## 2. Render Theme Concepts

These are future theme archetypes for the media engine. They should map to presets, subtitle treatments, overlay sets, and grading choices later.

### Cinematic

Use case:

- destination films
- trip montages
- premium recaps

Traits:

- warm contrast
- soft shadow lift
- restrained captions
- elegant pacing
- minimal overlays

### Luxury Travel

Use case:

- high-end resort content
- premium hospitality
- aspirational brand videos

Traits:

- polished blacks
- rich highlights
- gold or amber accents
- slower motion
- refined typography

### Breaking News

Use case:

- urgent travel updates
- route changes
- event coverage

Traits:

- sharp contrast
- bold type
- compact headline overlays
- decisive motion
- strong information hierarchy

### AI Mentor

Use case:

- guided planning
- travel assistant explainers
- itinerary coaching

Traits:

- calm, instructional pacing
- readable captions
- cards and callouts
- cool accent support
- minimal visual clutter

### Documentary

Use case:

- story-driven travel narratives
- cultural reports
- longer-form edits

Traits:

- neutral grading
- sentence-case subtitles
- slower pace
- lower visual noise
- chaptered structure

### Hype Reel

Use case:

- highlights
- short social cuts
- teaser content

Traits:

- high-energy cuts
- punchier captions
- stronger contrast
- brighter accents
- more motion and more frequent overlays

## 3. Recommended Future Modification Files

These are the first places that should absorb TravelBuddy branding once implementation starts:

- `helpers/render.py`
- `helpers/grade.py`
- `poster.html`
- `README.md`
- `SKILL.md`
- `static/video-use-banner.png`
- `static/timeline-view.svg`
- subtitle rendering paths inside `helpers/render.py`

Suggested responsibility split:

- `helpers/grade.py`: theme-specific look and grading presets
- `helpers/render.py`: subtitle style selection, overlays, theme wiring
- `poster.html`: brand showcase and visual identity
- `static assets`: logos, banner art, iconography, preview motifs
- subtitle paths: theme-specific caption rules and export naming

## 4. Suggested Folder Structure

Keep branding assets separate from engine code so the system can evolve without becoming tangled.

```text
branding/
  packs/
    travelbuddy/
      brand.json
      palette.json
      typography.json
      subtitles.json
      overlays.json
      themes/
        cinematic.json
        luxury-travel.json
        breaking-news.json
        ai-mentor.json
        documentary.json
        hype-reel.json
      fonts/
      overlays/
      transitions/
      audio-stings/
      watermarks/
```

Recommended subfolders:

- `overlays/` for cards, motion graphics, lower thirds, route visuals
- `transitions/` for wipes, fades, interstitial motion, chapter breaks
- `audio-stings/` for short open/close sounds, transitions, stingers
- `fonts/` for brand-approved type files or font references
- `branding-packs/` or `branding/packs/` for reusable brand profiles

This structure keeps TravelBuddy theme assets versioned without forcing them into the core engine tree.

## 5. Minimal-Risk Implementation Order

1. Brand docs only.
2. Static asset refresh for README/poster/timeline visuals.
3. Add brand pack metadata files.
4. Wire theme selection into the demo wrapper only.
5. Map brand pack to subtitle styling in render paths.
6. Map brand pack to grade presets.
7. Add overlay and watermark templates.
8. Add audio stings and transitions.
9. Add automation and export presets.

This order minimizes risk because it separates visual identity from pipeline mechanics until the design is stable.

## 6. Future CLI Example

```bash
python travelbuddy_demo.py --style cinematic --brand TRAVELBUDDY
```

## Implementation Guidance

For the first phase, treat this plan as the source of truth for:

- visual direction
- render theme language
- asset organization
- implementation sequencing

Do not change core rendering behavior until the branding system is defined well enough to survive a real edit pass.
