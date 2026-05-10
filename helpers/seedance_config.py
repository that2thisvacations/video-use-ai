"""Production Seedance 2.0 generation configuration.

This module is configuration-only. It validates requested generation settings
and returns a structured profile that can be threaded through CLI metadata
without touching the local render pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict


SUPPORTED_DURATIONS: tuple[int, ...] = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
SUPPORTED_RESOLUTIONS: tuple[str, ...] = ("480p", "720p", "1080p")
SUPPORTED_ASPECT_RATIOS: tuple[str, ...] = ("1:1", "9:16", "16:9", "3:4", "4:3")

DEFAULT_DURATION_SECONDS = 10
DEFAULT_RESOLUTION = "1080p"
DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_MODEL = "seedance_2_0"
DEFAULT_GENERATION_MODE = "production"
DEFAULT_OUTPUT_INTENT = "social_video"


@dataclass(frozen=True)
class SeedanceGenerationProfile:
    duration_seconds: int
    resolution: str
    aspect_ratio: str
    model: str = DEFAULT_MODEL
    generation_mode: str = DEFAULT_GENERATION_MODE
    output_intent: str = DEFAULT_OUTPUT_INTENT

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def validate_duration(value: int | str) -> int:
    duration = int(value)
    if duration not in SUPPORTED_DURATIONS:
        raise ValueError(
            f"unsupported duration: {duration}. "
            f"Supported durations: {', '.join(str(item) for item in SUPPORTED_DURATIONS)}"
        )
    return duration


def validate_resolution(value: str) -> str:
    resolution = str(value).strip().lower()
    if resolution not in SUPPORTED_RESOLUTIONS:
        raise ValueError(
            f"unsupported resolution: {value}. "
            f"Supported resolutions: {', '.join(SUPPORTED_RESOLUTIONS)}"
        )
    return resolution


def validate_aspect_ratio(value: str) -> str:
    aspect_ratio = str(value).strip()
    if aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        raise ValueError(
            f"unsupported aspect ratio: {value}. "
            f"Supported aspect ratios: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
        )
    return aspect_ratio


def get_seedance_generation_profile(
    duration_seconds: int | str = DEFAULT_DURATION_SECONDS,
    resolution: str = DEFAULT_RESOLUTION,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
) -> SeedanceGenerationProfile:
    return SeedanceGenerationProfile(
        duration_seconds=validate_duration(duration_seconds),
        resolution=validate_resolution(resolution),
        aspect_ratio=validate_aspect_ratio(aspect_ratio),
    )
