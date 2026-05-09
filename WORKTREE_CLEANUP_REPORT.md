# Worktree Cleanup Report

## Summary

The repository was not in a normal content-dirty state. `git status` showed the
entire tracked tree staged for deletion, while the same paths also existed as
untracked files in the working tree. This is an index-state problem, not a
source edit problem.

I restored the index from `HEAD` with:

```bash
git reset --mixed HEAD
```

That reset cleared the staged deletions without touching the working files.
After that, the worktree returned to a clean state.

## Exact Dirty Files

These were the paths reported as deleted/staged and also present as untracked:

```text
.env.example
.gitignore
BRANDING_INTEGRATION.md
DEMO_WORKFLOW.md
FIRST_REAL_RENDER_REVIEW.md
LOCAL_RUN_GUIDE.md
LOCAL_TTS_PLAN.md
PAUSE_PROFILE_COMPARISON.md
PHASE_A_MEDIA_ENGINE_PLAN.md
PIPER_INTEGRATION_GUIDE.md
PIPER_LOCAL_VALIDATION.md
POST_CHUNKING_RENDER_REVIEW.md
POST_PHRASING_RENDER_REVIEW.md
PROJECT_BRIEF.md
README.md
REAL_CLIP_BRANDING_NOTES.md
SCRIPT_PHRASING_IMPROVEMENTS.md
SKILL.md
TRAVELBUDDY_BRANDING_PLAN.md
TRAVELBUDDY_ROADMAP.md
branding/README.md
branding/assets/README.md
branding/assets/alternates/README.md
branding/assets/alternates/travelbuddy_circle_founder_stop_mark.png
branding/assets/alternates/travelbuddy_footer.png
branding/assets/alternates/travelbuddy_oneline.png
branding/assets/endcards/README.md
branding/assets/endcards/travelbuddy_luxury_endcard.png
branding/assets/fonts/README.md
branding/assets/watermarks/README.md
branding/assets/watermarks/travelbuddy_circle_founder_mark.png
branding/assets/watermarks/travelbuddy_lion_watermark.png
helpers/caption_styles.py
helpers/export_presets.py
helpers/grade.py
helpers/pack_transcripts.py
helpers/render.py
helpers/script_engine.py
helpers/timeline_view.py
helpers/transcribe.py
helpers/transcribe_batch.py
helpers/tts_providers/__init__.py
helpers/tts_providers/piper.py
helpers/tts_providers/placeholder.py
install.md
poster.html
pyproject.toml
skills/manim-video/README.md
skills/manim-video/SKILL.md
skills/manim-video/references/animation-design-thinking.md
skills/manim-video/references/animations.md
skills/manim-video/references/camera-and-3d.md
skills/manim-video/references/decorations.md
skills/manim-video/references/equations.md
skills/manim-video/references/graphs-and-data.md
skills/manim-video/references/mobjects.md
skills/manim-video/references/paper-explainer.md
skills/manim-video/references/production-quality.md
skills/manim-video/references/rendering.md
skills/manim-video/references/scene-planning.md
skills/manim-video/references/troubleshooting.md
skills/manim-video/references/updaters-and-trackers.md
skills/manim-video/references/visual-design.md
skills/manim-video/scripts/setup.sh
static/timeline-view.svg
static/video-use-banner.png
travelbuddy_demo.py
```

## Likely Cause

The pattern matches a broad index corruption or a bulk index operation that
removed tracked entries from the index while leaving the files on disk.

This does not look like:

- generated media or model output
- line-ending noise
- file mode noise

It does look like:

- staged deletions for the entire repository
- untracked reintroduced copies of the same tracked paths

## Safe Cleanup Recommendation

Restore the index from `HEAD` without touching the working tree:

```bash
git reset --mixed HEAD
```

That is the safest fix when the working files are still present and there is no
intentional local source edit to preserve.

## What Should Be Committed, Ignored, Restored, or Deleted

- Commit: nothing from this incident.
- Ignore: no `.gitignore` changes were needed.
- Restore: the full tracked tree should be restored in the index from `HEAD`.
- Delete: nothing. There were no clearly disposable generated media or model
  files involved in this inconsistency.

## Final State

After the mixed reset, `git status --short --branch` is clean:

```text
## main...origin/main
```
