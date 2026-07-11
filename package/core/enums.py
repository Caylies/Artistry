from enum import StrEnum
from typing import Literal, Self


class SyncType(StrEnum):
    Spawn = "Spawn"
    Card = "Card"
    Settings = "Settings"
    All = "All"

    def istype(self, sync_type: Self) -> bool:
        """
        Determines if a `SyncType` is equal to another `SyncType` or if its equal to `SyncType.ALL`.

        Parameters
        ----------
        sync_type: SyncType
            The sync type to compare with.
        """
        return self in (sync_type, SyncType.All)


class ArtType(StrEnum):
    Spawn = "Spawn"
    Card = "Card"

    @property
    def attribute(self) -> Literal["wild_card", "collection_card"]:
        return "wild_card" if self == ArtType.Spawn else "collection_card"
