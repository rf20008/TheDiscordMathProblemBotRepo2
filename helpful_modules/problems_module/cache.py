import asyncio
from types import FunctionType as function
import typing
from mysql.connector import connect
import disnake
import aiosqlite
from copy import deepcopy, copy
import sqlite3
import warnings
import pickle
from typing import *
from .errors import *
from helpful_modules.dict_factory import dict_factory
from .base_problem import BaseProblem
from .quizzes import Quiz, QuizProblem, QuizSubmission
from .mysql_connector_with_stmt import *


class MathProblemCache:
    "A class that stores math problems/quizzes :-)"

    def __init__(
        self,
        *,
        mysql_username: str,
        mysql_password: str,
        mysql_db_ip: str,
        mysql_db_name: str,
        use_sqlite: bool = False,
        max_answer_length: int = 100,
        max_question_limit: int = 250,
        max_guild_problems: int = 125,
        warnings_or_errors: Union[Literal["warnings"], Literal["errors"]] = "warnings",
        db_name: str = "problems_module.db",
        name: str = "1",
        update_cache_by_default_when_requesting: bool = True,
        use_cached_problems: bool = False,
    ):
        "Create a new MathProblemCache. the arguments should be self-explanatory"
        # make_sql_table([], db_name = sql_dict_db_name)
        # make_sql_table([], db_name = "MathProblemCache1.db", table_name="kv_store")
        if use_sqlite:
            warnings.warn("Sqlite has been deprecated. Use MySQL instead.")
        self.db_name = db_name
        if warnings_or_errors not in ["warnings", "errors"]:
            raise ValueError(
                f"warnings_or_errors is {warnings_or_errors}, not 'warnings' or 'errors'"
            )
        self.warnings = (
            warnings_or_errors == "warnings"
        )  # Whether to raise TypeErrors or warn
        self.use_sqlite = use_sqlite
        self.use_cached_problems = use_cached_problems
        self._max_answer_length = max_answer_length
        self._max_question_length = max_question_limit
        self._max_guild_limit = max_guild_problems
        self.mysql_username = mysql_username
        self.mysql_password = mysql_password
        self.mysql_db_ip = mysql_db_ip
        self.mysql_db_name = mysql_db_name
        asyncio.run(self.initialize_sql_table())
        self.update_cache_by_default_when_requesting = (
            update_cache_by_default_when_requesting
        )



    async def initialize_sql_table(self):
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS problems (
                        guild_id INT,
                        problem_id INT,
                        question TEXT(2000) NOT NULL,
                        answers BLOB NOT NULL, 
                        author INT NOT NULL,
                        voters BLOB NOT NULL,
                        solvers BLOB NOT NULL
                        )"""
                )  # Blob types will be compliled with pickle.loads() and pickle.dumps() (they are lists)
                # author: int = user_id

                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quizzes (
                    guild_id INT,
                    quiz_id INT NOT NULL PRIMARY KEY,
                    problem_id INT NOT NULL,
                    question TEXT(500) NOT NULL,
                    answer BLOB NOT NULL,
                    voters BLOB NOT NULL,
                    author INT NOT NULL,
                    solvers INT NOT NULL
                )"""
                )
                # Used for quizzes
                # answer: Blob (a list)
                # voters: Blob (a list)
                # solvers: Blob (a list)
                # submissions: Blob (a dictionary)
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quiz_submissions (
                    guild_id INT,
                    quiz_id INT NOT NULL,
                    user_id INT NOT NULL,
                    submissions BLOB NOT NULL
                    )"""
                )  # as dictionary
                # Used to store submissions!

                await conn.commit()  # Otherwise, when this closes, the database just reverted!
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS problems (
                        guild_id BIGINT,
                        problem_id BIGINT,
                        question TEXT(2000) NOT NULL,
                        answers BLOB NOT NULL, 
                        author BIGINT NOT NULL,
                        voters BLOB NOT NULL,
                        solvers BLOB NOT NULL
                        )"""
                )  # Blob types will be compliled with pickle.loads() and pickle.dumps() (they are lists)
                # author: int = user_id
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quizzes (
                    guild_id BIGINT,
                    quiz_id BIGINT NOT NULL PRIMARY KEY,
                    problem_id BIGINT NOT NULL,
                    question TEXT(500) NOT NULL,
                    answer BLOB NOT NULL,
                    voters BLOB NOT NULL,
                    author BIGINT NOT NULL,
                    solvers BLOB NOT NULL
                )"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quiz_submissions (
                    guild_id BIGINT,
                    quiz_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    submissions BLOB NOT NULL
                    )"""
                )  # as dictionary
                # Used to store submissions

    @property
    def max_answer_length(self):
        return self._max_answer_length

    @property
    def max_question_length(self):
        return self._max_question_length

    @property
    def max_guild_problems(self):
        return self._max_guild_limit

    async def convert_to_dict(self):
        "A method that converts self to a dictionary (not used, will probably be removed soon)"
        e = {}
        await self.update_cache()

        for guild_id in self.guild_ids:
            e[guild_id] = {}
            for Problem in self.guild_problems[guild_id]:
                e[guild_id][Problem.id] = Problem.to_dict()
        return e

    def convert_dict_to_math_problem(self, problem: dict, use_from_dict: bool = True):
        "Convert a dictionary into a math problem. It must be in the expected format. (Overriden by from_dict, but still used) Possibly not used due to SQL"
        if use_from_dict:
            return BaseProblem.from_dict(
                problem, cache=self
            )  # Return the baseproblem.from_dict method
        try:
            assert isinstance(problem, dict)
        except AssertionError:
            raise TypeError("problem is not actually a Dictionary")
        guild_id = problem["guild_id"]
        if guild_id == None:
            guild_id = None
        else:
            guild_id = int(guild_id)
        problem2 = self(
            question=problem["question"],
            answer=problem["answer"],
            id=int(problem["id"]),
            guild_id=guild_id,
            voters=problem["voters"],
            solvers=problem["solvers"],
            author=problem["author"],
            cache=self,
        )
        return problem2

    async def update_cache(self: "MathProblemCache") -> None:
        "Method revamped! This method updates the cache of the guilds, the guild problems, and the cache of the global problems. Takes O(N) time"
        guild_problems = {}
        guild_ids = []
        global_problems = {}
        quiz_problems_dict = {}
        quiz_submissions_dict = {}
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute("SELECT * FROM problems")  # Get all problems

                for row in await cursor.fetchall():
                    Problem = BaseProblem.from_row(
                        row, cache=copy(self)
                    )  # Convert the problems to math problems
                    if (
                        Problem.guild_id not in guild_ids
                    ):  # Similar logic: Make sure it's there!
                        guild_ids.append(Problem.guild_id)
                        guild_problems[
                            Problem.guild_id
                        ] = {}  # For quick, cached access?
                    try:
                        guild_problems[Problem.guild_id][Problem.id] = Problem
                    except BaseException as e:
                        raise SQLException(
                            "For some reason, the cache couldn't be updated. Please help!"
                        ) from e
                    await cursor.execute("SELECT * FROM quizzes")
                    for row in await cursor.fetchall():
                        quiz_problem = QuizProblem.from_row(row, cache=copy(self))
                        try:
                            quiz_problems_dict[quiz_problem.id].append(quiz_problem)
                        except KeyError:
                            quiz_problems_dict[quiz_problem.id] = [quiz_problem]
                    await cursor.execute("SELECT submissions from quiz_submissions")
                    for row in await cursor.fetchall():
                        submission = QuizSubmission.from_dict(
                            pickle.loads(row["submission"])
                        )
                        try:
                            quiz_submissions_dict[submission.quiz_id].append(submission)
                        except KeyError:
                            quiz_submissions_dict[submission.quiz_id] = [submission]

        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute("SELECT * FROM problems")  # Get all problems
                for row in cursor.fetchall():
                    Problem = BaseProblem.from_row(row, cache=copy(self))
                    if (
                        Problem.guild_id not in guild_ids
                    ):  # Similar logic: Make sure it's there!
                        guild_ids.append(Problem.guild_id)
                        guild_problems[
                            Problem.guild_id
                        ] = {}  # For quick, cached access?
                    try:
                        guild_problems[Problem.guild_id][Problem.id] = Problem
                    except BaseException as e:
                        raise SQLException(
                            "For some reason, the cache couldn't be updated. Please help!"
                        ) from e
                cursor.execute("SELECT * FROM quizzes")  # Get all quiz problems
                for row in cursor.fetchall():
                    quiz_problem = QuizProblem.from_row(
                        row, cache=copy(self)
                    )  # Turn the quiz problems into QuizProblem objects
                    try:
                        quiz_problems_dict[quiz_problem.id].append(
                            quiz_problem
                        )  # Add it to the quiz with the given id
                    except KeyError:
                        quiz_problems_dict[quiz_problem.id] = [
                            quiz_problem
                        ]  # New quiz!
                # Similar log for quiz submissions
                cursor.execute("SELECT submissions from quiz_submissions")
                for row in cursor.fetchall():
                    submission = QuizSubmission.from_dict(
                        pickle.loads(row["submission"])
                    )
                    try:
                        quiz_submissions_dict[submission.quiz_id].append(submission)
                    except KeyError:
                        quiz_submissions_dict[submission.quiz_id] = [submission]

        try:
            global_problems = deepcopy(
                guild_problems[None]
            )  # contention deepcopying more :-)
        except KeyError as exc:  # No global problems yet
            global_problems = {}
        self.guild_problems = deepcopy(
            guild_problems
        )  # More deep-copying (so it refers to a different object)
        self.guild_ids = deepcopy(guild_ids)
        self.global_problems = deepcopy(global_problems)
        self.cached_quizzes = [
            Quiz(_id, quiz_problems_dict[_id], submissions=quiz_submissions_dict[_id])
            for _id in quiz_problems_dict.keys()
        ]
        self.cached_submissions = quiz_submissions_dict.values()

    async def get_quizzes_by_func(
        self: "MathProblemCache",
        func: function = lambda quiz: False,
        args: typing.Union[tuple, list] = [],
        kwargs: dict = {},
    ) -> typing.List[Quiz]:
        "Get the quizzes that match the function. Function is a function that takes in the quiz, and the provided arguments and keyword arguments. Return True to signify you want the quiz in the list, and False to signify you don't."
        await self.update_cache()
        return [quiz for quiz in self.cached_quizzes if func(quiz, *args, **kwargs)]

    async def get_problems_by_func(
        self: "MathProblemCache",
        func: function = lambda problem: False,
        args: typing.Union[tuple, list] = [],
        kwargs: dict = {},
    ) -> typing.List[BaseProblem]:
        "Returns the list of all problems that match the given function"
        await self.update_cache()
        guild_problems = []
        for item in self.guild_problems.values():
            guild_problems.extend(
                item.values()
            )  # This could be a list concentation (but it creates the list of guild problems)
        global_problems_that_meet_the_criteria = [
            problem
            for problem in self.global_problems.values()
            if func(problem, *args, **kwargs)
        ]
        guild_problems_that_meet_the_criteria = [
            problem for problem in guild_problems if func(problem, *args, **kwargs)
        ]
        problems_that_meet_the_criteria = global_problems_that_meet_the_criteria
        problems_that_meet_the_criteria.extend(guild_problems_that_meet_the_criteria)
        return problems_that_meet_the_criteria

    async def get_problem(self, guild_id: int, problem_id: int) -> BaseProblem:
        "Gets the problem with this guild id and problem id. If the problem is not found, a ProblemNotFound exception will be raised."

        if not isinstance(guild_id, int) and guild_id is not None:
            if self.warnings:
                warnings.warn("guild_id is not a integer!", category=RuntimeWarning)
            else:
                raise TypeError(
                    "guild_id isn't an integer and this will cause issues in SQL!"
                )
        if not isinstance(problem_id, int):
            if self.warnings:
                warnings.warn("problem_id is not a integer", category=RuntimeWarning)
            else:
                raise TypeError("problem_id is not a integer")
        if self.use_cached_problems:
            if self.update_cache_by_default_when_requesting:
                await self.update_cache()  # Make sure the cache is up-to-date
            try:
                return self.guild_problems[guild_id][
                    problem_id
                ]  # Get the cached problem!
            except KeyError:
                raise ProblemNotFound(
                    "Problem not found in the cache! You may want to try again, but without caching!"
                )
        else:
            # Otherwise, use SQL to get the problem!
            if self.use_sqlite:
                async with aiosqlite.connect(self.db_name) as conn:

                    try:
                        conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                    except BaseException as exc:
                        # Not writeable?
                        try:
                            dict_factory  # Check for nameerror
                        except NameError as exc2:
                            raise MathProblemsModuleException(
                                "dict_factory could not be found"
                            ) from exc2
                        if isinstance(exc, AttributeError):  # Can't set attribute
                            pass
                        else:
                            raise  # Re-raise the exception
                    cursor = await conn.cursor()
                    await cursor.execute(
                        "SELECT * from problems WHERE guild_id = ? AND problem_id = ?",
                        (guild_id, problem_id),
                    )
                    rows = await cursor.fetchall()
                    if len(rows) == 0:
                        raise ProblemNotFound("Problem not found!")
                    elif len(rows) > 1:
                        raise TooManyProblems(
                            f"{len(rows)} problems exist with the same guild_id and problem_id, not 1"
                        )
                    await conn.commit()
                    if isinstance(rows[0], sqlite3.Row):
                        row = dict_factory(cursor, rows[0])  #
                    else:
                        row = rows[0]
                    return BaseProblem.from_row(rows[0], cache=copy(self))
            else:
                with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
                ) as connection:
                    cursor = connection.cursor(dictionaries=True)
                    cursor.execute(
                        "SELECT * from problems WHERE guild_id = %i AND problem_id = %i"
                    )  # Get the problem
                    rows = cursor.fetchall()
                    if len(rows) == 0:
                        raise ProblemNotFound("Problem not found!")
                    elif len(rows) > 1:
                        raise TooManyProblems(
                            "Uh oh... 2 problems exist with the same guild id and the same problem id"
                        )
                    return BaseProblem.from_row(cache=copy(self), row=rows[0])

    async def get_guild_problems(
        self, Guild: disnake.Guild
    ) -> typing.List[BaseProblem]:
        """Gets the guild problems! Guild must be a Guild object. If you are trying to get global problems, use get_global_problems."""
        assert isinstance(Guild, disnake.Guild)
        if self.update_cache_by_default_when_requesting:
            await self.update_cache()
        try:
            return self.guild_problems[Guild.id]
        except KeyError:
            return {}

    async def get_problems_by_guild_id(self, id: int) -> typing.List[BaseProblem]:
        if not isinstance(id, int) and id is not None:
            raise AssertionError

        if id == None:
            return await self.get_global_problems()
        try:
            return self.guild_problems[id]
        except KeyError:
            return {}

    async def get_global_problems(self: "MathProblemCache"):
        "Returns global problems"
        if self.update_cache_by_default_when_requesting:
            await self.update_cache()
        return self.global_problems

    def add_empty_guild(self, Guild) -> None:
        "Adds an dictionary that is empty for the guild. Guild must be a disnake.Guild object"
        warnings.warn("Deprecated method: add_empty_guild", DeprecationWarning)
        pass  # No longer needed
        # if not isinstance(Guild, disnake.Guild):
        #    raise TypeError("Guild is not actually a Guild")
        # try:
        #    if self._dict[str(Guild.id)] != {}:
        #        raise GuildAlreadyExistsException
        # except KeyError:
        #    self._dict[str(Guild.id)] = {}
        #
        # self._dict[Guild.id] = {}

    async def add_problem(
        self, guild_id: int, problem_id: int, Problem: BaseProblem
    ) -> Optional[BaseProblem]:
        "Adds a problem and returns the added MathProblem"
        # Preliminary checks -otherwise SQL bugs
        if not isinstance(guild_id, int) and guild_id is not None:
            if self.warnings:
                warnings.warn(
                    "guild_id is not an integer.... this may cause an exception"
                )
            else:
                raise TypeError("guild_id is not a integer!")
        if not isinstance(problem_id, int):
            if self.warnings:
                warnings.warn(
                    "problem_id is not a integer.... this may cause an exception"
                )
            else:
                raise TypeError("problem_id is not a integer.")

        # Make sure the problem does not exist!
        try:
            if (await self.get_problem(guild_id, problem_id)) is not None:
                raise MathProblemsModuleException(
                    "Problem already exists! Use update_problem instead"
                )
        except ProblemNotFound:  # an exception raised when the problem does not exist! That means we're good to add the problem!
            pass
        if (
            self.update_cache_by_default_when_requesting
        ):  # Used to determine whether it has reached the limit! Takes O(N) time
            self.update_cache()
        try:
            if (
                guild_id == None
            ):  # There is no limit for global problems (which could be exploited!)
                pass
            elif (
                len(self.guild_problems[guild_id]) >= self.max_guild_problems
            ):  # Make sure this doesn't go over the max guild problem limit (which is 150)
                raise TooManyProblems(
                    f"There are already {self.max_guild_problems} problems!"
                )
        except KeyError:  # New guild creating first problem
            pass
        if not isinstance(
            Problem, (BaseProblem)
        ):  # Make sure it's actually a Problem and not something else
            raise TypeError("Problem is not a valid Problem object.")
        # All the checks passed, hooray! Now let's add the problem.
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:

                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for nameerror
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception
                cursor = conn.cursor()
                # We will raise if the problem already exists!
                await cursor.execute(
                    """INSERT INTO problems (guild_id, problem_id, question, answer, voters, solvers, author)
                VALUES (?,?,?,?,?,?,?)""",
                    (
                        int(Problem.guild_id),
                        int(Problem.id),
                        Problem.get_question(),
                        pickle.dumps(Problem.get_answers()),
                        pickle.dumps(Problem.get_voters()),
                        pickle.dumps(Problem.get_solvers()),
                        int(Problem.author),
                    ),
                )

                await conn.commit()
            return Problem
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                await cursor.execute(
                    """INSERT INTO problems (guild_id, problem_id, question, answer, voters, solvers, author)
                VALUES (%i,%i,%s,%b,%b,%b,%i)""",
                    (
                        int(Problem.guild_id),
                        int(Problem.id),
                        Problem.get_question(),
                        pickle.dumps(Problem.get_answers()),
                        pickle.dumps(Problem.get_voters()),
                        pickle.dumps(Problem.get_solvers()),
                        int(Problem.author),
                    ),
                )

    async def remove_problem(self, guild_id: int, problem_id: int) -> BaseProblem:
        "Removes a problem. Returns the deleted problem"
        Problem = await self.get_problem(guild_id, problem_id)
        await self.remove_problem_without_returning(guild_id, problem_id)
        return Problem

    async def remove_problem_without_returning(
        self, guild_id: int, problem_id: int
    ) -> None:
        "Remove a problem without returning! Saves time."
        if not isinstance(guild_id, int) and guild_id is not None:
            if self.warnings:
                warnings.warn(
                    "guild_id is not a integer. There might be an error...", Warning
                )
            else:
                raise TypeError("guild_id is not a integer")
        if not isinstance(problem_id, int):
            if self.warnings:
                warnings.warn("problem_id isn't an integer")
            else:
                raise TypeError("problem_id isn't an integer!")
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for nameerror
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        raise SQLException("Uh oh")
                    else:
                        raise  # Re-raise the exception
                cursor = conn.cursor()
                await cursor.execute(
                    "DELETE FROM problems WHERE guild_id = %i and problem_id = %i",
                    (guild_id, problem_id),
                )  # The actual deletion
                try:
                    del self.guild_problems[guild_id][
                        problem_id
                    ]  # Delete from the cache
                    await self.update_cache()
                except KeyError:
                    # It's already deleted!
                    pass

                await conn.commit()

        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    "DELETE FROM problems WHERE guild_id = %i and problem_id = %i",
                    (guild_id, problem_id),
                )  # The actual deletion
                connection.commit()
                try:
                    del self.guild_problems[guild_id][
                        problem_id
                    ]  # Delete from the cache
                    await self.update_cache()
                except KeyError:
                    pass

    async def remove_duplicate_problems(self) -> None:
        "Deletes duplicate problems. Takes O(N^2) time which is slow"
        if self.use_sqlite:
            async with aiosqlite.connect(
                self.db_name
            ) as conn:  # Fetch the list of problems
                cursor = conn.cursor()
                await cursor.execute("SELECT * FROM problems")
                all_problems = [
                    BaseProblem.from_row(dict_factory(cursor, row))
                    for row in deepcopy(await cursor.fetchall())
                ]
                await conn.commit()
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                await cursor.execute("SELECT * FROM Problems")
                all_problems = [
                    BaseProblem.from_row(row, cache=copy(self))
                    for row in cursor.fetchall()
                ]
        for problemA in range(len(all_problems)):
            for problemB in range(len(all_problems)):
                if problemA == problemB:  # Same index?
                    pass  # Don't do anything
                if all_problems[problemA] == all_problems[problemB]:
                    await self.remove_problem_without_returning(
                        all_problems[problemA].guild_id, all_problems[problemA].id
                    )  # Delete the problem

    async def get_guilds(
        self, bot: disnake.ext.commands.Bot = None
    ) -> List[Union[int, Optional[disnake.Guild]]]:
        "Get the guilds (due to using sql, it must return the guild id, bot is needed to return guilds. takes O(n) time"
        try:
            assert bot == None or isinstance(bot, disnake.ext.commands.Bot)
        except:
            raise AssertionError("bot isn't a bot!")

        if self.update_cache_by_default_when_requesting:
            await self.update_cache()

        if bot is not None:
            self._guilds = []
            for guild_id in self.guild_ids:
                guild = bot.get_guild(guild_id)  # Get the guild
                if guild is None:  # Guild not found
                    if self.warnings:
                        warnings.warn("guild is None")  # Warn?
                    else:
                        raise RuntimeError(
                            f"Guild not found (id: {guild_id}) :-("
                        )  # Or error
                else:
                    self._guilds.append(guild)
            return self._guilds

        return self.guild_ids

    async def add_quiz(self, quiz: Quiz) -> Quiz:
        "Add a quiz"
        assert isinstance(quiz, Quiz)
        try:
            await self.get_quiz(quiz._id)
            raise MathProblemsModuleException(
                "Quiz already exists! Use update_quiz instead"
            )
        except QuizNotFound:
            pass
        if self.use_sqlite:

            async with aiosqlite.connect(self.db_name) as conn:
                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for nameerror
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception

                cursor = conn.cursor()
                for item in quiz:
                    await cursor.execute(
                        """INSERT INTO quizzes (guild_id, quiz_id, problem_id, question, answer, voters, solvers, author)
                    VALUES (?,?,?,?,?,?,?,?)""",
                        (
                            item.guild_id,
                            item.quiz_id,
                            item.problem_id,
                            item.question,
                            pickle.dumps(item.answers),
                            pickle.dumps(item.voters),
                            pickle.dumps(item.solvers),
                            item.author,
                        ),
                    )
                for item in quiz.submissions:
                    await cursor.execute(
                        """INSERT INTO quiz_submissions (guild_id, quiz_id, user_id, submissions)
                    VALUES (?,?,?,?)""",
                        (
                            item.guild_id,
                            item.quiz_id,
                            item.user_id,
                            pickle.dumps(item.to_dict()),
                        ),
                    )

                await conn.commit()
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)

                cursor = connection.cursor(dictionaries=True)
                for item in quiz:
                    cursor.execute(
                        """INSERT INTO quizzes (guild_id, quiz_id, problem_id, question, answer, voters, solvers, author)
                    VALUES ('%i','%i','%i',%s,%b,%b,%b,'%i')""",
                        (
                            item.guild_id,
                            item.quiz_id,
                            item.problem_id,
                            item.question,
                            pickle.dumps(item.answers),
                            pickle.dumps(item.voters),
                            pickle.dumps(item.solvers),
                            item.author,
                        ),
                    )
                for item in quiz.submissions:
                    cursor.execute(
                        """INSERT INTO quiz_submissions (guild_id, quiz_id, user_id, submissions)
                    VALUES ('%i','%l','%l',%b)""",
                        (
                            item.guild_id,
                            item.quiz_id,
                            item.user_id,
                            pickle.dumps(item.to_dict()),
                        ),
                    )

    def __str__(self):
        raise NotImplementedError

    async def get_quiz(self, quiz_id: int) -> Optional[Quiz]:
        "Get the quiz with the id specified. Returns None if not found"
        assert isinstance(quiz_id, int)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for nameerror
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception
                cursor = conn.cursor()
                await cursor.execute(
                    "SELECT * FROM quizzes WHERE quiz_id=?", (quiz_id,)
                )
                problems = await cursor.fetchall()
                if len(problems) == 0:
                    raise QuizNotFound(f"Quiz id {quiz_id} not found")

                await cursor.execute(
                    "SELECT submissions FROM quiz_submissions WHERE quiz_id = ?"
                )
                submissions = await cursor.fetchall()
                submissions = [
                    QuizSubmission.from_dict(pickle.loads(item), cache=copy(self))
                    for item in submissions
                ]
                problems = [
                    QuizProblem.from_row(dict_factory(cursor, row), cache=copy(self))
                    for row in problems
                ]
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute("SELECT * FROM quizzes WHERE quiz_id = '%i'", (quiz_id,))
                problems = [
                    QuizProblem.from_row(row, copy(self)) for row in cursor.fetchall()
                ]
                cursor.execute(
                    "SELECT * FROM submissions WHERE quiz_id = '%i'", (quiz_id,)
                )
                submissions = [
                    QuizSubmission.from_dict(pickle.loads(row), cache=copy(self))
                    for row in cursor.fetchall()
                ]

        quiz = Quiz(quiz_id, problems, submissions, cache=copy(self))
        return quiz

    async def update_problem(
        self, guild_id: int, problem_id: int, new: BaseProblem
    ) -> None:
        "Update the problem stored with the given guild id and problem id"
        assert isinstance(guild_id, int)
        assert isinstance(problem_id, int)
        assert isinstance(new, BaseProblem) and not isinstance(new, QuizProblem)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for nameerror
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception
                cursor = conn.cursor()
                # We will raise if the problem already exists!
                await cursor.execute(
                    """UPDATE problems 
                    SET guild_id = ?, problem_id = ?, question = ?, answer = ?, voters = ?, solvers = ?, author = ?
                    WHERE guild_id = ? AND problem_id = ?;""",
                    (
                        int(new.guild_id),
                        int(new.id),
                        new.get_question(),
                        pickle.dumps(new.get_answers()),
                        pickle.dumps(new.get_voters()),
                        pickle.dumps(new.get_solvers()),
                        int(new.author),
                        int(guild_id),
                        int(problem_id),
                    ),
                )
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    """UPDATE problems 
                    SET guild_id = '%i', problem_id = '%i', question = %s, answer = %b, voters = %b, solvers = %b, author = '%i'
                    WHERE guild_id = '%i' AND problem_id = '%i'""",
                    (
                        int(new.guild_id),
                        int(new.id),
                        new.question,
                        pickle.dumps(new.get_answers()),
                        pickle.dumps(new.voters),
                        pickle.dumps(new.solvers),
                        int(new.author),
                        guild_id,
                        problem_id,
                    ),
                )

    async def update_quiz(self, quiz_id: int, new: Quiz) -> None:
        "Update the quiz with the id given"
        # Because quizzes consist of multiple rows, it would be hard/impossible to replace each row one at a time
        assert isinstance(quiz_id, int)
        assert isinstance(new, Quiz)
        assert new.id == quiz_id
        await self.delete_quiz(quiz_id)

        await self.add_quiz(Quiz)

    async def delete_quiz(self, quiz_id):
        "Delete a quiz!"
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = conn.cursor()
                await cursor.execute(
                    "DELETE FROM quizzes WHERE quiz_id = ?", (quiz_id,)
                )  # Delete the quiz's problems
                await cursor.execute(
                    "DELETE FROM quiz_submissions WHERE quiz_id=?", (quiz_id)
                )  # Delete the submissions as well.
                await conn.commit()  # Commit
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    "DELETE FROM quizzes WHERE quiz_id = '?'", (quiz_id,)
                )  # Delete the quiz's problems
                cursor.execute(
                    "DELETE FROM quiz_submissions WHERE quiz_id='?'", (quiz_id)
                )  # Delete the submissions as well.

    async def get_all_by_author_id(self, author_id: int) -> dict:
        "Return a dictionary containing everything that was created by the author"
        assert isinstance(author_id, int)  # Make sure it is of type integef
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = await conn.cursor()  # Create a cursor
                # Get all quiz problems they made
                await cursor.execute(
                    "SELECT * FROM quizzes WHERE author = ?", (int(author_id),)
                )  # Get all problems made by the author
                quiz_problems_raw = [
                    dict_factory(cursor, row) for row in await cursor.fetchall()
                ]  # Get the results and convert it to a dictionary
                quiz_problems = [
                    QuizProblem.from_row(item, cache=copy(self))
                    for item in quiz_problems_raw
                ]  # Convert the rows into QuizProblems, because these will be easier to use than rows will (and it will also be more readable)

                # Get the submissions now
                await cursor.execute(
                    "SELECT submissions FROM quiz_submissions WHERE user_id = ?",
                    (author_id,),
                )  # Get the submissions
                # Convert them to QuizSubmissions!
                quiz_submissions = [
                    QuizSubmission.from_dict(pickle.loads(item))
                    for item in await cursor.fetchall()
                ]  # For each item: load it from bytes into a dictionary and convert the dictionary into a QuizSubmission! However, I should just pickle it directly.

                # Get the problems the author made that are not attached to a quiz
                await cursor.execute(
                    "SELECT * FROM problems WHERE author = ?", (author_id,)
                )
                problems = [
                    BaseProblem.from_row(dict_factory(cursor, row))
                    for row in await cursor.fetchall()
                ]
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute("SELECT * FROM quizzes WHERE author = '%i'", (author_id))
                quiz_problems = [
                    QuizProblem.from_row(row, cache=copy(self))
                    for row in cursor.fetchall()
                ]
                cursor.execute(
                    "SELECT submissions FROM quiz_submissions WHERE user_id = '%i'",
                    (author_id),
                )
                quiz_submissions = [
                    QuizSubmission.from_dict(submission, cache=copy(self))
                    for submission in [
                        pickle.loads(item["submissions"]) for item in cursor.fetchall()
                    ]
                ]
                cursor.execute(
                    "SELECT * FROM problems WHERE author = '%i'", (author_id)
                )
                problems = [
                    BaseProblem.from_dict(item, cache=copy(self))
                    for item in cursor.fetchall()
                ]

        return {
            "quiz_problems": quiz_problems,
            "quiz_submissions": quiz_submissions,
            "problems": problems,
        }

    async def delete_all_by_user_id(self, user_id: int) -> None:
        "Delete all data stored under a given user id"
        assert isinstance(user_id, int)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                cursor = conn.cursor()
                await cursor.execute(
                    "DELETE FROM problems WHERE author = ?", (user_id,)
                )  # Delete all problems submitted by the author
                await cursor.execute(
                    "DELETE FROM quizzes WHERE author = ?", (user_id)
                )  # Delete all quiz problems submitted by the author
                await cursor.execute(
                    "DELETE FROM quiz_submissions WHERE user_id = ?", (user_id)
                )  # Delete all quiz submissions created by the author
                await conn.commit()  # Otherwise, nothing happens and it rolls back!!
        else:
            with mysql_connection(
                host=self.mysql_db_ip,
                password=self.mysql_password,
                user=self.mysql_username,
                database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute("DELETE FROM problems WHERE author = '%i'", (user_id,))
                cursor.execute("DELETE FROM quizzes WHERE author = '%i'", (user_id,))
                cursor.execute(
                    "DELETE FROM quiz_submissions WHERE author = '%i'", (user_id)
                )
                connection.commit()

    async def delete_all_by_guild_id(self, guild_id: int) -> None:
        "Delete all data stored by a given guild. This deletes all problems & quizzes & quiz submissions under that guild!"
        if guild_id is None:
            raise MathProblemsModuleException(
                "You are not allowed to delete global problems!"
            )
        assert isinstance(guild_id, int)
        async with aiosqlite.connect(self.db) as conn:
            cursor = conn.cursor()
            await cursor.execute(
                "DELETE FROM problems WHERE guild_id = ?", (guild_id,)
            )  # Delete all problems from the guild
            await cursor.execute(
                "DELETE FROM quizzes WHERE guild_id = ?", (guild_id)
            )  # Delete all quiz problems from the guild
            await cursor.execute(
                "DELETE FROM quiz_submissions WHERE guild_id = ?", (guild_id)
            )  # Delete all quiz submissions from the guild!
            await conn.commit()  # Otherwise, nothing happens!

    def __bool__(self):
        "Return bool(self)"
        return True
