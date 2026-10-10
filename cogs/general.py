"""General utility slash commands."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class General(commands.Cog):
    """Everyday info commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! `{latency_ms}ms`")

    @app_commands.command(
        name="serverinfo", description="Show information about this server."
    )
    @app_commands.guild_only()
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        assert guild is not None  # guaranteed by @guild_only
        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Server ID", value=str(guild.id))
        embed.add_field(
            name="Owner", value=str(guild.owner) if guild.owner else "Unknown"
        )
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(
            name="Channels",
            value=f"{len(guild.text_channels)} text · "
            f"{len(guild.voice_channels)} voice",
        )
        embed.add_field(name="Roles", value=str(len(guild.roles)))
        embed.add_field(
            name="Created",
            value=discord.utils.format_dt(guild.created_at, style="D"),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="userinfo", description="Show information about a user."
    )
    @app_commands.describe(user="The user to look up (defaults to you).")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        user: discord.User | None = None,
    ) -> None:
        user = user or interaction.user
        member = interaction.guild.get_member(user.id) if interaction.guild else None

        embed = discord.Embed(title=str(user), color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="User ID", value=str(user.id))
        embed.add_field(
            name="Account created",
            value=discord.utils.format_dt(user.created_at, style="D"),
        )
        if member is not None:
            if member.joined_at:
                embed.add_field(
                    name="Joined server",
                    value=discord.utils.format_dt(member.joined_at, style="D"),
                )
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(
                name=f"Roles ({len(roles)})",
                value=" ".join(roles[:10]) or "None",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
