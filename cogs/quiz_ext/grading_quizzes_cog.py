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

    async def can_grade_quiz(self, inter, quiz_id):
        """Return whether the user can grade the quiz and respond no to the interaction if not."""
        if quiz_id is ...:
            await inter.send("You didn't provide a quiz id!")
            return False

        try:
            quiz = await self.cache.get_quiz(quiz_id)
        except problems_module.QuizNotFound:
            await inter.send(embed=ErrorEmbed("Quiz not found!"))
            return False

        if quiz.guild_id is not None and quiz.guild_id not in [guild.id for guild in inter.author.mutual_guilds]:
            await inter.send("This quiz isn't in any of your mutual guilds!")
            return False

        if quiz.guild_id is not None and quiz.guild_id != inter.guild_id:
            await inter.send(
                f"This is the wrong guild for the quiz -- the right guild is the one with the id {quiz.guild_id}")
            return False

        if inter.author.id not in quiz.authors:
            await inter.send("You don't have permission to grade this quiz.")
            return False
        return True

    @commands.slash_command(name="quiz_grade", description="Grade quizzes!")
    async def quiz_grade(self, inter: disnake.ApplicationCommandInteraction):
        """This is a slash command that is meant to be used to grade quizzes!"""
        pass

    @quiz_grade.sub_command(
        name='view_submission_users',
        description="View the users who submitted submissions to this quiz")
    async def view_submission_users(self, inter, quiz_id: int = commands.Param(large=True)) -> typing.Optional[
        typing.Union[
            disnake.InteractionMessage, disnake.Message
        ]
    ]:
        if not await self.can_grade_quiz(inter, quiz_id):
            return
        users_with_submissions = set()
        for submission in quiz.submissions:
            users_with_submissions.add(submission.user_id)

        string_to_send = f"""
        Users who have submitted answers to this quiz
        -------------
        """
        for user_id in users_with_submissions:
            string_to_send += f"<@{user_id}>\n"
        string_to_send += f"({len(users_with_submissions)} users)"
        await inter.send(
            embed=SuccessEmbed(string_to_send),
            allowed_mentions=disnake.AllowedMentions(users=False)
        )
        del users_with_submissions
        del string_to_send
        return

    # Quiz grading needs
    @quiz_grade.sub_command(
        name='manual_grade',
        description="Manually grade quizzes"
    )
    async def manual_grade(
            self,
            inter: disnake.ApplicationCommandInteraction,
            quiz_id: int = commands.Param(description="The quiz to grade"),
            user: disnake.User = commands.Param(description="The user to grade"),
            attempt_num: int = commands.Param(description="The attempt number to grade (defaults to 0)", le=0)
    ):
        if not await self.can_grade_quiz(inter, quiz_id):
            return

        # This user can grade the quiz
        # Fetch the quiz again
        # It is known that the quiz exists, or it would have been handled in await self.can_grade_quiz
        quiz = await self.cache.get_quiz(quiz_id)
        user_submission = [
            submission for submission in quiz.submissions
            if submission.user_id == user.id and submission.attempt_num == attempt_num and submission.done
        ][0]
        raise NotImplementedError("I don't know what logic I will use to get data! Also QuizSubmissionSessions don't have reasoning")