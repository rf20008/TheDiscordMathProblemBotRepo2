import disnake
import orjson
import typing
from helpful_modules.problems_module import MathProblemCache, QuizProblem, Quiz
from helpful_modules.problems_module import *
from helpful_modules.threads_or_useful_funcs import generate_new_id, get_log
from .helper_cog import HelperCog
from disnake.ext import commands

log = get_log(__name__)

# Licensed under GPLv3 (or later)


class QuizCog(HelperCog):
    """An incomplete cog which will eventually store quiz-related commands"""

    def __init__(self, bot: disnake.ext.commands.Bot):
        super().__init__(bot)
        self.bot = bot
        self.cache: MathProblemCache = bot.cache
        # TODO: quiz commands :-)

    @commands.slash_command(
        name='quiz',
        description="Interact with a quiz. This has subcommands."
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
        name='create',
        description='Create a quiz. However, interacting with quizzes has not been implemented!'
    )
    async def create(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """The base command to create a quiz. This has subcommands.

        Usage:
        /quiz create from_json [json: str]
        Creates a quiz from JSON. I suggest you do not use this.
        /quiz create blank
        Creates a blank quiz."""

    @create.sub_command(
        name='from_json',
        description='Create a quiz from JSON.',
        options=[
            disnake.Option(
                name='data',
                description='The data (JSON) to convert into a quiz.',
                required=True,
                type=disnake.OptionType.string
            )
        ]
    )
    async def from_json(self, inter: disnake.ApplicationCommandInteraction, data: str) -> None:
        """/quiz create from_json [json: str]
        Create a Quiz from JSON. This is not user-friendly, but it's quick.

        Structure:
        Quiz_Problem: list of quiz problem objects. This order will determine the order of the problems in the quiz.
        guild_id: guild id for the quiz. This guild id must be one of the guilds that you share with this bot or `null` for a global quiz. You must specify this or it will fail!
        -------
        Quiz problem:
        key | value type | description
        question | string | The question to ask the user in this question
        answer | List[string] | The acceptable answers. This is a list of strings.
        points | int | The number of points this problem is worth.

        ----
        """

        # Must parse into list
        # If parsing fails, tell the user.

        # TODO: quiz creation rules: make it possible to ensure that only some people can create quizzes to prevent spam
        try:
            _data: dict = orjson.loads(data)
        except orjson.JSONDecodeError as e:
            return await inter.send(f"""You didn't provide valid JSON, so I don't understand what you mean :(

JSON error: {e}""")
        try:
            guild_id, problems = _data['guild_id'], data["Quiz Problems"]
        except KeyError:
            return await inter.send(
                "Error: Could not decode guild_id or problems from the given dictionary. You probably copy-pasted something else.")
        if not isinstance(problems, list):
            return await inter.send("Problems must be a list.")

        if not isinstance(guild_id, int) or guild_id is None:
            return await inter.send("guild_id must either be an integer or None.")
        if guild_id not in [guild.id for guild in inter.author.mutual_guilds]:
            return await inter.send(
                "You cannot create this quiz because either you or I are not in the guild that you're trying to create the quiz for.")
        real_problems: typing.List[QuizProblem] = []
        for problem_num in range(len(problems)):
            problem = problems[problem_num]
            # parse the problem
            if not isinstance(problem, dict):
                return await inter.send(f"Problem#{problem_num} isn't a dictionary.")

            # Parse the question
            try:
                question = problem['question']
                if not isinstance(question, str):
                    raise TypeError("Question is not a string")
            except KeyError:
                return await inter.send(f"Invalid data - question missing for problem#{problem_num}")
            except TypeError:
                return await inter.send(f"Invalid data - question not a string for problem#{problem_num}")

            # Parse the answer
            try:
                answers: typing.List[str] = problem['answers']
                if not isinstance(answers, list):
                    return await inter.send(f"Invalid data - Answers isn't a list (problem#{problem_num})")
                for answer_num in range(len(answers)):
                    if not isinstance(answers[answer_num], str):
                        return await inter.send(
                            f"Invalid data - answer #{answer_num} in problem #{problem_num} isn't a string")
            except KeyError:
                return await inter.send(f"Invalid data - missing answers for problem #{problem_num}")

            # Parse the number of points this question is worth

            try:
                points: int = problem['points']
                if not isinstance(points, int):
                    return await inter.send(f"Invalid data -  problem#{problem_num}'s point worth isn't a integer")
            except KeyError:
                return await inter.send(f"Invalid data - missing point worth for problem#{problem_num}")

            real_problems.append(
                QuizProblem(
                    question=question,
                    answers=answers,
                    max_score=points,
                    cache=self.cache,
                )
            )
        already_existing_quiz_ids = [quiz.id for quiz in await self.cache.get_quizzes_by_func(func=lambda quiz: True)]
        while True:
            id = generate_new_id()
            if id not in already_existing_quiz_ids:
                break

        quiz_to_create = Quiz(
            id = id,
            problems = real_problems,
            submissions = [],
            cache = self.cache
        )
        await self.cache.add_quiz(quiz_to_create)
        await inter.send("Quiz successfully created!")
