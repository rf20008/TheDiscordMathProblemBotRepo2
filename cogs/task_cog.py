import disnake
from disnake.ext import commands, tasks

from helpful_modules import problems_module
from helpful_modules._error_logging import log_error
from helpful_modules.custom_bot import TheDiscordMathProblemBot

from .helper_cog import HelperCog
from typing import Union
from disnake.ext.commands import Bot, InteractionBot, AutoShardedInteractionBot, AutoShardedBot

# TODO: make this an extension :-)


class TaskCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        self.bot = bot
        super().__init__(self, bot)
        self.cache = bot.cache
    @commands.Cog.listener()
    async def on_slash_command(self, inter: disnake.ApplicationCommandInteraction):
        """Leave guilds because the guild is blacklisted"""
        if not inter.guild:
            return
        if not isinstance(inter.bot, TheDiscordMathProblemBot):
            raise TypeError()
        if await inter.bot.is_guild_blacklisted(inter.guild):
            await inter.send("Your guild is blacklisted - so I am leaving this guild")
            await inter.bot.notify_guild_on_guild_leave_because_guild_blacklist()

    @tasks.loop(seconds=15)
    async def report_tasks_task(self):
        for task in self.bot._tasks:
            if task.failed():
                # Log the exception
                _int_task = task.get_task()
                if _int_task.done():
                    try:
                        log_error(_int_task.exception())
                    except asyncio.InvalidStateError as ISE:
                        log_error(ISE)

    @tasks.loop(minutes=15)
    async def leaving_blacklisted_guilds_task(self):
        for guild in self.bot.guilds:
            if await self.bot.is_guild_blacklisted(guild):
                await self.bot.notify_guild_on_guild_leave_because_guild_blacklist(
                    guild
                )
    @tasks.loop(seconds=15)
    async def update_cache_task(self):
        await self.cache.update_cache()



    def cog_unload(self):
        super().cog_unload()
        self.leaving_blacklisted_guilds_task.stop()
        self.update_cache_task.stop()
        self.report_tasks_task.stop()

def setup(bot: TheDiscordMathProblemBot):
    bot.add_cog(TaskCog(bot))