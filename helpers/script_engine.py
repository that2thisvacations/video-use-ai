"""Future-facing TravelBuddy script generation hooks.

This module is intentionally lightweight. It does not call any LLM or AI API.
It generates deterministic topic-to-script structures that can later be
replaced with a real content model without changing the calling contract.
"""

from __future__ import annotations

from textwrap import shorten


CONTENT_TYPES = (
    "ai_news",
    "travel_lifestyle",
    "mentor_pitch",
    "luxury_travel",
    "breaking_news",
    "airport_intel",
)


SCRIPT_ROUTING_HINTS = {
    "ai_news": "brief factual update with clear source framing",
    "travel_lifestyle": "lifestyle story arc with destination-forward pacing",
    "mentor_pitch": "direct advisory opener with practical next steps",
    "luxury_travel": "premium atmosphere, refinement, and service tone",
    "breaking_news": "urgent headline-first structure",
    "airport_intel": "logistical update with concise operational detail",
}

SCRIPT_TEMPLATES = {
    "mentor_pitch": {
        "headline": "{topic}",
        "hook": "If you keep waiting for permission, you are choosing delay.",
        "main_points": [
            "Start with one clear problem.",
            "Build the smallest useful version today.",
            "Publish before you feel ready.",
        ],
        "cta": "Pick one idea and ship the first draft tonight.",
    },
    "ai_news": {
        "headline": "AI update: {topic}",
        "hook": "Here is the part that matters for builders.",
        "main_points": [
            "What changed.",
            "Why it matters.",
            "What to watch next.",
        ],
        "cta": "Follow for the next practical breakdown.",
    },
    "luxury_travel": {
        "headline": "Luxury travel note: {topic}",
        "hook": "The best trips feel effortless because they are planned well.",
        "main_points": [
            "Where the experience feels elevated.",
            "What makes the pacing calm.",
            "Why the details matter.",
        ],
        "cta": "Save this for the next premium itinerary.",
    },
    "breaking_news": {
        "headline": "Breaking: {topic}",
        "hook": "This is the one-sentence version before the details land.",
        "main_points": [
            "What happened.",
            "Who it affects.",
            "What happens next.",
        ],
        "cta": "Stay tuned for the next update.",
    },
    "airport_intel": {
        "headline": "Airport intel: {topic}",
        "hook": "Keep the trip moving by focusing on the operational details.",
        "main_points": [
            "Best timing.",
            "Useful logistics.",
            "What to avoid.",
        ],
        "cta": "Share this with the person handling the itinerary.",
    },
    "travel_lifestyle": {
        "headline": "Travel lifestyle: {topic}",
        "hook": "The story lands better when it feels lived-in.",
        "main_points": [
            "The atmosphere.",
            "The habit that improves the trip.",
            "The emotional payoff.",
        ],
        "cta": "Use this as the hook for the next reel.",
    },
}


SUGGESTED_PAUSE_MS = 220


def normalize_content_type(content_type: str) -> str:
    content_key = content_type.strip().lower()
    if content_key not in CONTENT_TYPES:
        return "mentor_pitch"
    return content_key


def normalize_topic(topic: str) -> str:
    value = " ".join(topic.strip().split())
    return value or "Untitled idea"


def get_routing_hint(content_type: str) -> str:
    content_key = normalize_content_type(content_type)
    return SCRIPT_ROUTING_HINTS[content_key]


def build_voice_chunks(
    headline: str,
    hook: str,
    main_points: list[str],
    cta: str,
) -> list[str]:
    chunks = [headline.strip(), hook.strip(), *[point.strip() for point in main_points], cta.strip()]
    return [chunk for chunk in chunks if chunk]


def build_caption_groups(
    headline: str,
    hook: str,
    main_points: list[str],
    cta: str,
) -> list[str]:
    groups: list[str] = []
    intro = " ".join(part for part in [headline.strip(), hook.strip()] if part)
    if intro:
        groups.append(intro)

    points = [point.strip() for point in main_points if point.strip()]
    if points:
        if len(points) == 1:
            groups.append(points[0])
        elif len(points) == 2:
            groups.append(" ".join(points))
        else:
            groups.append(" ".join(points[:2]))
            tail = " ".join(points[2:])
            if tail:
                groups.append(tail)

    cta_text = cta.strip()
    if cta_text:
        groups.append(cta_text)

    return [group for group in groups if group]


def join_voice_chunks(chunks: list[str]) -> str:
    normalized = [chunk.strip().rstrip(".!?") for chunk in chunks if chunk and chunk.strip()]
    if not normalized:
        return ""
    return ". ".join(normalized).strip()


def generate_script_stub(
    topic: str,
    content_type: str,
    *,
    brand: str = "TRAVELBUDDY",
    export_preset: str = "cinematic_916",
    caption_style: str = "cinematic_gold",
) -> dict[str, object]:
    content_key = normalize_content_type(content_type)
    topic_text = normalize_topic(topic)
    template = SCRIPT_TEMPLATES[content_key]
    headline = template["headline"].format(topic=topic_text)
    hook = template["hook"]
    main_points = [point.format(topic=topic_text) for point in template["main_points"]]
    cta = template["cta"]
    voice_chunks = build_voice_chunks(headline, hook, main_points, cta)
    caption_groups = build_caption_groups(headline, hook, main_points, cta)
    voice_text = join_voice_chunks(voice_chunks)
    routing_hint = get_routing_hint(content_key)
    return {
        "brand": brand.strip().upper() or "TRAVELBUDDY",
        "content_type": content_key,
        "topic": topic_text,
        "export_preset": export_preset,
        "caption_style": caption_style,
        "routing_hint": routing_hint,
        "headline": headline,
        "hook": hook,
        "main_points": main_points,
        "cta": cta,
        "voice_chunks": voice_chunks,
        "suggested_pause_ms": SUGGESTED_PAUSE_MS,
        "caption_groups": caption_groups,
        "voice_text": shorten(voice_text, width=1200, placeholder=""),
        "notes": [
            "future LLM call site",
            "keep transcript contract unchanged",
            "route content type into travel-specific script prompts",
            "deterministic voice chunking for social pacing",
            "deterministic template output for local-first workflow",
        ],
    }
