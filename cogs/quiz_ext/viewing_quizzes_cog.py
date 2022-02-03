import disnake
from disnake.ext import commands

from helpful_modules import problems_module
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules.custom_embeds import *
from helpful_modules.problems_module import *

from ..helper_cog import HelperCog
from ._utils import get_attempt_num_for_user, get_quiz_submission


class ViewingQuizzesCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)
        self.bot = bot
        self.cache = bot.cache

    @commands.slash_command(name="quiz_view", description="View quizzes!")
    async def quiz_view(self, inter: disnake.ApplicationCommandInteraction):
        """/quiz_view

        View quizzes

        Subcommands:
        /quiz view entire_quiz
        ---
        View the entire quiz. You must have an existing session for this to work!


        /quiz view ids
        ---
        View the available Quiz IDs


        /quiz view problem

        View the specific quiz problems!"""
        pass

    @quiz_view.sub_command(
        name="entire_quiz",
        description="View the entire quiz. You must have a session!",
        options=[
            disnake.Option(
                name="quiz_id",
                description="The Quiz ID of the quiz you wish to view",
                type=disnake.OptionType.integer,
                required=True,
            ),
            disnake.Option(
                name="raw",
                description="Whether to view the problem raw. You must either be a moderator or be a trusted user to do this!",
                type=disnake.OptionType.boolean,
                required=False,
            ),
            disnake.Option(
                name="show_all_info",
                description="Whether to show all the info. This permission is normally not granted to normal users.",
                type=disnake.OptionType.boolean,
                required=False,
            ),
        ],
    )
    @commands.max_concurrency(7, commands.BucketType.default, wait=True)
    async def entire_quiz(
            self,
            inter: disnake.ApplicationCommandInteraction,
            quiz_id: int,
            raw: bool = False,
            show_all_info: bool = False,
    ):
        """/quiz view entire_quiz [quiz_id: int] (raw: bool = False) (show_all_data: bool = False)
        Raw: Show the data as JSON. You must be trusted to do this!
        show_all_data: Whether to show all data. You must have either solved the quiz (and the quiz owner has to enable quiz solvers seeing the quiz, which is not implemented yet), or you need to be a moderator, or you need to be a trusted user.


        View the entire quiz. Due to Discord limitations, it will be sent in multiple embeds and multiple messages, which might trigger spam filters."""
        await inter.response.defer()
        if raw and not show_all_info:
            await inter.send(embed=ErrorEmbed("You must enable show_all_info to see raw data!"))
            return
        allowed = False
        if raw or show_all_info:
            allowed = False
            if show_all_info:
                # Did they solve it?
                try:
                    quiz: Quiz = await self.cache.get_quiz(quiz_id)
                except QuizNotFoundException:
                    await inter.send(embed=ErrorEmbed("Quiz not found"))
                    return
                solved_quiz: bool = (
                                            len(
                                                filter(
                                                    lambda submission: submission.user_id == inter.author.id,
                                                    quiz.submissions,
                                                )
                                            )
                                            != 0
                                    ) or (
                                            len(
                                                filter(
                                                    lambda _session: (_session.overtime
                                                                      and _session.user_id == inter.author.id),
                                                    quiz.existing_sessions,
                                                )
                                            )
                                            != 0
                                    )
                if quiz.description.solvers_can_view_quiz and solved_quiz:
                    allowed = True
                else:
                    # Are they a mod?
                    data: problems_module.GuildData = (
                        await self.bot.cache.get_guild_data(
                            inter.guild.id,
                            default=problems_module.GuildData.default(
                                guild_id=inter.guild.id
                            ),
                        )
                    )
                    if data.mod_check.check_for_user_passage(inter.author):
                        # They're a mod!
                        allowed = True
                    else:
                        user_data: problems_module.UserData = (
                            await self.bot.cache.get_user_data(
                                user_id=inter.author.id,
                                default=problems_module.UserData(
                                    user_id=inter.author.id,
                                    trusted=False,
                                    blacklisted=False,
                                ),
                            )
                        )
                        if user_data.trusted:
                            allowed = True
            if not allowed:
                await inter.send(
                    embed=ErrorEmbed(
                        """You didn't pass the checks required to pass. Firstly, you didn't solve the quiz, or you did, but people who solve this quiz can't see the answers.
                Secondly, you're not a moderator.
                Finally, you're not trusted. 
                For these reasons, you are not allowed to see all data for the quiz"""
                    )
                )
            if raw:
                allowed = False
                user_data: problems_module.UserData = await self.bot.cache.get_user_data(
                    user_id=inter.author.id,
                    default=problems_module.UserData(
                        user_id=inter.author.id, trusted=False, blacklisted=False
                    )
                )
                if user_data.trusted:
                    allowed = True

        try:
            quiz: Quiz = await self.cache.get_quiz(quiz_id)
        except QuizNotFound:
            await inter.send(embed=ErrorEmbed("Quiz not found"))
            return

        try:
            session: problems_module.QuizSolvingSession = await get_quiz_submission(
                self, inter.author.id, quiz_id
            )
        except problems_module.errors.SessionNotFoundException:
            await inter.send(embed=ErrorEmbed("You don't have a session for this quiz!!"))
            return

        if session.done:
            await inter.send(
                embed=ErrorEmbed(
                    "Sorry, but you ran out of time, so you'll need to try again!"
                )
            )
            return

        thing_to_send: str = f"Quiz id #{quiz_id}"
        try:
            quiz_problems: typing.List[QuizProblem] = list(
                (await self.cache.get_quiz(quiz_id)).quiz_problems
            )
        except problems_module.QuizNotFound:
            await inter.send(
                embed=ErrorEmbed(
                    "Apparently the quiz was deleted while you were solving... :("
                )
            )
            return
        if not raw and not show_all_info:
            await inter.send(embed=disnake.Embed(thing_to_send))
            for problem_num, problem in quiz_problems.items():
                problem_str = f"""
                    Question: {problem.question}
                    Is Written: {'yes' if problem.is_written else 'no'}
                    Max Score: {problem.max_score}
                    Problem Number: {problem_num}
    """
                await inter.send(
                    embed=disnake.Embed(
                        title=f"Problem #{problem_num}",
                        description=problem_str,
                        color=disnake.Color.from_rgb(20, 200, 30),
                    )
                )
                await asyncio.sleep(1)  # To avoid rate-limiting

        if not allowed:
            await inter.send("You are not allowed to do this!")
        elif show_all_info and not raw and allowed:
            await inter.send(thing_to_send)
            for problem_num, problem in quiz.quiz_problems.items():
                problem_str = f"""
    Question: {problem.question}
    Answer: {problem.answer if problem.is_written else '(This problem is a written problem)'}
    Is Written: {problem.is_written}
    Max Score: {problem.max_score}
    Problem Number: {problem_num}"""
                await inter.send(
                    embed=disnake.Embed(
                        title=f"Problem #{problem_num}",
                        description=problem_str,
                        color=disnake.Color.from_rgb(90, 90, 250)
                    )
                )
                await asyncio.sleep(1)
        elif raw and show_all_info and allowed:
            file: disnake.File = disnake.File(BytesIO(
                json.dumps(
                    quiz.to_dict()
                ),
                'utf-8'),
                filename='raw_quiz.json')
            await inter.send('I have attached the file!', file=file)
            del file

    # TODO: /quiz_view single_problem