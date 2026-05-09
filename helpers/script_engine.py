"""Future-facing TravelBuddy script generation hooks.

This module is intentionally lightweight. It does not call any LLM or AI API.
It generates deterministic topic-to-script structures that can later be
replaced with a real content model without changing the calling contract.
"""

from __future__ import annotations

import hashlib
import re
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
        "hook": "You do not need permission. You need a start.",
        "hook_variations": [
            "Stop waiting for permission. Start moving.",
            "You do not need another credential. You need motion.",
            "The delay is the decision.",
        ],
        "main_points": [
            "Pick one clear problem.",
            "Ship the smallest useful version today.",
            "Publish before you feel ready.",
        ],
        "cta": "Pick one idea. Build the first version tonight.",
        "cta_variations": [
            "Pick one idea. Build the first version tonight.",
            "Choose one problem. Ship the first draft today.",
            "Start small. Send the work now.",
        ],
    },
    "ai_news": {
        "headline": "AI update: {topic}",
        "hook": "Here is the part that matters for builders.",
        "hook_variations": [
            "Here is the useful version, not the hype.",
            "This matters if you build with AI.",
            "The signal is in the second-order effect.",
        ],
        "main_points": [
            "What changed.",
            "Why it matters.",
            "What to watch next.",
        ],
        "cta": "Follow for the next practical breakdown.",
        "cta_variations": [
            "Follow for the next practical breakdown.",
            "Save this for the next update.",
            "Stay tuned for the next signal.",
        ],
    },
    "luxury_travel": {
        "headline": "Luxury travel note: {topic}",
        "hook": "The best trips feel effortless because every detail is arranged.",
        "hook_variations": [
            "Luxury feels calm when the planning disappears.",
            "The best trips move with quiet confidence.",
            "The experience should feel smooth from the first step.",
        ],
        "main_points": [
            "Where the experience feels elevated.",
            "What makes the pacing calm.",
            "Why the details matter.",
        ],
        "cta": "Save this for the next premium itinerary.",
        "cta_variations": [
            "Save this for the next premium itinerary.",
            "Use this when the trip needs a cleaner feel.",
            "Keep this for the next luxury route.",
        ],
    },
    "breaking_news": {
        "headline": "Breaking: {topic}",
        "hook": "Here is the clean version before the details land.",
        "hook_variations": [
            "This is the sharp version before the details land.",
            "The headline is moving fast.",
            "Here is the part worth acting on now.",
        ],
        "main_points": [
            "What happened.",
            "Who it affects.",
            "What happens next.",
        ],
        "cta": "Stay tuned for the next update.",
        "cta_variations": [
            "Stay tuned for the next update.",
            "Watch for the next development.",
            "Hold this until the next report lands.",
        ],
    },
    "airport_intel": {
        "headline": "Airport intel: {topic}",
        "hook": "Keep the trip moving by focusing on the operational details.",
        "hook_variations": [
            "The trip goes smoother when the timing is right.",
            "The useful part is in the logistics.",
            "Small details decide whether the day feels easy.",
        ],
        "main_points": [
            "Best timing.",
            "Useful logistics.",
            "What to avoid.",
        ],
        "cta": "Share this with the person handling the itinerary.",
        "cta_variations": [
            "Share this with the person handling the itinerary.",
            "Save this before the airport run.",
            "Keep this handy for the next departure.",
        ],
    },
    "travel_lifestyle": {
        "headline": "Travel lifestyle: {topic}",
        "hook": "The story lands better when it feels lived-in.",
        "hook_variations": [
            "The story lands better when it feels lived-in.",
            "Travel feels richer when the moment feels personal.",
            "The best scenes feel like they already happened to someone you know.",
        ],
        "main_points": [
            "The atmosphere.",
            "The habit that improves the trip.",
            "The emotional payoff.",
        ],
        "cta": "Use this as the hook for the next reel.",
        "cta_variations": [
            "Use this as the hook for the next reel.",
            "Save this for the next travel cut.",
            "Turn this into the next destination post.",
        ],
    },
}

