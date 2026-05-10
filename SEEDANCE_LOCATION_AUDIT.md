# Seedance Location Audit

This repository now has more than one Seedance-related surface. Keep them separate until consolidation is explicitly planned.

## 1. video-use-ai local engine

Primary files:
- `travelbuddy_demo.py`
- `helpers/seedance_config.py`
- `helpers/seedance_payload.py`
- `helpers/script_engine.py`
- `README_QUICKSTART.md`
- `PROJECT_BRIEF.md`
- `TRAVELBUDDY_ROADMAP.md`
- `SEEDANCE_PRODUCTION_CONFIG.md`
- `SEEDANCE_PAYLOAD_REFERENCE.md`

What it controls:
- Local TravelBuddy reel orchestration
- Seedance 2.0 production config metadata
- Seedance payload generation for future API handoff
- Local render pipeline, batch manifests, and creator exports

Current behavior:
- Builds `edit/generated_script.json`
- Builds `edit/seedance_payload.json`
- Builds `edit/batch/reel_###/seedance_payload.json`
- Supports `--seedance-payload-only` to skip local rendering

Do not merge this surface with the UI surfaces below yet.

## 2. aistudio VPS loop builder

Current known location:
- `~/Documents/travelbuddy-main/src/pages/LoopBuilderPage.jsx`

Deployment references found in repo metadata:
- container/app name: `aistudio`
- compose path: `/var/www/aistudio/docker-compose.yml`
- public domain: `aistudio.that2thismedia.com`

What it controls:
- The web UI loop builder experience
- Seedance prompt generation language for the production site
- User-facing copy that still contains older "test clip" wording in the live bundle/source

Why it matters:
- This is a separate deployment surface from the local Python engine.
- It likely needs its own copy update, build, and restart path.

## 3. Other Seedance references in this repo

Direct code and docs references currently live in:
- `travelbuddy_demo.py`
- `helpers/seedance_config.py`
- `helpers/seedance_payload.py`
- `SEEDANCE_PRODUCTION_CONFIG.md`
- `SEEDANCE_PAYLOAD_REFERENCE.md`
- `PROJECT_BRIEF.md`
- `README_QUICKSTART.md`
- `TRAVELBUDDY_ROADMAP.md`

These references define:
- supported durations, resolutions, and aspect ratios
- production payload schema
- payload-only generation mode
- batch manifest recording
- creator wrapper behavior

## 4. What each location should own

- `video-use-ai`: local reel generation, deterministic script metadata, and Seedance handoff payloads
- `aistudio`: production web UI copy, button labels, and user-facing generation language

## 5. Warning

Do not merge, refactor, or rename these Seedance surfaces yet.
They are intentionally separate and can diverge in release cadence.

## 6. Future consolidation plan

1. Keep the local Python payload builder as the source of truth for Seedance request schema.
2. Update the aistudio UI copy to production wording independently.
3. Confirm the live bundle and deployment folder for `aistudio.that2thismedia.com`.
4. After both surfaces are stable, extract shared Seedance schema documentation into one canonical spec.
5. Only then consider a shared client library or monorepo-level Seedance contract.
