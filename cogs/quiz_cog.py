import nextcord
import dislash
from dislash import *
from .helper_cog import HelperCog


class QuizCog(HelperCog):
    "An incomplete cog which will eventually store quiz-related commands"

    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        self.cache = bot.cache
        self.slash = bot.slash
