"""Caption style metadata for TravelBuddy social exports.

This module is configuration-only. It defines caption look-and-feel hints for
future subtitle rendering work without changing the current pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class CaptionStyle:
    name: str
    font_placeholder: str
    font_size: int
    color_palette: dict[str, str]
    emphasis_color: str
    stroke_shadow_intent: str
    animation_intent: str
    subtitle_positioning: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


CAPTION_STYLES: dict[str, CaptionStyle] = {
    "cinematic_gold": CaptionStyle(
        name="cinematic_gold",
        font_placeholder="Helvetica Neue Bold",
        font_size=54,
        color_palette={
            "primary": "#F9F3E6",
            "secondary": "#E7D7B4",
            "background": "#0F0F0F",
        },
        emphasis_color="#D4AF37",
        stroke_shadow_intent="soft black shadow, light stroke",
        animation_intent="gentle fade and slight rise",
        subtitle_positioning={"anchor": "bottom-center", "margin_v": 120, "max_lines": 2},
    ),
    "breaking_news": CaptionStyle(
        name="breaking_news",
        font_placeholder="Inter Bold",
        font_size=58,
        color_palette={
            "primary": "#FFFFFF",
            "secondary": "#E91C24",
            "background": "#10151C",
        },
        emphasis_color="#FF3B30",
        stroke_shadow_intent="crisp stroke, urgent shadow",
        animation_intent="sharp pop-in with ticker energy",
        subtitle_positioning={"anchor": "bottom-center", "margin_v": 110, "max_lines": 2},
    ),
    "luxury_minimal": CaptionStyle(
        name="luxury_minimal",
        font_placeholder="Avenir Next Demi Bold",
        font_size=48,
        color_palette={
            "primary": "#FCF7F0",
            "secondary": "#C8B69A",
            "background": "#111111",
        },
        emphasis_color="#B79A6A",
        stroke_shadow_intent="thin elegant stroke, subtle depth",
        animation_intent="minimal crossfade",
        subtitle_positioning={"anchor": "lower-third", "margin_v": 130, "max_lines": 2},
    ),
    "mentor_bold": CaptionStyle(
        name="mentor_bold",
        font_placeholder="Helvetica Bold",
        font_size=56,
        color_palette={
            "primary": "#FFFFFF",
            "secondary": "#7ED321",
            "background": "#0D0F11",
        },
        emphasis_color="#7ED321",
        stroke_shadow_intent="strong outline, confident shadow",
        animation_intent="clean assertive build-in",
        subtitle_positioning={"anchor": "mid-lower", "margin_v": 115, "max_lines": 2},
    ),
}


def get_caption_style(name: str) -> CaptionStyle:
    style = CAPTION_STYLES.get(name.strip().lower())
    if style is None:
        raise KeyError(f"unknown caption style: {name}")
    return style

