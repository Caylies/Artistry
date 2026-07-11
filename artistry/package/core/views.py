from discord.ui import Container, Section, TextDisplay, Thumbnail

from ballsdex.core.discord import LayoutView

__all__ = ("GeneratingView", "SyncingSettingsView")


class GeneratingView(LayoutView):
    container = Container(
        Section(
            TextDisplay("### Generating Threads..."),
            TextDisplay("This operation may take a couple of seconds."),
            accessory=Thumbnail("https://i.imgur.com/uGCnRl1.gif"),
        )
    )


class SyncingSettingsView(LayoutView):
    container = Container(TextDisplay("Syncing settings with current configuration..."))
