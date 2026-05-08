# TravelBuddy Roadmap

## Current Capabilities

This repo is already a conversation-driven video editing toolkit. The current flow is:

1. Transcribe source video into per-file JSON.
2. Pack transcripts into `takes_packed.md`.
3. Use `timeline_view.py` for targeted visual inspection.
4. Build an EDL.
5. Render per-segment clips, concat them, then apply overlays and subtitles.
6. Save outputs in `<videos_dir>/edit/`.

The important existing surfaces are:

- `README.md` and `poster.html` for first-impression branding.
- `SKILL.md` for operator behavior, editing rules, and workflow UX.
- `install.md` for first-run setup and environment assumptions.
- `helpers/transcribe.py` for audio/transcription input.
- `helpers/render.py` and `helpers/grade.py` for render pipeline and visual style.
- `helpers/timeline_view.py` for visual inspection and cut validation.

## What Should Be Customized For TravelBuddy

### Branding

Best targets:

- `README.md`
- `poster.html`
- `SKILL.md`
- `static/video-use-banner.png`
- `static/timeline-view.svg`

Branding should define:

- product name and positioning
- tone of voice
- color palette
- type system
- subtitle style
- overlay style
- sample outputs and use cases

This should happen before any code changes so the repo reads like TravelBuddy from the first page, not only after rendering.

### Prompts

Best targets:

- `README.md` setup prompt
- `install.md`
- `SKILL.md`

Prompt changes should teach the agent how to work for TravelBuddy:

- what kind of videos TravelBuddy edits
- what to ask first
- what must be preserved
- what style of edit to propose
- what brand values matter

### Audio Engine

Best target:

- `helpers/transcribe.py`

The current audio path is local-first placeholder plus optional Piper. The roadmap should keep that boundary abstracted behind a TravelBuddy-specific provider layer.

Likely options:

- keep placeholder as default and add TravelBuddy-specific fallback behavior
- add a provider abstraction so TravelBuddy can swap engines later
- introduce a real alternate transcription provider when quality and cost are acceptable

### Render Templates

Best targets:

- `helpers/render.py`
- `helpers/grade.py`
- `SKILL.md`

This is where TravelBuddy can define the actual look of the output:

- color grade presets
- subtitle defaults
- typography
- cut pacing defaults
- overlay timing
- output size presets

### Workflow UX

Best targets:

- `SKILL.md`
- `install.md`
- `README.md`
- `PROJECT_BRIEF.md`
- `LOCAL_RUN_GUIDE.md`

Workflow UX should answer:

- how a TravelBuddy session starts
- what the first prompt should be
- what file structure the user should expect
- where outputs land
- what the agent should do automatically versus ask about

### Automation / Wrapper

Likely future targets:

- a TravelBuddy wrapper script or CLI
- a TravelBuddy project template
- optional automation around loading prompts, source folders, and brand defaults

That wrapper should be thin. It should configure defaults and guide usage, not replace the core pipeline.

## Phases

### Phase 1: Branding Only

Goal:
Make the repo read like TravelBuddy without changing runtime behavior.

Scope:

- update `README.md`
- update `poster.html`
- update `SKILL.md` tone and examples
- add TravelBuddy-specific brand guidance
- adjust static banner assets if needed

Deliverable:

- a TravelBuddy-branded repo identity
- consistent terminology and messaging
- a documented style direction for edits

### Phase 2: Real Audio Provider Replacement

Goal:
Remove hard dependence on the current transcription vendor if needed.

Scope:

- add a provider abstraction in `helpers/transcribe.py`
- preserve the current fallback mode
- support a second real transcription backend
- keep transcript JSON shape compatible with `pack_transcripts.py`

Deliverable:

- interchangeable audio/transcription backend
- no change to downstream render flow
- compatibility with current placeholder mode

### Phase 3: Video Workflow Improvements

Goal:
Make the editing process more TravelBuddy-specific and less generic.

Scope:

- refine operator prompts in `SKILL.md`
- add TravelBuddy edit patterns
- tune subtitle style and grade defaults
- add example TravelBuddy EDLs or session templates

Deliverable:

- faster first edit
- better default pacing for TravelBuddy content
- less manual prompt engineering per session

### Phase 4: UI or Automation Wrapper

Goal:
Reduce the number of manual commands needed to start a TravelBuddy session.

Scope:

- thin wrapper CLI or script
- optional preset loader
- folder bootstrap helper
- default prompt injection

Deliverable:

- a single entrypoint for common TravelBuddy workflows
- easier onboarding for non-expert users

### Phase A: Social Media Engine Metadata

Goal:
Add social-ready metadata architecture without changing rendering behavior.

Scope:

- export preset metadata for 9:16 and 16:9 deliverables
- caption style metadata for social subtitle treatment
- script-engine stubs for future content-type routing
- demo wrapper wiring that records the selected metadata in `edit/edl.json`

Deliverable:

- a stable additive layer for future caption/export/script automation
- no change to the core ffmpeg render pipeline
- a clean handoff point for future queue or batch automation

### Phase 5: Deployment Path

Goal:
Define how TravelBuddy is distributed or run for real users.

Possible paths:

- keep it as a local agent workflow
- package it as an internal tool
- wrap it as a hosted service
- integrate with a product-specific dashboard

Deliverable:

- a clear operating model
- defined storage and auth assumptions
- a repeatable install/update path

## Risks and Blockers

- The current workflow is tightly coupled to the agent skill model in `SKILL.md`.
- The render pipeline depends on `ffmpeg` conventions and ordering rules that should not be casually changed.
- Transcript JSON shape is a contract with `pack_transcripts.py` and `render.py`.
- The placeholder audio mode is useful for local runs, but it is not a substitute for a real provider.
- Branding changes can drift into product redesign if they are not separated from behavior changes.
- Social export and caption metadata should stay additive until the first real branded outputs are reviewed.
- Deployment should wait until the local workflow is stable and the branding direction is fixed.

## Safest Next Implementation Task

Create a TravelBuddy brand pack without changing logic:

1. Add a TravelBuddy section to `SKILL.md`.
2. Update `README.md` and `poster.html` to match that brand.
3. Define a TravelBuddy subtitle and grade direction in docs only.

That gives the repo a coherent identity first, while preserving the existing pipeline and keeping the audio/render path unchanged.
