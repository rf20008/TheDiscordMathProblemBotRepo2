import disnake

from helpful_modules.problems_module.cache import MathProblemCache
from .helper_cog import HelperCog


class QuizCog(HelperCog):
    "An incomplete cog which will eventually store quiz-related commands"

    def __init__(self, bot: disnake.ext.commands.Bot):
        super().__init__(bot)
        self.bot = bot
        self.cache: MathProblemCache = bot.cache
        self.slash = bot.slash
