from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, cast

import discord

from bd_models.models import Ball

from ...models import ArtistrySettings, get_settings
from .enums import ArtType, SyncType
from .utils import format_ball_filename

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def _fetch_threads(channel: discord.ForumChannel) -> set[discord.Thread]:
    existing_threads = {thread for thread in channel.threads}
    archived_threads = {thread async for thread in channel.archived_threads(limit=None)}

    return existing_threads | archived_threads


async def update_ball_thread(bot: "BallsDexBot", art_type: ArtType, thread: discord.Thread, ball: Ball | None = None):
    message = await thread.fetch_message(thread.id)

    ball = ball or await Ball.objects.aget(country=thread.name)
    art_attribute = getattr(ball, art_type.attribute)

    if art_type.attribute == "emoji_id":
        emoji = bot.get_emoji(art_attribute)
        if emoji is None:
            return

        data = await emoji.read()
        await message.edit(
            attachments=[
                discord.File(
                    BytesIO(data), filename=format_ball_filename(ball.country, ".gif" if emoji.animated else ".png")
                )
            ]
        )
    else:
        await message.edit(
            attachments=[
                discord.File(
                    f"media/{art_attribute}",
                    filename=format_ball_filename(ball.country, Path(str(art_attribute)).suffix),
                )
            ]
        )


class ThreadGroup:
    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.spawn_channel_id: str | None = None
        self.card_channel_id: str | None = None
        self.emoji_channel_id: str | None = None
        self.spawn_threads: set[discord.Thread] = set()
        self.card_threads: set[discord.Thread] = set()
        self.emoji_threads: set[discord.Thread] = set()

    def in_sync(self, new_settings: "ArtistrySettings") -> bool:
        return (
            self.spawn_channel_id == new_settings.spawn_art_channel
            and self.card_channel_id == new_settings.card_art_channel
            and self.emoji_channel_id == new_settings.emoji_art_channel
        )

    async def sync(self, settings: "ArtistrySettings | None" = None, *, focus: SyncType = SyncType.All):
        settings = settings or await get_settings()

        spawn_threads: set[discord.Thread] = set()
        card_threads: set[discord.Thread] = set()
        emoji_threads: set[discord.Thread] = set()

        if settings.spawn_art_channel != "" and focus.istype(SyncType.Spawn):
            channel = int(settings.spawn_art_channel)
            spawn_channel = cast(discord.ForumChannel, await self.bot.fetch_channel(channel))
            spawn_threads = await _fetch_threads(spawn_channel)

        if settings.card_art_channel != "" and focus.istype(SyncType.Card):
            channel = int(settings.card_art_channel)
            card_channel = cast(discord.ForumChannel, await self.bot.fetch_channel(channel))
            card_threads = await _fetch_threads(card_channel)

        if settings.emoji_art_channel and focus.istype(SyncType.Emoji):
            channel = int(settings.emoji_art_channel)
            emoji_channel = cast(discord.ForumChannel, await self.bot.fetch_channel(channel))
            emoji_threads = await _fetch_threads(emoji_channel)

        if focus.istype(SyncType.Settings):
            self.spawn_channel_id = settings.spawn_art_channel
            self.card_channel_id = settings.card_art_channel
            self.emoji_channel_id = settings.emoji_art_channel

        self.spawn_threads = spawn_threads
        self.card_threads = card_threads
        self.emoji_threads = emoji_threads