SCRIPT_STYLE_METADATA = {
    "mentor_pitch": {"script_style": "mentor", "suggested_pause_ms": 260, "emphasis_pop_ms": 220},
    "ai_news": {"script_style": "punchy", "suggested_pause_ms": 180, "emphasis_pop_ms": 150},
    "luxury_travel": {"script_style": "luxury", "suggested_pause_ms": 240, "emphasis_pop_ms": 180},
    "breaking_news": {"script_style": "urgent", "suggested_pause_ms": 150, "emphasis_pop_ms": 140},
    "airport_intel": {"script_style": "cinematic", "suggested_pause_ms": 210, "emphasis_pop_ms": 170},
    "travel_lifestyle": {"script_style": "cinematic", "suggested_pause_ms": 230, "emphasis_pop_ms": 190},
}

EMPHASIS_WORD_POOLS = {
    "mentor_pitch": ["mentor", "build", "future", "freedom", "income", "travel"],
    "ai_news": ["ai", "future", "build", "travel", "mentor", "income"],
    "luxury_travel": ["luxury", "travel", "future", "freedom", "build", "income"],
    "breaking_news": ["breaking", "travel", "future", "build", "income", "mentor"],
    "airport_intel": ["travel", "airport", "future", "freedom", "build", "mentor"],
    "travel_lifestyle": ["travel", "future", "freedom", "build", "mentor", "income"],
}

