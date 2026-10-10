"""discord-bot-starter — a minimal, production-ready discord.py bot template."""

from __future__ import annotations

import logging
import sys

import discord
from discord import app_commands
from discord.ext import commands

from config import Config, ConfigError

log = logging.getLogger("discord-bot-starter")

# Dotted paths of cogs loaded on startup. Add your own here.
INITIAL_COGS = (
    "cogs.general",
    "cogs.moderation",
)


class StarterBot(commands.Bot):
    """Bot subclass with cog loading, slash-command sync, and error handling."""

    def __init__(self, config: Config) -> None:
        intents = discord.Intents.default()
        intents.members = True  # needed for /userinfo and moderation commands
        super().__init__(command_prefix=config.prefix, intents=intents)
        self.config = config
        # Route slash-command errors to our handler below.
        self.tree.on_error = self.on_app_command_error

    async def setup_hook(self) -> None:
        for name in INITIAL_COGS:
            try:
                await self.load_extension(name)
            except Exception:
                log.exception("Failed to load cog %s", name)
            else:
                log.info("Loaded cog: %s", name)

        # Sync slash commands. A dev-guild ID gives instant updates;
        # global sync can take up to an hour to propagate to all servers.
        if self.config.guild_id:
            guild = discord.Object(id=self.config.guild_id)
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            log.info(
                "Synced %d command(s) to dev guild %s",
                len(synced),
                self.config.guild_id,
            )
        else:
            synced = await self.tree.sync()
            log.info("Synced %d global command(s)", len(synced))

    async def on_ready(self) -> None:
        assert self.user is not None
        log.info("Logged in as %s (id=%s)", self.user, self.user.id)

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        # Prefix commands are legacy here; slash commands are primary.
        if isinstance(error, commands.CommandNotFound):
            return
        log.error("Prefix command error in %s: %s", ctx.command, error, exc_info=error)

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        """Friendly, ephemeral error replies for slash commands."""
        if isinstance(error, app_commands.CommandOnCooldown):
            message = (
                "This command is on cooldown. "
                f"Try again in {error.retry_after:.1f}s."
            )
        elif isinstance(error, app_commands.MissingPermissions):
            message = "You don't have permission to use this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            missing = ", ".join(error.missing_permissions)
            message = f"I'm missing these permissions: {missing}"
        elif isinstance(error, discord.Forbidden):
            message = (
                "I can't do that — check that my role is above the target "
                "member and that I have the right permissions."
            )
        elif isinstance(error, app_commands.CheckFailure):
            message = "You can't use this command here."
        else:
            log.error("Slash command error: %s", error, exc_info=error)
            message = "Something went wrong running that command."

        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            log.warning("Could not send error reply", exc_info=True)


def main() -> int:
    try:
        config = Config.from_env()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Keep discord.py's own logs quiet; ours are enough.
    logging.getLogger("discord").setLevel(logging.WARNING)

    bot = StarterBot(config)
    try:
        # log_handler=None: we already configured logging above.
        bot.run(config.token, log_handler=None)
    except discord.LoginFailure:
        log.error("Login failed: the DISCORD_TOKEN is invalid.")
        return 1
    except KeyboardInterrupt:
        log.info("Shutting down.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
