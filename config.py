"""Environment-based configuration with validation.

All settings come from environment variables (or a local ``.env`` file loaded
via python-dotenv). Anything invalid fails fast with a clear error message
instead of crashing later at runtime.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # no-op if there is no .env file


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    token: str
    prefix: str = "!"
    guild_id: int | None = None  # dev guild for instant slash-command sync
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token or token == "your-bot-token-here":
            raise ConfigError(
                "DISCORD_TOKEN is not set. Copy .env.example to .env and paste "
                "your bot token from https://discord.com/developers/applications"
            )

        prefix = os.getenv("COMMAND_PREFIX", "!").strip() or "!"

        guild_id: int | None = None
        raw_guild = os.getenv("DEV_GUILD_ID", "").strip()
        if raw_guild:
            if not raw_guild.isdigit():
                raise ConfigError(
                    f"DEV_GUILD_ID must be a numeric server ID, got {raw_guild!r}."
                )
            guild_id = int(raw_guild)

        log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ConfigError(
                f"LOG_LEVEL must be one of DEBUG/INFO/WARNING/ERROR/CRITICAL, "
                f"got {log_level!r}."
            )

        return cls(token=token, prefix=prefix, guild_id=guild_id, log_level=log_level)
