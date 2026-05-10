"""Seedance 2.0 production payload builder.

This module is configuration-only. It converts the TravelBuddy topic/script
metadata into API-ready JSON without invoking any external service.
"""

from __future__ import annotations

from textwrap import shorten

from helpers.script_engine import normalize_mode


PAYLOAD_STYLE_PROFILES: dict[str, dict[str, str]] = {
    "motivational": {
        "style": "cinematic motivation",
        "camera_direction": "heroic push-in with low-angle momentum",
        "motion_profile": "forward motion, rising reframes, and emotional escalation",
        "visual_energy": "uplifting, emotional, and high momentum",
    },
    "airport_intel": {
        "style": "travel urgency",
        "camera_direction": "fast lateral motion with departure-board emphasis",
        "motion_profile": "quick cuts, operational clarity, and travel urgency",
        "visual_energy": "kinetic, practical, and deadline-driven",
    },
    "luxury": {
        "style": "cinematic luxury lifestyle",
        "camera_direction": "slow glide with premium spacing and controlled parallax",
        "motion_profile": "smooth camera drift, restrained movement, and luxury pacing",
        "visual_energy": "refined, calm, and premium",
    },
    "ai_marketing": {
        "style": "futuristic AI marketing",
        "camera_direction": "layered UI motion with subtle push-ins and digital overlays",
        "motion_profile": "interface-driven motion, data accents, and clean transitions",
        "visual_energy": "tech-forward, intelligent, and electric",
    },
    "breaking_news": {
        "style": "breaking urgency",
        "camera_direction": "zoom cuts, snap reframes, and tension-driven framing",
        "motion_profile": "rapid updates, sharp transitions, and high-tension pacing",
        "visual_energy": "urgent, alert, and high tension",
    },
    "mentor_story": {
        "style": "cinematic documentary",
        "camera_direction": "observational framing with intimate, human storytelling",
        "motion_profile": "natural movement, documentary realism, and patient reveals",
        "visual_energy": "grounded, emotional, and reflective",
    },
}

DEFAULT_STYLE_KEY = "mentor_story"


def _clean_text(value: object, fallback: str = "") -> str:
    text = " ".join(str(value or "").split()).strip()
    return text or fallback


def _infer_mode_key(mode: str | None, generated_script: dict[str, object]) -> str:
    script_mode = generated_script.get("mode")
    normalized = normalize_mode(mode or str(script_mode or ""))
    if normalized is not None:
        return normalized
    return DEFAULT_STYLE_KEY


def _resolve_style_profile(mode_key: str) -> dict[str, str]:
    return PAYLOAD_STYLE_PROFILES.get(mode_key, PAYLOAD_STYLE_PROFILES[DEFAULT_STYLE_KEY])


def build_seedance_payload(
    topic: str,
    generated_script: dict[str, object],
    mode: str | None,
    duration: int,
    resolution: str,
    aspect_ratio: str,
    pacing_profile: str,
    caption_style: str,
    export_preset: str,
) -> dict[str, object]:
    """Return a production-ready Seedance 2.0 handoff payload."""

    mode_key = _infer_mode_key(mode, generated_script)
    style_profile = _resolve_style_profile(mode_key)

    topic_text = _clean_text(
        topic
        or generated_script.get("topic")
        or generated_script.get("headline")
        or generated_script.get("mode_description"),
        fallback="Untitled TravelBuddy idea",
    )
    hook = _clean_text(generated_script.get("hook") or generated_script.get("headline"), fallback=topic_text)
    voice_chunks = [
        _clean_text(chunk)
        for chunk in generated_script.get("voice_chunks", [])
        if _clean_text(chunk)
    ]
    pacing = _clean_text(pacing_profile or generated_script.get("pacing_profile"), fallback="natural")
    creator_mode = _clean_text(generated_script.get("mode") or mode_key, fallback=mode_key)
    content_type = _clean_text(generated_script.get("content_type"), fallback="mentor_pitch")
    mode_description = _clean_text(generated_script.get("mode_description"))
    script_style = _clean_text(generated_script.get("script_style"), fallback=style_profile["style"])
    routing_hint = _clean_text(generated_script.get("routing_hint"))

    prompt_parts = [
        f"Topic: {topic_text}",
        f"Hook: {hook}",
        f"Narration beats: {' | '.join(voice_chunks)}" if voice_chunks else None,
        f"Pacing: {pacing}",
        f"Creator mode: {creator_mode}",
        f"Content type: {content_type}",
        f"Mode description: {mode_description}" if mode_description else None,
        f"Routing hint: {routing_hint}" if routing_hint else None,
        f"Style direction: {style_profile['style']}",
        f"Camera direction: {style_profile['camera_direction']}",
        f"Motion profile: {style_profile['motion_profile']}",
        f"Visual energy: {style_profile['visual_energy']}",
        f"Caption style: {caption_style}",
        f"Export preset: {export_preset}",
        f"Script style: {script_style}",
    ]
    prompt = shorten(" ".join(part for part in prompt_parts if part), width=3000, placeholder="")

    return {
        "model": "seedance_2_0",
        "generation_mode": "production",
        "topic": topic_text,
        "prompt": prompt,
        "duration_seconds": int(duration),
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "style": style_profile["style"],
        "camera_direction": style_profile["camera_direction"],
        "motion_profile": style_profile["motion_profile"],
        "visual_energy": style_profile["visual_energy"],
        "caption_style": caption_style,
        "branding": {
            "watermark": True,
            "endcard": True,
        },
        "output_intent": "social_video",
        "mode": creator_mode,
        "pacing_profile": pacing,
        "export_preset": export_preset,
        "content_type": content_type,
        "script_style": script_style,
        "voice_chunks": voice_chunks,
    }
