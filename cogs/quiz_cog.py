import asyncio
import json
import typing
from io import BytesIO

import disnake
from disnake.ext import commands

from helpful_modules import problems_module
from helpful_modules.custom_embeds import ErrorEmbed, SuccessEmbed
from helpful_modules.problems_module import *
from helpful_modules.problems_module import MathProblemCache, Quiz, QuizProblem
from helpful_modules.problems_module.quizzes import (QuizSolvingSession,
                                                     QuizSubmission)
from helpful_modules.threads_or_useful_funcs import generate_new_id, get_log

from .helper_cog import HelperCog

log = get_log(__name__)


# Licensed under GPLv3 (or later)
# TODO: implement everything!


class QuizCog(HelperCog):
    """An incomplete cog which will eventually store all quiz-related commands"""

    def __init__(self, bot: disnake.ext.commands.Bot):
        super().__init__(bot)
        self.bot = bot
        self.cache: MathProblemCache = bot.cache
        # TODO: quiz commands :-)

    @commands.slash_command(
        name="quiz", description="Interact with a quiz. This has subcommands."
    )
    async def quiz(self, inter):
        """/quiz ...
        Interact with a quiz. This has subcommands.
        Usage:
        /quiz create from_json [json: str]
        Creates a quiz from JSON. I suggest you do not use this.
        /quiz create blank
        Create a blank quiz.
        """

    @quiz.sub_command_group(
        name="create",
        description="Create a quiz. However, interacting with quizzes has not been implemented!",
    )
    async def create(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """The base command to create a quiz. This has subcommands.

        Usage:
        /quiz create from_json [json: str]
        Creates a quiz from JSON. I suggest you do not use this.
        /quiz create blank
        Creates a blank quiz."""

    @create.sub_command(
        name="from_json",
        description="Create a quiz from JSON.",
        options=[
            disnake.Option(
                name="data",
                description="The data (JSON) to convert into a quiz.",
                required=True,
                type=disnake.OptionType.string,
            )
        ],
    )
    async def from_json(
            self, inter: disnake.ApplicationCommandInteraction, data: str
    ) -> None:
        """/quiz create from_json [json: str]
        Create a Quiz from JSON. This is not user-friendly, but it's quick.

        Structure:
        Quiz Problem: list of quiz problem objects. This order will determine the order of the problems in the quiz.
        guild_id: guild id for the quiz. This guild id must be one of the guilds that you share with this bot or `null` for a global quiz. You must specify this or it will fail!
        -------
        Quiz problem:
        legend: key | value type | description
        --------
        question | string | The question to ask the user in this question
        answer | List[string] | The acceptable answers. This is a list of strings.
        points | int | The number of points this problem is worth.
        is_written | boolean (either `true` or `false`) | whether this problem is a written problem. Cannot be used with the `answers` parameter.
        ------
        """

        # Must parse into list
        # If parsing fails, tell the user.

        # TODO: quiz creation rules: make it possible to ensure that only some people can create quizzes to prevent spam
        try:
            _data: dict = json.loads(data)
        except json.JSONDecodeError as e:
            return await inter.send(
                f"""You didn't provide valid JSON, so I don't understand what you mean :(

JSON error: {e}"""
            )
        try:
            guild_id, problems = _data["guild_id"], _data["Quiz Problems"]
        except KeyError:
            return await inter.send(
                "Error: Could not decode guild_id or problems from the given dictionary. You probably copy-pasted something else."
            )
        if not isinstance(problems, list):
            return await inter.send("Problems must be a list.")

        if not isinstance(guild_id, int) or guild_id is None:
            return await inter.send("guild_id must either be an integer or None.")
        if guild_id not in [guild.id for guild in inter.author.mutual_guilds]:
            return await inter.send(
                "You cannot create this quiz because either you or I are not in the guild that you're trying to create the quiz for."
            )
        real_problems: typing.List[QuizProblem] = []
        for problem_num in range(len(problems)):
            problem = problems[problem_num]
            # parse the problem
            if not isinstance(problem, dict):
                return await inter.send(f"Problem#{problem_num} isn't a dictionary.")
            has_answers: bool = "answers" in problem.keys()
            # Parse the question
            try:
                question = problem["question"]
                if not isinstance(question, str):
                    raise TypeError("Question is not a string")
            except KeyError:
                return await inter.send(
                    f"Invalid data - question missing for problem#{problem_num}"
                )
            except TypeError:
                return await inter.send(
                    f"Invalid data - question not a string for problem#{problem_num}"
                )

            # Parse the answer
            if has_answers:
                try:
                    answers: typing.List[str] = problem["answers"]
                    if not isinstance(answers, list):
                        return await inter.send(
                            f"Invalid data - Answers isn't a list (problem#{problem_num})"
                        )
                    for answer_num in range(len(answers)):
                        if not isinstance(answers[answer_num], str):
                            return await inter.send(
                                f"Invalid data - answer #{answer_num} in problem #{problem_num} isn't a string"
                            )
                except KeyError:
                    return await inter.send(
                        f"Invalid data - missing answers for problem #{problem_num}"
                    )
            else:
                answers = []
                try:
                    is_written: bool = problem["is_written"]
                    if not isinstance(is_written, bool):
                        return await inter.send(
                            f"Invalid data - is_written for problem #{problem_num} is not a boolean."
                        )
                except KeyError:
                    return await inter.send(
                        f"Invalid data - missing is_written and answer for problem#{problem_num}. Please try again!"
                    )

            # Parse the number of points this question is worth

            try:
                points: int = problem["points"]
                if not isinstance(points, int):
                    return await inter.send(
                        f"Invalid data -  problem#{problem_num}'s point worth isn't a integer"
                    )
            except KeyError:
                return await inter.send(
                    f"Invalid data - missing point worth for problem#{problem_num}"
                )

            real_problems.append(
                QuizProblem(
                    question=question,
                    answers=answers,
                    max_score=points,
                    cache=self.cache,
                    author=inter.author.id,
                    guild_id=guild_id,
                )
            )
        already_existing_quiz_ids = [
            quiz.id
            for quiz in await self.cache.get_quizzes_by_func(func=lambda quiz: True)
        ]
        while True:
            id = generate_new_id()
            if id not in already_existing_quiz_ids:
                break

        quiz_to_create = Quiz(
            id=id,
            problems=real_problems,
            submissions=[],
            cache=self.cache,
            authors=[inter.author.id],
        )
        await self.cache.add_quiz(quiz_to_create)
        await inter.send("Quiz successfully created!")

    @create.sub_command(name="blank", description="Create a blank quiz")
    async def blank(self, inter):
        """/quiz create blank
        Create a blank quiz. This is more user-friendly than /quiz create from_json, but it's slower!

        There is currently a bug. Don't use this because there is a bug that makes the quiz not actually be created because there are no problems."""

        # TODO: only some people can create quizzes
        already_existing_quiz_ids = [
            quiz.id
            for quiz in await self.cache.get_quizzes_by_func(func=lambda quiz: True)
        ]
        while True:
            id = generate_new_id()
            if id not in already_existing_quiz_ids:
                break
        quiz = Quiz(
            id=id,
            quiz_problems=[],
            submissions=[],
            authors=[inter.author.id],
            cache=self.cache,
        )
        # bug: empty quizzes cannot be added because they are empty
        # TODO: fix
        await self.bot.cache.add_quiz(quiz)
        await inter.send("Successfully created quiz!")



    @quiz.sub_command_group(name="view", description="View quizzes!")
    def view(self, inter: disnake.ApplicationCommandInteraction):
        """/quiz view

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

    @view.sub_command(
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
            session: QuizSolvingSession = await self._get_quiz_submission(
                inter.author.id, quiz_id
            )
        except problems_module.errors.SessionNotFoundException:
            await inter.send(embed=ErrorEmbed("Session not found!"))
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

