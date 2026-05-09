# Script Phrasing Improvements

This change tightens the topic-to-script layer for short-form TravelBuddy
videos without introducing AI APIs or changing the render pipeline.

## What Changed

- Hooks now use deterministic variation pools instead of a single fixed line.
- CTA phrasing now varies by content type so the ending feels less repetitive.
- Voice chunks are split into shorter phrases for better spoken rhythm.
- Caption groups are built from those chunks so subtitles break more cleanly.
- Each script now records a `script_style` value such as `mentor`, `punchy`,
  `cinematic`, `urgent`, or `luxury`.
- Each script now records `emphasis_words` so key words can be visually
  highlighted in `cinematic_gold` without changing the caption engine.

## Pacing Strategy

- Keep the headline as the anchor.
- Break the hook into short, spoken pieces.
- Let each main point land as a single beat or a small beat pair.
- End with a CTA that feels like a finish, not a paragraph.
- Use deterministic pause hints instead of random timing.
- Use named pause profiles when the narration needs a tighter, more natural,
  or more dramatic gap.

TravelBuddy default:

- `natural`: default daily/social rhythm
- `tight`: fast news or quick-hit content
- `dramatic`: motivational or emphasis reels

## Social Rhythm Strategy

- Favor direct verbs and short clauses.
- Use punctuation breaks to create spoken stops.
- Keep the writing compact enough for voice pacing and on-screen captions.
- Preserve the same transcript contract so the render path stays stable.

## Future Upgrade Ideas

- Add a second pass for topic-specific sentence timing.
- Expand variation pools with more TravelBuddy brand tones.
- Add a dedicated caption emphasis layer for key phrases.
- Expand emphasis words into animated emphasis only after the static highlight
  pass is validated.
- Introduce smarter chunking for long topics or multi-part hooks.
- Add optional script reviews for pace before render, still without AI APIs.
- Add finer-grained pause timing per chunk once the current profiles are
  visually approved.
