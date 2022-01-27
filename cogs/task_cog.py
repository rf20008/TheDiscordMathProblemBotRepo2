import disnake
from disnake.ext import commands, tasks

from helpful_modules import problems_module
from helpful_modules._error_logging import log_error
from helpful_modules.custom_bot import TheDiscordMathProblemBot

from .helper_cog import HelperCog


class TaskCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        self.bot = bot
        super().__init__(self, bot)
        self.cache = bot.cache

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
            data: problems_module.GuildData = await self.bot.cache.get_guild_data(
                guild.id,
                default=problems_module.GuildData(
                    guild_id=guild_id,
                    blacklisted=False,
                    mod_check=problems_module.CheckForUserPassage(
                        [], [], [], ["administrator"]
                    ),
                    can_create_quizzes_check=problems_module.CheckForUserPassage(
                        [], [], [], []
                    ),
                    can_create_problems_check=problems_module.CheckForUserPassage(
                        [], [], [], []
                    ),
                ),
            )
            if data.blacklisted:
                await guild.leave()
