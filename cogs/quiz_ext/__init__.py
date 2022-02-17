import disnake
from disnake.ext import commands

from helpful_modules.custom_bot import TheDiscordMathProblemBot

from .creating_quizzes_commands import CreatingQuizzesCommandsCog
from .solving_commands import QuizSolveCog
from .viewing_quizzes_cog import ViewingQuizzesCog
from .modifying_quizzes_cog import ModifyingQuizzesCog


def setup(bot: TheDiscordMathProblemBot) -> None:
    bot.add_cog(QuizSolveCog(bot))
    bot.add_cog(CreatingQuizzesCommandsCog(bot))
    bot.add_cog(ViewingQuizzesCog(bot))
    bot.add_cog(ModifyingQuizzesCog(bot))


def teardown(bot: TheDiscordMathProblemBot) -> None:
    bot.remove_cog("QuizSolveCog")
    bot.remove_cog("CreatingQuizzesCommandsCog")
    bot.remove_cog("ViewingQuizzesCog")
    bot.remove_cog("ModifyingQuizzesCog")
