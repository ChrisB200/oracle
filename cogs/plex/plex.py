import logging
import math
import re

import discord
from discord.ext import commands

from config.settings import SETTINGS, get_setting, set_setting
from services.alfred import (
    download_media,
    get_magnet_hash,
    get_progress,
    get_storage,
    search_library,
)

from .views import PaginatorView

logger = logging.getLogger(__name__)


class Plex(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.last_results = {}

    @commands.group(invoke_without_command=True)
    async def plex(self, ctx, media_type=None, *, query=""):
        """Scrape and download media for Plex."""
        if media_type is None:
            return await ctx.invoke(ctx.bot.get_command("help"), "plex")

        await self._search(ctx, media_type, query)

    @plex.command()
    async def storage(self, ctx):
        """Shows the storage information on the plex server"""
        try:
            stats = get_storage()
        except Exception:
            logger.exception("Failed to fetch storage from Alfred")
            return await ctx.send("Could not fetch storage from Alfred")

        embed = discord.Embed(title="📊 Storage Info", color=discord.Color.blurple())
        embed.add_field(name="Total", value=stats.get("total", "?"), inline=True)
        embed.add_field(name="Used", value=stats.get("used", "?"), inline=True)
        embed.add_field(name="Free", value=stats.get("free", "?"), inline=True)

        await ctx.send(embed=embed)

    @plex.command(name="help")
    async def plex_help(self, ctx):
        """Show help for Plex commands."""
        embed = discord.Embed(
            title="📺 Plex Commands",
            color=discord.Color.blurple(),
            description="Available subcommands:",
        )

        plex_cmd = ctx.bot.get_command("plex")

        for cmd in plex_cmd.commands:
            aliases = ", ".join(cmd.aliases) if cmd.aliases else "None"
            embed.add_field(
                name=f".plex {cmd.name}",
                value=f"{cmd.help or 'No description'}\nAliases: `{aliases}`",
                inline=False,
            )

        await ctx.send(embed=embed)

    async def _search(self, ctx, media_type: str, series: str):
        commands = get_setting("channels", "commands")
        if commands and int(commands) != ctx.channel.id:
            channel = self.client.get_channel(commands)
            return await ctx.send(
                f"Please use commands in {channel.mention}",
                delete_after=5,
            )

        try:
            rows = search_library(media_type, series)
            logger.info(
                "Searching %s in Alfred for %s by user %s",
                media_type,
                series,
                ctx.author.name,
            )
        except Exception:
            logger.exception("Failed to search for %s", media_type)
            return await ctx.send("Search failed")

        if not rows or rows == []:
            await ctx.send(f"No results found for `{series}`.")
            return

        chunk_size = 10
        pages = []

        for i in range(0, len(rows), chunk_size):
            chunk = rows[i : i + chunk_size]
            description_lines = []

            for j, row in enumerate(chunk, start=i + 1):
                pretty_name = re.sub(r"(1080p|720p|2160p)", r"**\1**", row["name"])
                description_lines.append(
                    f"**{j}.** 🎞️ {pretty_name}\n"
                    f"  💾 `{row['size']}` | 🌱 `{row['seeders']}` seeders"
                )

            embed = discord.Embed(
                title=f"🔍 Results for '{series}'",
                description="\n\n".join(description_lines),
                color=discord.Color.blurple(),
            )
            embed.set_footer(
                text=f"Use .download <number> to begin downloading\nPage {len(pages)+1} / {math.ceil(len(rows)/chunk_size)}"
            )
            pages.append(embed)

        self.last_results[ctx.author.id] = {
            "rows": rows,
            "type": media_type,
        }

        view = PaginatorView(ctx, pages)
        view.message = await ctx.send(embed=pages[0], view=view)

    @plex.command()
    async def download(self, ctx, *, id):
        """Download a result by its number from the last search"""
        user_search = self.last_results.get(ctx.author.id)
        if not user_search:
            return await ctx.send("Must search for a show, movie or anime first")

        last_results = user_search["rows"]
        if not last_results:
            return await ctx.send("Must search for a show, movie or anime first")

        try:
            id = int(id) - 1

            if id > len(last_results) - 1 or id < 0:
                return await ctx.send(f"Must be between 1 and {len(last_results)}")

            result = last_results[id]
            magnet = result.get("magnet")
            media_type = user_search.get("type")
            user_id = ctx.author.id

            download_media(media_type, magnet, user_id, "discord")
        except Exception:
            logger.exception("An error occurred trying to download")
            return await ctx.send("An error has occurred")

        await ctx.send(
            f"Began downloading: {result.get('name')}\n use .plex progress to check its progress"
        )

    @plex.command()
    async def progress(self, ctx):
        """Get the progress of all media currently downloading"""
        try:
            torrents = get_progress()
        except Exception:
            logger.exception("Failed to fetch progress from Alfred")
            return await ctx.send("Could not fetch progress from Alfred")

        if not torrents:
            return await ctx.send("Nothing is currently downloading")

        description_lines = []
        for i, t in enumerate(torrents):
            description_lines.append(f"{i}. {t[0]}: **{round(float(t[1]))}%**")

        embed = discord.Embed(
            title="Download Progress",
            description="\n".join(description_lines),
            color=discord.Color.blurple(),
        )

        await ctx.send(embed=embed)

    @plex.command()
    async def set_downloads(self, ctx, channel: discord.TextChannel):
        set_setting(
            channel.id,
            "channels",
            "downloads",
        )

        await ctx.send(f"Downloads channel set to {channel.mention}")

    @plex.command()
    async def set_commands(self, ctx, channel: discord.TextChannel):
        set_setting(
            channel.id,
            "channels",
            "commands",
        )

        await ctx.send(f"Downloads channel set to {channel.mention}")


async def setup(client):
    await client.add_cog(Plex(client))
