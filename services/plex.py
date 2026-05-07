from datetime import datetime

import discord

from ..client import client


async def send_plex_embed(event, account, server, metadata):
    BUM_CHANNEL = 1456246678834118860

    poster_url = get_plex_poster(metadata)

    avatar_url = account.get("thumb")
    if avatar_url and not avatar_url.startswith("http"):
        avatar_url = None

    embed = discord.Embed(
        title=metadata["title"],
        description="Finished watching",
        timestamp=datetime.utcnow(),
    )

    if poster_url:
        embed.set_image(url=poster_url)

    if avatar_url:
        embed.set_author(
            name=f"{account.get('title')} finished watching",
            icon_url=avatar_url,
        )

    embed.add_field(
        name="Media type",
        value=metadata.get("librarySectionType", "?"),
        inline=True,
    )

    channel = await client.fetch_channel(BUM_CHANNEL)
    await channel.send(embed=embed)


def get_plex_poster(metadata):
    for img in metadata.get("Image", []):
        if img.get("type") == "coverPoster":
            return "https://metadata-static.plex.tv" + img["url"]
    return None
