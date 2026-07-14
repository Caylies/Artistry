import contextlib
import logging
from io import BytesIO
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
from .core.enums import ArtType
from .core.thread import fetch_threads_from_art_channel, update_ball_thread
from .core.utils import format_ball_filename, sanitize_ball_emoji_name
from .core.views import GeneratingView

log = logging.getLogger("artistry.package.cog")


class Artistry(commands.GroupCog):
    """
    Artistry package commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
        self.generating = False

        self.accept_art_menu = app_commands.ContextMenu(name="Accept Art", callback=self.accept_art)
        self.bot.tree.add_command(self.accept_art_menu)

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

        if message.id == channel.id:
            await interaction.response.send_message("You cannot accept the thread's starter message.", ephemeral=True)
            return

        if not message.attachments:
            await interaction.response.send_message(
                "This message requires an attachment to be accepted.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        settings = await get_settings()
        parent_id = str(channel.parent_id)

        ball = await Ball.objects.aget_or_none(country=channel.name)

        if parent_id not in settings.art_channels or not ball:
            await interaction.followup.send(
                f"You can only accept messages posted in a {bd_settings.collectible_name}'s thread.", ephemeral=True
            )
            return

        art_type = ArtType.from_settings(settings, parent_id)
        attachment = message.attachments[0]

        if art_type == ArtType.Emoji:
            old_emoji = self.bot.get_emoji(ball.emoji_id)

            if old_emoji is not None:
                await old_emoji.delete()

            try:
                emoji = await self.bot.create_application_emoji(
                    name=sanitize_ball_emoji_name(ball.country), image=await attachment.read()
                )
            except discord.HTTPException:
                log.exception("An error occurred while trying to accept a new emoji art.")
                await interaction.followup.send("An error occurred while trying to accept a new emoji art.")
                return
            else:
                setattr(ball, art_type.attribute, emoji.id)
        else:
            setattr(ball, art_type.attribute, ContentFile(await attachment.read(), attachment.filename))

        await ball.asave(update_fields=(art_type.attribute,))
        await self.bot.load_cache()

        if settings.accepted_message != "":
            with contextlib.suppress(discord.Forbidden, discord.HTTPException):
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

        await update_ball_thread(self.bot, art_type, channel)

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
        Generates and maintains threads for the specified art type by deleting invalid threads
        and creating any that are missing.

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

        try:
            settings = await get_settings()

            if len(set(settings.art_channels)) != len(settings.art_channels):
                await interaction.response.send_message(
                    "Configured art channels cannot share the same ID.", ephemeral=True
                )
                return

            await interaction.response.defer(thinking=True)

            message = cast(discord.Message | None, await interaction.followup.send(view=GeneratingView()))
            channel = cast(discord.ForumChannel, await self.bot.fetch_channel(art.get_channel_id(settings)))

            threads = await fetch_threads_from_art_channel(self.bot, art, settings)

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
                if art == ArtType.Emoji:
                    emoji = self.bot.get_emoji(media)

                    if emoji is None:
                        continue

                    thread = await channel.create_thread(
                        name=country,
                        file=discord.File(
                            BytesIO(await emoji.read()),
                            filename=format_ball_filename(country, ".gif" if emoji.animated else ".png"),
                        ),
                    )

                    await thread.message.pin()
                else:
                    thread = await channel.create_thread(
                        name=country,
                        file=discord.File(f"media/{media}", filename=format_ball_filename(country, Path(media).suffix)),
                    )

                    await thread.message.pin()

            self.generating = False

            plural = "" if len(ball_dict) == 1 else "s"

            if message:
                await message.reply(f"Generated **{len(ball_dict):,}** {art.lower()} art thread{plural}!")

            log.info(
                f"{interaction.user} generated {len(ball_dict):,} {art.value.lower()} art thread{plural}",
                extra={"webhook": True},
            )
        finally:
            self.generating = False
