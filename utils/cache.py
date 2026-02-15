"""
Prompt Cache
============
Hash-based caching for AI agent responses.
Avoids redundant API calls for identical prompts.
"""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path.home() / ".ai-web-builder" / "cache"
CACHE_TTL_HOURS = 24


def _get_cache_key(system_prompt: str, user_prompt: str, model: str) -> str:
    """Generate a deterministic cache key from prompt + model."""
    content = f"{model}::{system_prompt}::{user_prompt}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def get_cached_response(
    system_prompt: str,
    user_prompt: str,
    model: str,
) -> Optional[dict]:
    """
    Retrieve a cached response if it exists and hasn't expired.
    
    Returns:
        dict with 'text', 'model', 'provider' keys, or None if cache miss.
    """
    cache_key = _get_cache_key(system_prompt, user_prompt, model)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text())
        # Check TTL
        age_hours = (time.time() - data.get("timestamp", 0)) / 3600
        if age_hours > CACHE_TTL_HOURS:
            cache_file.unlink(missing_ok=True)
            logger.debug("Cache expired for key %s (%.1fh old)", cache_key, age_hours)
            return None
        logger.info("Cache hit for key %s", cache_key)
        return data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Cache read error for key %s: %s", cache_key, e)
        cache_file.unlink(missing_ok=True)
        return None


def save_to_cache(
    system_prompt: str,
    user_prompt: str,
    model: str,
    response_text: str,
    provider: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
) -> None:
    """Save a response to the cache."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_key = _get_cache_key(system_prompt, user_prompt, model)
        cache_file = CACHE_DIR / f"{cache_key}.json"

        data = {
            "text": response_text,
            "model": model,
            "provider": provider,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost_usd,
            "timestamp": time.time(),
        }
        cache_file.write_text(json.dumps(data, indent=2))
        logger.debug("Cached response for key %s", cache_key)
    except OSError as e:
        logger.warning("Cache write error: %s", e)


def clear_cache() -> int:
    """Clear all cached responses. Returns number of entries cleared."""
    count = 0
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()
            count += 1
    logger.info("Cleared %d cache entries", count)
    return count