MODE_PROFILES = {
    "motivational": {
        "content_type": "mentor_pitch",
        "mode_description": "motivational builder-first framing",
        "script_style": "mentor",
        "hook_style": "motivational",
        "pacing_profile": "dramatic",
        "chunk_rhythm": "dramatic",
        "hook": "You do not need permission. You need a start.",
        "hook_variations": [
            "Stop waiting for permission. Start moving.",
            "The delay is the decision.",
            "Your next move matters more than your mood.",
        ],
        "main_points": [
            "Pick one clear problem.",
            "Ship the smallest useful version today.",
            "Publish before you feel ready.",
        ],
        "cta": "Start the first version tonight.",
        "cta_variations": [
            "Start the first version tonight.",
            "Pick one idea and build it before bed.",
            "Move first. Refine after.",
        ],
        "emphasis_words": ["mentor", "build", "future", "freedom", "income", "start"],
    },
    "breaking_news": {
        "content_type": "breaking_news",
        "mode_description": "headline-first update framing",
        "script_style": "urgent",
        "hook_style": "headline",
        "pacing_profile": "tight",
        "chunk_rhythm": "tight",
        "hook": "This is the clean version before the details land.",
        "hook_variations": [
            "Here is the headline version first.",
            "This is the part worth acting on now.",
            "The signal is moving fast.",
        ],
        "main_points": [
            "What happened.",
            "Who it affects.",
            "What happens next.",
        ],
        "cta": "Stay tuned for the next update.",
        "cta_variations": [
            "Stay tuned for the next update.",
            "Watch for the next development.",
            "Save this until the next report lands.",
        ],
        "emphasis_words": ["breaking", "travel", "update", "fast", "urgent", "watch"],
    },
    "luxury": {
        "content_type": "luxury_travel",
        "mode_description": "premium travel and service tone",
        "script_style": "luxury",
        "hook_style": "premium",
        "pacing_profile": "natural",
        "chunk_rhythm": "luxury",
        "hook": "Luxury feels calm when every detail is handled.",
        "hook_variations": [
            "Luxury feels calm when the planning disappears.",
            "The best trips move with quiet confidence.",
            "The experience should feel smooth from the first step.",
        ],
        "main_points": [
            "The arrival feels easy.",
            "The service stays quiet and precise.",
            "The whole trip feels lighter.",
        ],
        "cta": "Save this for the next premium itinerary.",
        "cta_variations": [
            "Save this for the next premium itinerary.",
            "Use this when the trip needs a cleaner feel.",
            "Keep this for the next luxury route.",
        ],
        "emphasis_words": ["luxury", "travel", "calm", "service", "premium", "detail"],
    },
    "airport_intel": {
        "content_type": "airport_intel",
        "mode_description": "logistics-first airport advice",
        "script_style": "cinematic",
        "hook_style": "ops",
        "pacing_profile": "tight",
        "chunk_rhythm": "tight",
        "hook": "Keep the trip moving by focusing on the logistics.",
        "hook_variations": [
            "The useful part is in the logistics.",
            "Small details decide whether the day feels easy.",
            "This is the part that saves time at the airport.",
        ],
        "main_points": [
            "Best timing.",
            "Useful logistics.",
            "What to avoid.",
        ],
        "cta": "Keep this handy for the next departure.",
        "cta_variations": [
            "Keep this handy for the next departure.",
            "Share this with the person handling the itinerary.",
            "Save this before the airport run.",
        ],
        "emphasis_words": ["airport", "travel", "time", "gate", "plan", "builder"],
    },
    "ai_marketing": {
        "content_type": "ai_news",
        "mode_description": "practical AI marketing angle",
        "script_style": "punchy",
        "hook_style": "signal",
        "pacing_profile": "tight",
        "chunk_rhythm": "tight",
        "hook": "AI is changing the way marketing gets done.",
        "hook_variations": [
            "This is the useful AI shift for marketers.",
            "The gap between average and useful just widened.",
            "The signal is bigger than the hype.",
        ],
        "main_points": [
            "What is changing.",
            "Why it matters.",
            "What to test next.",
        ],
        "cta": "Follow for the next practical breakdown.",
        "cta_variations": [
            "Follow for the next practical breakdown.",
            "Save this for the next workflow update.",
            "Build the test before the trend cools.",
        ],
        "emphasis_words": ["ai", "marketing", "future", "build", "income", "travel"],
    },
    "mentor_story": {
        "content_type": "mentor_pitch",
        "mode_description": "story-led mentor framing",
        "script_style": "mentor",
        "hook_style": "story",
        "pacing_profile": "natural",
        "chunk_rhythm": "mentor",
        "hook": "The best mentor stories sound simple after the fact.",
        "hook_variations": [
            "This is what the turning point actually sounds like.",
            "A good story makes the next step obvious.",
            "The lesson lands when the story feels lived-in.",
        ],
        "main_points": [
            "What changed first.",
            "What the lesson cost.",
            "What finally worked.",
        ],
        "cta": "Use this frame for the next story-led reel.",
        "cta_variations": [
            "Use this frame for the next story-led reel.",
            "Save this for a softer, trust-building post.",
            "Turn this into the next founder story.",
        ],
        "emphasis_words": ["mentor", "story", "future", "build", "freedom", "income"],
    },
}

MODE_CHOICES = tuple(MODE_PROFILES.keys())

EMPHASIS_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "your",
    "this",
    "that",
    "from",
    "into",
    "about",
    "stop",
    "start",
    "apply",
    "applying",
    "build",
    "building",
}


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


def get_script_style(content_type: str) -> str:
    content_key = normalize_content_type(content_type)
    return SCRIPT_STYLE_METADATA[content_key]["script_style"]


def get_suggested_pause_ms(content_type: str) -> int:
    content_key = normalize_content_type(content_type)
    return int(SCRIPT_STYLE_METADATA[content_key]["suggested_pause_ms"])


def get_emphasis_pop_ms(content_type: str) -> int:
    content_key = normalize_content_type(content_type)
    return int(SCRIPT_STYLE_METADATA[content_key]["emphasis_pop_ms"])


def normalize_mode(mode: str | None) -> str | None:
    if mode is None:
        return None
    cleaned = mode.strip().lower()
    if cleaned in MODE_PROFILES:
        return cleaned
    return None


def get_mode_profile(mode: str | None) -> dict[str, object] | None:
    mode_key = normalize_mode(mode)
    if mode_key is None:
        return None
    return MODE_PROFILES[mode_key]


