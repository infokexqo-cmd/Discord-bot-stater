"""Basic moderation slash commands (permission-gated)."""

from __future__ import annotations

from datetime import timedelta

import discord
from discord import app_commands
from discord.ext import commands


class Moderation(commands.Cog):
    """Kick, ban, and timeout — each requires the matching Discord permission."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(
        member="The member to kick.",
        reason="Why they're being kicked.",
    )
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
    ) -> None:
        await member.kick(reason=reason)
        await interaction.response.send_message(
            f"Kicked **{member}**." + (f" Reason: {reason}" if reason else ""),
            ephemeral=True,
        )

    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(
        member="The member to ban.",
        reason="Why they're being banned.",
        delete_days="Days of their messages to delete (0-7).",
    )
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.guild_only()
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
        delete_days: app_commands.Range[int, 0, 7] = 0,
    ) -> None:
        await member.ban(reason=reason, delete_message_days=delete_days)
        await interaction.response.send_message(
            f"Banned **{member}**." + (f" Reason: {reason}" if reason else ""),
            ephemeral=True,
        )

    @app_commands.command(name="timeout", description="Time out a member.")
    @app_commands.describe(
        member="The member to time out.",
        minutes="Length in minutes (1 minute – 28 days).",
        reason="Why they're being timed out.",
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.guild_only()
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str | None = None,
    ) -> None:
        await member.timeout(timedelta(minutes=minutes), reason=reason)
        await interaction.response.send_message(
            f"Timed out **{member}** for {minutes} minute(s).",
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
