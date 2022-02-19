from ._utils import get_quiz_submission
from ..helper_cog import HelperCog

from disnake.ext import commands
import disnake
from helpful_modules import problems_module
from helpful_modules.problems_module import *
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules.my_modal import MyModal


class GradingQuizzesCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)

    @commands.slash_command(name="quiz_grade", description="Grade quizzes!")
    async def quiz_grade(self, inter: disnake.ApplicationCommandInteraction):
        """This is a slash command that is meant to be used to grade quizzes!"""
        raise NotImplementedError
