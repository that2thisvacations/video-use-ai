# Piper Integration Guide

Piper is the first local provider candidate because it is the lightest realistic
path that still fits this repo's current pipeline. It is a better first step
than heavier local engines because it keeps dependency risk low, runs well on
macOS, and can be introduced without changing the transcript JSON contract or
the render flow.

## Why Piper First

- low install and packaging risk compared with heavier local TTS systems
- good Mac compatibility for a first local provider pass
- straightforward VPS compatibility when a small local voice model is available
- simple audio output contract that can feed the existing placeholder pipeline
- low likelihood of forcing changes in render or branding code

## Expected Install Options for Mac

Likely installation paths to evaluate later:

1. install through a Python package if the supported wrapper remains lightweight
2. install via Homebrew only if an official formula exists and remains small
3. keep the model files local and managed separately from Python dependencies

The goal is to avoid adding heavy system dependencies before the provider proves
useful in the current pipeline.

## Expected Model File Location

Keep Piper voice/model assets outside the repo by default, for example:

```text
~/Library/Application Support/video-use-ai/piper/
```

or a clearly documented local model folder in the user's workspace. The provider
adapter should read model paths from configuration rather than hardcoding them.

## Expected Future CLI Usage

```bash
python helpers/transcribe.py <video.mp4> --tts-provider piper
```

The demo wrapper can later forward the same flag:

```bash
python travelbuddy_demo.py --brand TRAVELBUDDY --style cinematic --tts-provider piper
```

Do not enable this flag in the runtime path until the provider adapter is
implemented and tested.

## Provider Contract

Piper should follow the same boundary the current providers use:

- input: source video path, edit directory, optional language hint, optional
  speaker hint, and a verbosity flag
- output: transcript JSON written to
  `<edit_dir>/transcripts/<video_stem>.json`
- compatibility: keep the transcript shape unchanged so downstream packing,
  timeline views, and render steps do not need to change

## Known Risks

- model download and packaging size
- voice quality variance across models
- macOS-specific runtime quirks when the wrapper or audio backend changes
- possible latency or memory issues on smaller VPS instances
- the chance that a first pass needs configuration plumbing for model paths and
  voice selection

## Rollback Plan

Rollback should be simple:

1. leave `placeholder` as the default provider
2. keep `elevenlabs` behavior unchanged
3. keep `helpers/tts_providers/piper.py` as a stub until the integration is
   verified
4. if Piper causes issues, stop routing to it and fall back to placeholder mode
5. remove only the Piper adapter code and any provider-specific configuration,
   not the transcript contract or render helpers

