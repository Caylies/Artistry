from typing import TYPE_CHECKING

from django.contrib import admin
from django.db import models
from django.forms import widgets

from .models import ArtistrySettings

if TYPE_CHECKING:
    from django.http import HttpRequest


@admin.register(ArtistrySettings)
class ArtistrySettingsAdmin(admin.ModelAdmin):
    save_on_top = True
    formfield_overrides = {models.TextField: {"widget": widgets.TextInput}}
    fieldsets = [
        (None, {"fields": ("spawn_art_channel", "card_art_channel", "emoji_art_channel")}),
        ("Personalization", {"fields": ("accepted_message", "accepted_emoji")}),
        ("Thread management", {"fields": ("safe_thread_ids",)}),
    ]

    def has_add_permission(self, request: "HttpRequest") -> bool:
        return super().has_add_permission(request) and ArtistrySettings.objects.first() is None

    def has_delete_permission(self, request: "HttpRequest", obj: ArtistrySettings | None = None) -> bool:
        return False
