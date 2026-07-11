import contextlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING, cast

import discord
from discord import app_commands
from discord.ext import commands
from django.core.files.base import ContentFile

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

from ballsdex.core.utils import checks
from bd_models.models import Ball
from settings.models import settings as bd_settings

from ..models import get_settings
from .core.enums import ArtType, SyncType
from .core.thread import ThreadGroup, update_ball_thread
from .core.utils import format_ball_filename
from .core.views import GeneratingView, SyncingSettingsView

log = logging.getLogger("artistry.package.cog")


class Artistry(commands.GroupCog):
    """
    Artistry package commands.
    """

    def __init__(self, bot: "BallsDexBot", thread_group: ThreadGroup):
        self.bot = bot
        self.thread_group = thread_group
        self.syncing = False
        self.generating = False

        self.accept_art_menu = app_commands.ContextMenu(name="Accept Art", callback=self.accept_art)

        self.bot.tree.add_command(self.accept_art_menu)

    async def _sync(self, focus: SyncType = SyncType.All):
        self.syncing = True
        await self.thread_group.sync(focus=focus)
        self.syncing = False

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        self.syncing = False
        self.generating = False

    async def accept_art(self, interaction: discord.Interaction["BallsDexBot"], message: discord.Message):
        ctx = await commands.Context.from_interaction(interaction)

        if not await checks.has_permissions("artistry.can_accept").predicate(ctx):
            await interaction.response.send_message("You are not allowed to use this command.", ephemeral=True)
            return

        channel = interaction.channel

        if not isinstance(channel, discord.Thread) or not channel.parent:
            await interaction.response.send_message(
                f"You can only accept messages posted in a {bd_settings.collectible_name}'s thread.", ephemeral=True
            )
            return

        if not message.attachments:
            await interaction.response.send_message(
                "This message requires an attachment to be accepted.", ephemeral=True
            )
            return

        if self.syncing:
            await interaction.response.send_message("This command cannot be used while syncing.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        settings = await get_settings()
        parent_id = str(channel.parent_id)

        ball = await Ball.objects.aget_or_none(country=channel.name)

        if parent_id not in (settings.spawn_art_channel, settings.card_art_channel) or not ball:
            await interaction.followup.send(
                f"You can only accept messages posted in a {bd_settings.collectible_name}'s thread.", ephemeral=True
            )
            return

        art_type = ArtType["Spawn" if parent_id == settings.spawn_art_channel else "Card"]
        attachment = message.attachments[0]

        setattr(ball, art_type.attribute, ContentFile(await attachment.read(), attachment.filename))

        await ball.asave(update_fields=(art_type.attribute,))

        if settings.accepted_message != "":
            with contextlib.suppress(discord.Forbidden):
                await message.author.send(
                    settings.accepted_message.format(
                        user=message.author.mention,
                        accepter=interaction.user.mention,
                        collectibles=bd_settings.plural_collectible_name,
                        collectible=bd_settings.collectible_name,
                        discord=bd_settings.discord_invite,
                        bot=bd_settings.bot_name,
                        ball=ball.country,
                        emoji=self.bot.get_emoji(ball.emoji_id),
                        art_type=art_type.value.lower(),
                    )
                )

        if settings.accepted_emoji != "":
            await message.add_reaction(settings.accepted_emoji)

        await update_ball_thread(art_type, channel)

        await interaction.followup.send(
            f"Accepted **{ball.country}** {art_type.value.lower()} art from {message.author.mention}!", ephemeral=True
        )

        log.info(
            f"{interaction.user} accepted {ball.country} {art_type.value.lower()} art made by {message.author}",
            extra={"webhook": True},
        )

    @app_commands.command()
    @checks.app_check(checks.has_permissions("artistry.can_generate"))
    async def generate(self, interaction: discord.Interaction["BallsDexBot"], art: ArtType):
        """
        Generates and maintains threads for the specified art type (Spawn or Card)
        by deleting invalid threads and creating any that are missing.

        Parameters
        ----------
        art: ArtType
            The type of art to generate threads for.
        """
        if self.generating:
            await interaction.response.send_message(
                "This command cannot be used while generating threads.", ephemeral=True
            )
            return

        self.generating = True

        if self.syncing:
            await interaction.response.send_message("This command cannot be used while syncing.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)

        settings = await get_settings()
        original = None

        if not self.thread_group.in_sync(settings):
            original = cast(discord.Message | None, await interaction.followup.send(view=SyncingSettingsView()))
            await self._sync(SyncType.Settings)

        await self._sync(SyncType[art.value])

        if original:
            await original.edit(view=GeneratingView())

        message = original or cast(discord.Message | None, await interaction.followup.send(view=GeneratingView()))

        channel = None
        threads = None

        match art:
            case ArtType.Spawn:
                channel = await self.bot.fetch_channel(int(settings.spawn_art_channel))
                threads = self.thread_group.spawn_threads

            case ArtType.Card:
                channel = await self.bot.fetch_channel(int(settings.card_art_channel))
                threads = self.thread_group.card_threads

            case _:
                return

        channel = cast(discord.ForumChannel, channel)
        ball_dict: dict[str, str] = {}
        safe_names: list[str] = []

        async for country, media in Ball.objects.filter(enabled=True).values_list("country", art.attribute):
            if any([thread.name == country for thread in threads]):
                safe_names.append(country)
                continue

            ball_dict[country] = media

        safe_threads = settings.safe_thread_ids.split(";")

        for thread in [
            thread for thread in threads if thread.name not in safe_names and str(thread.id) not in safe_threads
        ]:
            await thread.delete()

        for country, media in ball_dict.items():
            thread = await channel.create_thread(
                name=country,
                file=discord.File(f"media/{media}", filename=format_ball_filename(country, Path(media).suffix)),
            )

            await thread.message.pin()

        plural = "" if len(ball_dict) == 1 else "s"

        if message:
            await message.reply(f"Generated **{len(ball_dict):,}** {art.lower()} art thread{plural}!")

        self.generating = False

        log.info(
            f"{interaction.user} generated {len(ball_dict):,} {art.value.lower()} art thread{plural}",
            extra={"webhook": True},
        )

    @app_commands.command()
    @checks.app_check(checks.is_staff())
    async def sync(self, interaction: discord.Interaction["BallsDexBot"]):
        """
        Syncs Artistry settings.
        """
        if self.syncing:
            await interaction.response.send_message("This command cannot be used while syncing.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        await self._sync(SyncType.Settings)
        await interaction.followup.send("Synced Artistry settings!", ephemeral=True)
