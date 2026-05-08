# Local TTS Provider Plan

This repo now uses local-first transcription. `placeholder` is the default
provider, and `piper` is the optional local provider path.

## Provider Comparison

| Provider | Setup complexity | Mac compatibility | VPS compatibility | Speed | Voice realism | Voice cloning | Dependency weight | Best use case |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Placeholder mode | Very low | Excellent | Excellent | Fastest | None | No | Very light | Local smoke tests and pipeline bring-up |
| Piper | Low to medium | Good | Excellent | Very fast | Good for its size, but not premium | Limited / not the main goal | Light | Cheap, stable local narration where latency matters |

Notes:

- Placeholder mode is not a real TTS provider. It exists to keep the video workflow runnable when audio synthesis is unavailable.
- Piper is the safest lightweight local engine when the main requirement is reliability and low resource usage.

## Where Selection Should Route

The provider split happens inside `helpers/transcribe.py`, which dispatches to `helpers/tts_providers/placeholder.py` or `helpers/tts_providers/piper.py`.

Recommended routing shape:

1. Resolve the requested provider from CLI.
2. Select a provider-specific backend implementation.
3. Generate or reuse the audio file for the current video.
4. Write the transcript JSON in the same shape the rest of the workflow expects.
5. Preserve the existing placeholder fallback path as the default when no real provider is configured.

## Future CLI Pattern

```bash
--tts-provider placeholder
--tts-provider piper
--piper-voice en_US-lessac-low
--piper-data-dir /path/to/piper_data
```

## Next Provider Candidate

**Kokoro**

Reasoning:

- Piper is already wired as an optional provider path
- Kokoro is a reasonable next local engine to evaluate for quality gains
- the routing layer is already in place, so Kokoro can be added one adapter at a time

## Piper Implementation Checklist

1. keep `placeholder` as the default provider
2. allow `--tts-provider piper` to remain optional, not required
3. keep the transcript JSON output identical to the current contract
4. add provider-specific configuration without touching render code
5. verify one macOS smoke test before broadening the provider set
6. keep rollback simple by leaving placeholder unchanged

## Safest First Implementation Path

1. Keep `placeholder` as the default.
2. Add provider adapters one at a time under `helpers/tts_providers/`.
3. Reuse the existing transcript JSON contract so render code stays untouched.
4. Add one smoke test per provider path once the first backend lands.

## Architecture Recommendation

Keep the transcribe helper as the provider boundary and avoid spreading provider logic into the demo wrapper or render pipeline. A simple shape is:

- `helpers/transcribe.py` for provider selection and transcript output
- `helpers/tts_providers/` for provider adapters
- `edit/transcripts/` for the unchanged JSON contract

This makes the migration reversible and keeps the placeholder path available as the safe fallback while the first real provider is being added.

