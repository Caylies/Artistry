from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, cast

import discord

from bd_models.models import Ball

from ...models import ArtistrySettings
from .enums import ArtType
from .utils import format_ball_filename

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def _fetch_threads(channel: discord.ForumChannel) -> set[discord.Thread]:
    existing_threads = {thread for thread in channel.threads}
    archived_threads = {thread async for thread in channel.archived_threads(limit=None)}

    return existing_threads | archived_threads


async def fetch_threads_from_art_channel(bot: "BallsDexBot", art_type: ArtType, settings: ArtistrySettings):
    channel = cast(discord.ForumChannel, await bot.fetch_channel(art_type.get_channel_id(settings)))
    return await _fetch_threads(channel)


async def update_ball_thread(bot: "BallsDexBot", art_type: ArtType, thread: discord.Thread, ball: Ball | None = None):
    message = await thread.fetch_message(thread.id)

    ball = ball or await Ball.objects.aget(country=thread.name)
    art_attribute = getattr(ball, art_type.attribute)

    if art_type == ArtType.Emoji:
        emoji = bot.get_emoji(art_attribute)

        if emoji is None:
            return

        await message.edit(
            attachments=[
                discord.File(
                    BytesIO(await emoji.read()),
                    filename=format_ball_filename(ball.country, ".gif" if emoji.animated else ".png"),
                )
            ]
        )
        return

    await message.edit(
        attachments=[
            discord.File(
                f"media/{art_attribute}", filename=format_ball_filename(ball.country, Path(str(art_attribute)).suffix)
            )
        ]
    )
