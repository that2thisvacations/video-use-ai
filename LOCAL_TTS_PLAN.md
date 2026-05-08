# Local TTS Provider Migration Plan

This repo currently uses a placeholder transcript path when `ELEVENLABS_API_KEY`
is missing or set to a local placeholder value. That is the safest baseline.
The next step is to introduce a provider switch in `helpers/transcribe.py`
without changing the current default behavior.

## Provider Comparison

The comparison below is framed for this repo’s use case: short-form video
generation where transcript output needs to unblock the rest of the pipeline.

| Provider | Setup complexity | Mac compatibility | VPS compatibility | Speed | Voice realism | Voice cloning | Dependency weight | Best use case |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Placeholder mode | Very low | Excellent | Excellent | Fastest | None | No | Very light | Local smoke tests and pipeline bring-up |
| Piper | Low to medium | Good | Excellent | Very fast | Good for its size, but not premium | Limited / not the main goal | Light | Cheap, stable local narration where latency matters |
| Kokoro | Medium | Good | Good | Fast | Strong for a compact model | Limited / depends on the wrapper | Light to moderate | Default local TTS candidate for TravelBuddy narration |
| Chatterbox | Medium to high | Good, but more hardware-sensitive | Good on stronger VPSs | Moderate | Highest realism of the local options listed here | Stronger fit for cloning-style workflows | Heaviest of the group | Premium-sounding narration or expressive branded voice work |

Notes:

- Placeholder mode is not a real TTS provider. It exists to keep the video
  workflow runnable when audio synthesis is unavailable.
- Piper is the safest lightweight local engine when the main requirement is
  reliability and low resource usage.
- Kokoro is the best balance of setup size and narration quality for a first
  non-ElevenLabs integration.
- Chatterbox is the most ambitious option here. It is the most likely to need
  GPU, memory, and packaging attention, but it is also the strongest candidate
  when voice character and realism matter more than simplicity.

## Where Selection Should Route

The future provider split should happen inside `helpers/transcribe.py`, because
that file already owns the audio generation step that feeds the rest of the
pipeline.

Recommended routing shape:

1. Resolve the requested provider from CLI and/or environment.
2. Select a provider-specific backend implementation.
3. Generate or reuse the audio file for the current video.
4. Write the transcript JSON in the same shape the rest of the workflow expects.
5. Preserve the existing placeholder fallback path as the default when no real
   provider is configured.

That keeps the downstream render and demo wrappers unchanged.

## Future CLI Pattern

Use one explicit provider flag and keep the placeholder default available:

```bash
--tts-provider placeholder
--tts-provider kokoro
--tts-provider chatterbox
--tts-provider piper
```

Current repo support now covers:

```bash
--tts-provider placeholder
--tts-provider elevenlabs
```

Recommended semantics:

- `placeholder` keeps the current local smoke-test behavior.
- `piper` prioritizes light footprint and low setup risk.
- `kokoro` is the first real local provider worth wiring in for TravelBuddy.
- `chatterbox` is the later premium option once the team wants stronger voice
  realism or cloning-like workflows.

## Next Provider Candidate

**Piper**

Reasoning:

- simplest local install of the realistic options
- low dependency risk compared with the other local engines
- good macOS compatibility for a first pass
- minimal change to the current pipeline because the output contract is simple

Use Piper as the first local provider after placeholder, then evaluate Kokoro
for a higher-quality follow-up once the routing layer is stable.

## Safest First Implementation Path

1. Add `--tts-provider` parsing to `helpers/transcribe.py`.
2. Keep `placeholder` as the default.
3. Keep `elevenlabs` as the only real backend until a local provider lands.
4. Introduce a provider registry or small adapter layer in the transcribe helper.
5. Implement `piper` or `kokoro` first, not both at once.
6. Reuse the existing transcript JSON contract so render code stays untouched.
7. Add one smoke test per provider path once the first backend lands.

## Architecture Recommendation

Keep the transcribe helper as the provider boundary and avoid spreading provider
logic into the demo wrapper or render pipeline. A simple shape is:

- `helpers/transcribe.py` for provider selection and transcript output
- `helpers/transcribe_backends/` for small provider adapters later
- `edit/transcripts/` for the unchanged JSON contract

This makes the migration reversible and keeps the placeholder path available as
the safe fallback while the first real provider is being added.
