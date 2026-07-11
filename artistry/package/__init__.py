from typing import TYPE_CHECKING

from .cog import Artistry
from .core.thread import ThreadGroup

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot


async def setup(bot: "BallsDexBot"):
    thread_group = ThreadGroup(bot)
    await thread_group.sync()

    await bot.add_cog(Artistry(bot, thread_group))
