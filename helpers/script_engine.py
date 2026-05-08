"""Future-facing TravelBuddy script generation hooks.

This module is intentionally lightweight. It does not call any LLM or AI API.
It only centralizes future route metadata for content-specific script drafts.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


CONTENT_TYPES = (
    "ai_news",
    "travel_lifestyle",
    "mentor_pitch",
    "luxury_travel",
    "breaking_news",
    "airport_intel",
)


@dataclass(frozen=True)
class ScriptStub:
    content_type: str
    brand: str
    export_preset: str
    caption_style: str
    routing_hint: str
    notes: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


SCRIPT_ROUTING_HINTS = {
    "ai_news": "brief factual update with clear source framing",
    "travel_lifestyle": "lifestyle story arc with destination-forward pacing",
    "mentor_pitch": "direct advisory opener with practical next steps",
    "luxury_travel": "premium atmosphere, refinement, and service tone",
    "breaking_news": "urgent headline-first structure",
    "airport_intel": "logistical update with concise operational detail",
}


def generate_script_stub(
    content_type: str,
    *,
    brand: str = "TRAVELBUDDY",
    export_preset: str = "cinematic_916",
    caption_style: str = "cinematic_gold",
) -> ScriptStub:
    content_key = content_type.strip().lower()
    if content_key not in CONTENT_TYPES:
        content_key = "mentor_pitch"
    routing_hint = SCRIPT_ROUTING_HINTS[content_key]
    return ScriptStub(
        content_type=content_key,
        brand=brand.strip().upper() or "TRAVELBUDDY",
        export_preset=export_preset,
        caption_style=caption_style,
        routing_hint=routing_hint,
        notes=[
            "future LLM call site",
            "keep transcript contract unchanged",
            "route content type into travel-specific script prompts",
        ],
    )

