import discord

from client import client
from config.settings import get_setting


async def send_dm(user_id: int, message: str):
    user = await client.fetch_user(user_id)
    await user.send(message)


async def send_channel(channel_id: int, message: str):
    channel = await client.fetch_channel(channel_id)
    await channel.send(message)


async def send_download_complete(user_id: int, name: str):
    user = await client.fetch_user(user_id)

    channel_id = get_setting("channels", "downloads")

    if not channel_id:
        return

    channel = client.get_channel(channel_id)

    if not channel:
        channel = await client.fetch_channel(channel_id)

    embed = discord.Embed(
        title="Download Completed",
        description=f"**{name}** has finished downloading",
        color=discord.Color.green(),
    )

    embed.add_field(
        name="Requested By",
        value=user.mention,
        inline=True,
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    embed.set_footer(text=f"User ID: {user.id}")

    await channel.send(embed=embed)
