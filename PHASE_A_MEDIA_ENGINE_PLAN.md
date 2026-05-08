# Phase A Media Engine Plan

Phase A adds metadata architecture for social-ready output without changing the
stable render pipeline.

## Social Export Roadmap

The export preset layer defines future output targets such as:

- 9:16 cinematic edits for short-form social platforms
- 16:9 cinematic edits for horizontal deliverables
- breaking-news vertical outputs
- luxury vertical outputs

For now, presets are metadata only. They record aspect ratio, resolution, safe
zones, and output suffixes so future rendering hooks can consume them later.

## Subtitle Roadmap

Caption styles define the future subtitle look-and-feel:

- font placeholder
- font sizing
- palette and emphasis colors
- stroke and shadow intent
- animation intent
- subtitle positioning intent

No caption animation implementation is added yet. The current pipeline remains
unchanged.

## AI Scripting Roadmap

The script engine stub introduces content-type routing for future script
generation.

Target content categories:

- `ai_news`
- `travel_lifestyle`
- `mentor_pitch`
- `luxury_travel`
- `breaking_news`
- `airport_intel`

This is only a routing boundary. It does not call any AI API and does not
change transcripts, EDL structure, or render behavior.

## Future Automation API Vision

The long-term shape is a thin orchestration API that can:

- choose export presets by platform
- choose caption styles by brand or content type
- request script drafts for a selected topic
- enqueue batches of jobs for multiple source videos
- write all selected metadata into the edit JSON for reproducibility

The API should stay additive and should not replace the helper scripts.

## Queue and Batch Direction

Future batch automation should likely:

- ingest a folder of clips
- select export presets per target platform
- attach caption style metadata per brand
- route content types through script generation stubs
- fan out rendering jobs with a queue or worker model

The safest version is a local queue first, with no remote orchestration.

## Safest Implementation Order

1. Keep preset/style/script modules as metadata only.
2. Record chosen metadata in `edit/edl.json`.
3. Use the metadata to drive documentation and operator prompts.
4. Add one real export behavior at a time, starting with `cinematic_916`.
5. Add subtitle rendering presets only after reviewing real outputs.
6. Add AI script generation last, behind an explicit content-type route.

## Phase B Verification Note

The first real preset behavior now exists for `cinematic_916`:

- the demo still generates the stable `preview.mp4`
- the branded 16:9 export remains `preview_branded.mp4`
- the new vertical export is `preview_branded_916.mp4`
- the vertical output is 1080x1920 and uses a center-crop strategy

Other presets remain metadata-only until they are intentionally implemented.
