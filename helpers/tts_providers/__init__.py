"""Provider adapters used by helpers/transcribe.py.

The package stays intentionally small so the current placeholder workflow
remains the default while future local providers can be added one file at a
time.
"""

from __future__ import annotations

PROVIDER_NAMES = ("placeholder", "elevenlabs", "piper")
ACTIVE_PROVIDER_NAMES = ("placeholder", "elevenlabs")
FUTURE_PROVIDER_NAMES = ("piper",)