def extract_topic_keywords(topic: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9']+", topic.lower())
    keywords: list[str] = []
    for token in tokens:
        cleaned = token.strip("'")
        if len(cleaned) < 4 or cleaned in EMPHASIS_STOPWORDS:
            continue
        if cleaned not in keywords:
            keywords.append(cleaned)
    return keywords


def build_emphasis_words(topic: str, content_type: str, mode_profile: dict[str, object] | None = None) -> list[str]:
    content_key = normalize_content_type(content_type)
    emphasis_words: list[str] = []
    if mode_profile is not None:
        for candidate in mode_profile.get("emphasis_words", []):
            cleaned = str(candidate).strip().lower()
            if cleaned and cleaned not in emphasis_words:
                emphasis_words.append(cleaned)
    for candidate in EMPHASIS_WORD_POOLS.get(content_key, []):
        cleaned = candidate.strip().lower()
        if cleaned and cleaned not in emphasis_words:
            emphasis_words.append(cleaned)

    for candidate in extract_topic_keywords(topic):
        if candidate not in emphasis_words:
            emphasis_words.append(candidate)

    if not emphasis_words:
        emphasis_words = ["travel", "future", "build"]
    return emphasis_words[:8]


def stable_choice(options: list[str], *parts: str) -> str:
    clean_options = [option for option in options if option.strip()]
    if not clean_options:
        return ""
    digest = hashlib.sha1("||".join(parts).encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(clean_options)
    return clean_options[index]


def split_paced_phrases(text: str, rhythm: str = "natural") -> list[str]:
    normalized = " ".join(text.strip().split())
    if not normalized:
        return []

    segments: list[str] = []
    current = []
    for char in normalized:
        if char in ",;:—-":
            segment = "".join(current).strip()
            if segment:
                segments.append(segment.rstrip(".!?"))
            current = []
            continue
        current.append(char)

    tail = "".join(current).strip()
    if tail:
        segments.append(tail.rstrip(".!?"))

    if not segments:
        return [normalized.rstrip(".!?")]

    rhythm_key = (rhythm or "natural").strip().lower()
    split_sizes = {
        "tight": 4,
        "natural": 5,
        "dramatic": 8,
        "luxury": 7,
        "mentor": 6,
    }
    target_size = split_sizes.get(rhythm_key, 5)

    result: list[str] = []
    for segment in segments:
        words = segment.split()
        if len(words) <= target_size:
            result.append(segment)
            continue
        if rhythm_key == "tight":
            for index in range(0, len(words), target_size):
                piece = " ".join(words[index : index + target_size]).strip()
                if piece:
                    result.append(piece)
            continue
        if rhythm_key == "dramatic":
            split_at = max(1, int(round(len(words) * 0.68)))
        elif rhythm_key == "luxury":
            split_at = max(1, int(round(len(words) * 0.60)))
        elif rhythm_key == "mentor":
            split_at = max(1, int(round(len(words) * 0.58)))
        else:
            split_at = max(1, len(words) // 2)
        first = " ".join(words[:split_at]).strip()
        second = " ".join(words[split_at:]).strip()
        if first:
            result.append(first)
        if second:
            result.append(second)
    return [piece for piece in result if piece]


def build_voice_chunks(
    headline: str,
    hook: str,
    main_points: list[str],
    cta: str,
    rhythm: str = "natural",
) -> list[str]:
    chunks: list[str] = []
    if headline.strip():
        chunks.append(headline.strip())
    chunks.extend(split_paced_phrases(hook, rhythm=rhythm))
    for point in main_points:
        chunks.extend(split_paced_phrases(point, rhythm=rhythm))
    chunks.extend(split_paced_phrases(cta, rhythm=rhythm))
    return [chunk for chunk in chunks if chunk]


def build_caption_groups(
    voice_chunks: list[str],
) -> list[str]:
    if not voice_chunks:
        return []

    groups: list[str] = []
    index = 0
    total = len(voice_chunks)
    while index < total:
        remaining = total - index
        if index == 0 and remaining >= 2:
            groups.append(" ".join(voice_chunks[index : index + 2]))
            index += 2
            continue
        if remaining >= 3 and len(voice_chunks[index].split()) <= 3:
            groups.append(" ".join(voice_chunks[index : index + 3]))
            index += 3
            continue
        groups.append(voice_chunks[index])
        index += 1

    cleaned = [" ".join(group.split()) for group in groups if group.strip()]
    return cleaned


def join_voice_chunks(chunks: list[str]) -> str:
    normalized = [chunk.strip().rstrip(".!?") for chunk in chunks if chunk and chunk.strip()]
    if not normalized:
        return ""
    return ". ".join(normalized).strip()


def generate_script_stub(
    topic: str,
    content_type: str,
    *,
    mode: str | None = None,
    brand: str = "TRAVELBUDDY",
    export_preset: str = "cinematic_916",
    caption_style: str = "cinematic_gold",
) -> dict[str, object]:
    mode_key = normalize_mode(mode)
    mode_profile = MODE_PROFILES.get(mode_key) if mode_key is not None else None
    content_key = normalize_content_type(content_type)
    if mode_profile is not None:
        content_key = normalize_content_type(str(mode_profile.get("content_type", content_key)))
    topic_text = normalize_topic(topic)
    template = SCRIPT_TEMPLATES[content_key]
    profile_template = mode_profile or {}
    headline_template = str(profile_template.get("headline", template["headline"]))
    headline = headline_template.format(topic=topic_text)
    hook_pool = [
        str(profile_template.get("hook", template["hook"])),
        *[str(item) for item in profile_template.get("hook_variations", template.get("hook_variations", []))],
    ]
    hook = stable_choice(hook_pool, topic_text, content_key, mode_key or content_key, "hook")
    main_points_template = [str(point) for point in profile_template.get("main_points", template["main_points"])]
    main_points = [point.format(topic=topic_text) for point in main_points_template]
    cta_pool = [
        str(profile_template.get("cta", template["cta"])),
        *[str(item) for item in profile_template.get("cta_variations", template.get("cta_variations", []))],
    ]
    cta = stable_choice(cta_pool, topic_text, content_key, mode_key or content_key, "cta")
    rhythm = str(profile_template.get("chunk_rhythm", "natural"))
    voice_chunks = build_voice_chunks(headline, hook, main_points, cta, rhythm=rhythm)
    caption_groups = build_caption_groups(voice_chunks)
    voice_text = join_voice_chunks(voice_chunks)
    routing_hint = get_routing_hint(content_key)
    style_meta = SCRIPT_STYLE_METADATA[content_key]
    script_style = str(profile_template.get("script_style", style_meta["script_style"]))
    emphasis_words = build_emphasis_words(topic_text, content_key, mode_profile)
    mode_description = str(profile_template.get("mode_description", "")) if mode_profile is not None else ""
    hook_style = str(profile_template.get("hook_style", content_key.replace("_", "-")))
    pacing_profile = str(profile_template.get("pacing_profile", "natural"))
    return {
        "brand": brand.strip().upper() or "TRAVELBUDDY",
        "mode": mode_key,
        "mode_description": mode_description,
        "content_type": content_key,
        "topic": topic_text,
        "export_preset": export_preset,
        "caption_style": caption_style,
        "script_style": script_style,
        "hook_style": hook_style,
        "pacing_profile": pacing_profile,
        "routing_hint": routing_hint,
        "emphasis_pop_ms": style_meta["emphasis_pop_ms"],
        "headline": headline,
        "hook": hook,
        "main_points": main_points,
        "cta": cta,
        "voice_chunks": voice_chunks,
        "suggested_pause_ms": style_meta["suggested_pause_ms"],
        "caption_groups": caption_groups,
        "emphasis_words": emphasis_words,
        "voice_text": shorten(voice_text, width=1200, placeholder=""),
        "notes": [
            "future LLM call site",
            "keep transcript contract unchanged",
            "route content type into travel-specific script prompts",
            "deterministic voice chunking for social pacing",
            "deterministic emphasis words for caption highlighting",
            "deterministic emphasis pop timing for cinematic_gold",
            "deterministic template output for local-first workflow",
        ],
    }
