"""Lightweight export preset metadata for TravelBuddy social outputs.

This module is configuration-only. It does not change the render engine.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class ExportPreset:
    name: str
    aspect_ratio: str
    resolution: str
    subtitle_safe_zone: dict[str, float]
    watermark_safe_zone: dict[str, float]
    end_card_safe_zone: dict[str, float]
    output_suffix: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


EXPORT_PRESETS: dict[str, ExportPreset] = {
    "cinematic_916": ExportPreset(
        name="cinematic_916",
        aspect_ratio="9:16",
        resolution="1080x1920",
        subtitle_safe_zone={"x": 0.08, "y": 0.70, "w": 0.84, "h": 0.18},
        watermark_safe_zone={"x": 0.72, "y": 0.74, "w": 0.22, "h": 0.18},
        end_card_safe_zone={"x": 0.00, "y": 0.00, "w": 1.00, "h": 1.00},
        output_suffix="_916_cinematic",
    ),
    "cinematic_169": ExportPreset(
        name="cinematic_169",
        aspect_ratio="16:9",
        resolution="1920x1080",
        subtitle_safe_zone={"x": 0.10, "y": 0.74, "w": 0.80, "h": 0.16},
        watermark_safe_zone={"x": 0.76, "y": 0.76, "w": 0.18, "h": 0.14},
        end_card_safe_zone={"x": 0.00, "y": 0.00, "w": 1.00, "h": 1.00},
        output_suffix="_169_cinematic",
    ),
    "breaking_news_916": ExportPreset(
        name="breaking_news_916",
        aspect_ratio="9:16",
        resolution="1080x1920",
        subtitle_safe_zone={"x": 0.07, "y": 0.66, "w": 0.86, "h": 0.20},
        watermark_safe_zone={"x": 0.70, "y": 0.72, "w": 0.24, "h": 0.18},
        end_card_safe_zone={"x": 0.00, "y": 0.00, "w": 1.00, "h": 1.00},
        output_suffix="_916_breaking",
    ),
    "luxury_916": ExportPreset(
        name="luxury_916",
        aspect_ratio="9:16",
        resolution="1080x1920",
        subtitle_safe_zone={"x": 0.10, "y": 0.72, "w": 0.80, "h": 0.16},
        watermark_safe_zone={"x": 0.74, "y": 0.74, "w": 0.20, "h": 0.16},
        end_card_safe_zone={"x": 0.00, "y": 0.00, "w": 1.00, "h": 1.00},
        output_suffix="_916_luxury",
    ),
}


def get_export_preset(name: str) -> ExportPreset:
    preset = EXPORT_PRESETS.get(name.strip().lower())
    if preset is None:
        raise KeyError(f"unknown export preset: {name}")
    return preset

