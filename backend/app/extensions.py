import os

from slowapi import Limiter
from slowapi.util import get_remote_address


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    enabled=_env_bool("RATELIMIT_ENABLED", True),
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)
