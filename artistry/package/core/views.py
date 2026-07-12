from discord.ui import Container, Section, TextDisplay, Thumbnail

from ballsdex.core.discord import LayoutView

__all__ = ("GeneratingView",)


class GeneratingView(LayoutView):
    container = Container(
        Section(
            TextDisplay("### Generating Threads..."),
            TextDisplay(
                "This operation may take a couple of seconds to minutes.\n"
                "Generation may pause occasionally due to Discord rate limits."
            ),
            accessory=Thumbnail("https://i.imgur.com/uGCnRl1.gif"),
        )
    )
