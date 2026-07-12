from enum import StrEnum
from typing import Literal

from ...models import ArtistrySettings


class ArtType(StrEnum):
    Spawn = "Spawn"
    Card = "Card"
    Emoji = "Emoji"

    def get_channel_id(self, settings: ArtistrySettings) -> int:
        return int(getattr(settings, f"{self.value.lower()}_art_channel"))

    @staticmethod
    def from_settings(settings: ArtistrySettings, channel_id: str):
        match channel_id:
            case settings.spawn_art_channel:
                return ArtType.Spawn
            case settings.card_art_channel:
                return ArtType.Card
            case settings.emoji_art_channel:
                return ArtType.Emoji
            case _:
                return ArtType.Spawn

    @property
    def attribute(self) -> Literal["wild_card", "collection_card", "emoji_id"]:
        match self:
            case ArtType.Spawn:
                return "wild_card"
            case ArtType.Card:
                return "collection_card"
            case ArtType.Emoji:
                return "emoji_id"
