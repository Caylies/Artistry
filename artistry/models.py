from __future__ import annotations

import re

from django.core.validators import RegexValidator
from django.db import models
from django.forms import ValidationError

DISCORD_ID_RE = re.compile(r"^\d{17,21}$")
COLON_IDS_RE = re.compile(r"^(\d{17,21}(;\d{17,21})*)?$")


class ArtistrySettings(models.Model):
    spawn_art_channel = models.TextField(
        blank=True,
        help_text="The forum channel ID that will manage spawn artwork.",
        validators=(RegexValidator(DISCORD_ID_RE, message="Invalid forum channel ID."),),
    )
    card_art_channel = models.TextField(
        blank=True,
        help_text="The forum channel ID that will manage card artwork.",
        validators=(RegexValidator(DISCORD_ID_RE, message="Invalid forum channel ID."),),
    )
    emoji_art_channel = models.TextField(
        blank=True,
        help_text="The forum channel ID that will manage emoji artwork.",
        validators=(RegexValidator(DISCORD_ID_RE, message="Invalid forum channel ID."),),
    )

    accepted_message = models.TextField(
        max_length=2000,
        blank=True,
        help_text=(
            "The message that will be sent to a user through DMs when their art is accepted. "
            "If blank, no message will be sent."
        ),
        default="Hi {user}, your artwork for **{ball}** has been accepted!",
    )
    accepted_emoji = models.CharField(
        max_length=20,
        blank=True,
        help_text="A unicode character that will be reacted with. If blank, no reaction will be added.",
        default="✅",
    )

    safe_thread_ids = models.TextField(
        blank=True,
        help_text="Semicolon-delimited thread IDs that will not be deleted during generation.",
        validators=(RegexValidator(COLON_IDS_RE, message="The IDs must be semicolon-separated"),),
    )

    def clean(self) -> None:
        if ArtistrySettings.objects.exclude(pk=self.pk).exists():
            raise ValidationError("You can only have one instance of ArtistrySettings.")

    def __str__(self) -> str:
        return "Artistry package settings"

    class Meta:
        verbose_name_plural = "Settings"
        permissions = [("can_generate", "Can generate art threads."), ("can_accept", "Can accept art submissions.")]

    @property
    def art_channels(self):
        return (self.spawn_art_channel, self.card_art_channel, self.emoji_art_channel)

    def save(self, *args, **kwargs) -> None:
        def lower_safe_threads(thread_ids: str) -> str:
            return ";".join([x.strip() for x in thread_ids.split(";")]).lower()

        self.safe_thread_ids = lower_safe_threads(self.safe_thread_ids)

        return super().save(*args, **kwargs)


async def get_settings():
    return await ArtistrySettings.objects.afirst() or await ArtistrySettings.objects.acreate()
