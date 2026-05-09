# Pause Profile Comparison

This compares the local-first Piper topic render using the same topic and
social-ready TravelBuddy workflow with two pause profiles:

- `natural`
- `dramatic`

Test command shape:

```bash
.venv/bin/python3.11 travelbuddy_demo.py \
  --social-ready \
  --tts-provider piper \
  --piper-voice en_US-lessac-low \
  --piper-data-dir ./models/piper \
  --topic "Stop applying. Start building. Travel is the new freedom." \
  --pause-profile <profile>
```

## Natural Pacing Notes

- Feels closer to a short-form default.
- The narration moves with enough air to separate ideas, but it still keeps
  momentum.
- The pause length is restrained enough that the script does not feel overly
  dramatic.
- Best fit for most social exports where the goal is clarity and speed.

## Dramatic Pacing Notes

- The longer pause profile gives each chunk more room to land.
- It creates more emphasis around the chunk boundaries and CTA.
- It feels more theatrical, but it can slow the rhythm if the topic is already
  compact.
- Best fit when the script needs more gravity or a stronger ending beat.

## Which Should Be Default

`natural` should remain the default.

Reason:

- It preserves short-form tempo.
- It stays closer to the current social-ready rhythm.
- It is the safer baseline for most TravelBuddy topic videos.

## Best Use Case By Profile

- `tight`: fastest pacing, utility-style updates, high-density content
- `natural`: default social pacing, most topic videos, balanced clarity
- `dramatic`: emphasis, emotional framing, slower CTA landings, premium or
  cinematic delivery

## ffprobe Summary

`edit/final_social.mp4` from both runs:

- duration: `3.041667s`
- dimensions: `1080x1920`
- video codec: `h264`
- audio codec: `aac`

## Final Recommendation

Keep `natural` as the default and reserve `dramatic` for cases where the
script needs a more deliberate, premium cadence.

The main takeaway is that pause profile choice is now an editorial decision,
not a render stability issue. The pipeline stays unchanged; only the narration
rhythm shifts.
