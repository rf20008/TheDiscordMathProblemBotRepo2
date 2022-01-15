import asyncio
import logging
import pickle
import sqlite3
import typing
import warnings
from copy import copy, deepcopy
from types import FunctionType
from typing import *

import aiosqlite
import disnake

from helpful_modules.dict_factory import dict_factory
from helpful_modules.threads_or_useful_funcs import get_log

from .base_problem import BaseProblem
from .errors import *
from .mysql_connector_with_stmt import *
from .quizzes import Quiz, QuizProblem, QuizSolvingSession, QuizSubmission
from .user_data import UserData

log = get_log(__name__)
log.setLevel(logging.NOTSET)


class MathProblemCache:
    """A class that stores math problems/quizzes :-). This makes my code much more readable."""

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
            max_answers_per_problem: int = 25,
            max_problems_per_quiz: int = 50,
            max_quizzes_per_guild: int = 50,
            warnings_or_errors: Union[Literal["warnings"], Literal["errors"]] = "warnings",
            db_name: str = "problems_module.db",
            update_cache_by_default_when_requesting: bool = True,
            use_cached_problems: bool = False,
    ):
        """Create a new MathProblemCache. The arguments should be self-explanatory.
        Many methods are async!"""
        log.info("Initializing the MathProblemCache object.")
        # make_sql_table([], db_name = sql_dict_db_name)
        # make_sql_table([], db_name = "MathProblemCache1.db", table_name="kv_store")
        if use_sqlite:
            warnings.warn("Sqlite has been deprecated. Use MySQL instead.")
        self.db_name = db_name
        self.db = db_name
        if warnings_or_errors not in ["warnings", "errors"]:
            log.critical("Uh oh; warnings_or_errors is bad")
            raise ValueError(
                f"warnings_or_errors is {warnings_or_errors}, not 'warnings' or 'errors'"
            )
        self.warnings = (
                warnings_or_errors == "warnings"
        )  # Whether to raise TypeErrors or warn
        if max_answers_per_problem < 1:
            raise ValueError("max_answers_per_problem must be at least 1!")
        self._max_answers_per_problem = max_answers_per_problem
        self.use_sqlite = use_sqlite
        self.use_cached_problems = use_cached_problems
        self._max_answer_length = max_answer_length
        self._max_question_length = max_question_limit
        self._max_guild_limit = max_guild_problems
        self.mysql_username = mysql_username
        self.max_quizzes_per_guild = max_quizzes_per_guild
        self.max_problems_per_quiz = max_problems_per_quiz
        self.mysql_password = mysql_password
        self.mysql_db_ip = mysql_db_ip
        self.mysql_db_name = mysql_db_name
        asyncio.run(
            self.initialize_sql_table()
        )  # Initialize the SQL tables (but asyncio.run() has to be used because __init__ cannot be async)
        self.update_cache_by_default_when_requesting = (
            update_cache_by_default_when_requesting
        )
        self.guild_ids = []
        self.global_problems = {}
        self.cached_submissions = []
        self.cached_quizzes = []
        self.guild_problems = {}
        self._guilds: typing.List[disnake.Guild] = []
        asyncio.run(self.update_cache())

    async def initialize_sql_table(self):
        """Initialize my internal SQL tables. This does nothing if the internal SQL tables already exist!"""
        log.info("Initializing my internal SQL tables")
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
                )  # Blob types will be compiled with pickle.loads() and pickle.dumps() (they are lists)
                # author: int = user_id
                # Create table of problems
                log.debug("Created problems table")
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
                log.debug("Created quizzes table")
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quiz_submissions (
                    guild_id INT,
                    quiz_id INT NOT NULL,
                    user_id INT NOT NULL,
                    submissions BLOB NOT NULL
                    )"""
                )  # as dictionary
                # Used to store submissions!
                log.debug("Created submissions table")
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS user_data (
                    USER_ID INT,
                    trusted INT NOT NULL,
                    blacklisted INT NOT NULL)"""  # will use bool(val) because SQLite doesn't support booleans
                )
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quiz_submission_sessions (
                    quiz_id INT NOT NULL,
                    user_id INT NOT NULL,
                    is_finished INT,
                    start_time INT,
                    expire_time INT,
                    guild_id INT,
                    answers BLOB,
                    special_id INT
                    )"""
                )  # Special_id is for avoiding the weird bug with 'and' not working in SQL statements
                log.debug("Created user_data table")
                await conn.commit()  # Otherwise, when this closes, the database just reverted!
                log.debug("Saved!")
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                log.debug("Created cursor")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS problems (
                        guild_id BIGINT,
                        problem_id BIGINT NOT NULL,
                        question TEXT(2000) NOT NULL,
                        answers BLOB NOT NULL, 
                        author BIGINT NOT NULL,
                        voters BLOB NOT NULL,
                        solvers BLOB NOT NULL
                        )"""
                )  # Blob types will be compiled with pickle.loads() and pickle.dumps() (they are lists)
                # author: int = user_id
                log.debug("Created problems table!")
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
                log.debug("Created quizzes table")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quiz_submissions (
                    guild_id BIGINT,
                    quiz_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    submissions BLOB NOT NULL
                    )"""
                )  # as dictionary
                # Used to store submissions
                log.debug("Created submissions table")
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS user_data (
                    user_id INT,
                    trusted BOOLEAN DEFAULT false,
                    blacklisted BOOLEAN DEFAULT false
                    )"""
                )
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS quiz_submission_sessions (
                    quiz_id INT NOT NULL,
                    user_id INT NOT NULL,
                    is_finished INT,
                    start_time INT,
                    expire_time INT,
                    guild_id INT,
                    answers BLOB,
                    special_id INT
                    )"""
                )
                log.debug("Created user data table")
                connection.commit()
                log.debug("Saved tables!")

    async def get_user_data(
            self, user_id: int, default: typing.Optional[UserData] = None
    ):
        log.debug(
            f"get_user_data method called. user_id: {user_id}, default: {default}"
        )
        assert isinstance(user_id, int)
        assert isinstance(default, UserData) or default is None or default == Exception
        if default is None:
            default = UserData(user_id=user_id, trusted=False, blacklisted=False)
            # To avoid mutable default arguments
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute(
                    "SELECT * FROM user_data WHERE user_id = ?", (user_id,)
                )  # Select the data
                cursor_results = list(await cursor.fetchall())
                log.debug(f"Data selected (results: {cursor_results})")
                if len(cursor_results) == 0:
                    return default
                elif len(cursor_results) == 1:

                    dict_to_use = cursor_results[0]
                    dict_to_use["trusted"] = bool(dict_to_use["trusted"])
                    dict_to_use["blacklisted"] = bool(dict_to_use["blacklisted"])
                    dict_to_use["user_id"] = int(dict_to_use["USER_ID"])
                    log.debug("Data successfully returned!")
                    return UserData.from_dict(dict_to_use)
                else:
                    raise TooMuchUserDataException(
                        f"Too much user data; found {len(cursor_results)} results; expected either 1 or 0"
                    )
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                log.debug("Connected to MySQL")
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    "SELECT * FROM user_data WHERE USER_ID=%s",
                    (user_id,),  # TODO: fix placeholders
                )
                results = list(cursor.fetchall())
                if len(results) == 0:
                    return default
                elif len(results) == 1:
                    results[0]["user_id"] = results[0]["USER_ID"]
                    return UserData.from_dict(results[0])
                else:
                    try:
                        raise TooMuchUserDataException(
                            f"Too much user data; found {len(results)} results;    expected either 1 or 0"
                        )
                    except NameError:
                        raise MathProblemsModuleException("Too much user data found.")

    async def set_user_data(self, user_id: int, new: UserData) -> None:
        """Set the user_data of a user."""
        assert isinstance(user_id, int)
        assert isinstance(new, UserData)
        if (await self.get_user_data(user_id=user_id, default=Exception)) != Exception:
            raise UserDataNotExistsException(
                "User data does not exist! Use add_user_data instead"
            )
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                log.debug("Connected to SQLite!")
                conn.row_factory = dict_factory
                blacklisted_int = int(new.blacklisted)
                trusted_int = int(new.trusted)
                cursor = await conn.cursor()
                await cursor.execute(
                    """UPDATE user_data 
                SET user_id=?, blacklisted=?, trusted=?
                WHERE user_id=?;""",
                    (user_id, blacklisted_int, trusted_int, user_id),
                )
                await conn.commit()
                log.debug("Finished!")
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                log.debug("Connected to MySQL")
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    """UPDATE user_id
                   SET user_id = %s, trusted=%s, blacklisted=%s
                   WHERE user_id = %s""",
                    (user_id, new.trusted, new.blacklisted, user_id),
                )
                connection.commit()
                log.debug("Finished!")
                return

    async def add_user_data(self, user_id: int, thing_to_add: UserData) -> None:
        assert isinstance(user_id, int)
        assert isinstance(thing_to_add, UserData)
        if (await self.get_user_data(user_id, default=Exception)) != Exception:  # type: ignore
            # This is because the user_id is None. Then it will return the default instead
            raise MathProblemsModuleException(
                "User data already exists"
            )  # Make sure the user data doesn't already exist
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """INSERT INTO user_data (user_id, trusted, blacklisted)
                VALUES (?,?,?)""",
                    (user_id, thing_to_add.trusted, thing_to_add.blacklisted),
                )  # add the user data
                await conn.commit()
                log.debug("Finished adding user data!")
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    """INSERT INTO user_data (user_id, trusted, blacklisted)
                VALUES (%s, %s, %s)""",
                    (user_id, thing_to_add.trusted, thing_to_add.blacklisted),
                )
                connection.commit()

    async def del_user_data(self, user_id: int):
        """Delete user data given the user id"""
        assert isinstance(user_id, int)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    "DELETE FROM user_data WHERE user_id = ?", (user_id,)
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
                cursor.execute("DELETE FROM user_data WHERE user_id = %s", (user_id,))
                connection.commit()
                connection.close()

    @property
    def max_answer_length(self):
        return self._max_answer_length

    @property
    def max_question_length(self):
        return self._max_question_length

    @property
    def max_guild_problems(self):
        return self._max_guild_limit

    @property
    def max_answers_per_problem(self):
        return self._max_answers_per_problem

    async def convert_to_dict(self) -> dict:
        """A method that converts self to a dictionary (not used, will probably be removed soon)"""
        e = {}
        await self.update_cache()

        for guild_id in self.guild_ids:
            e[guild_id] = {}
            for Problem in self.guild_problems[guild_id]:
                e[guild_id][Problem.id] = Problem.to_dict()
        return e

    # TODO: finish logging
    def convert_dict_to_math_problem(self, problem: dict, use_from_dict: bool = True):
        """Convert a dictionary into a math problem. It must be in the expected format. (Overridden by from_dict, but still used) Possibly not used due to SQL."""
        if use_from_dict:
            return BaseProblem.from_dict(
                problem, cache=self
            )  # Use the base problem.from_dict method
        try:
            assert isinstance(problem, dict)
        except AssertionError:
            raise TypeError("problem is not actually a Dictionary")
        guild_id = problem["guild_id"]
        if guild_id is not None:
            guild_id = int(guild_id)
        problem2 = BaseProblem(  # Create the problem
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
        """Method revamped! This method updates the cache of the guilds, the guild problems, and the cache of the global problems. Takes O(N) time"""
        guild_problems = {}
        guild_ids = []
        quiz_problems_dict = {}
        quiz_submissions_dict = {}
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute("SELECT * FROM problems")  # Get all problems
                for row in await cursor.fetchall():  # For each problem:
                    if not isinstance(row, dict):
                        problem = BaseProblem.from_row(
                            pickle.loads(row), cache=copy(self)
                        )  # Convert the problems to problem objects
                    else:
                        problem = BaseProblem.from_row(row=row, cache=copy(self))
                    if (
                            problem.guild_id not in guild_ids
                    ):  # Similar logic: Make sure it's there!
                        guild_ids.append(problem.guild_id)
                        guild_problems[
                            problem.guild_id
                        ] = {}  # For quick, cached access?
                    try:
                        guild_problems[problem.guild_id][problem.id] = problem
                    except BaseException as e:
                        raise SQLException(
                            "The cache could not be updated because assigning the problem failed!"
                        ) from e
                    await cursor.execute("SELECT * FROM quizzes")
                    for Row in await cursor.fetchall():
                        quiz_problem = QuizProblem.from_row(Row, cache=copy(self))
                        # Add the problem to the cache
                        try:
                            quiz_problems_dict[quiz_problem.id].append(quiz_problem)
                        except KeyError:
                            quiz_problems_dict[quiz_problem.id] = [quiz_problem]
                    await cursor.execute("SELECT submissions from quiz_submissions")
                    for Row in await cursor.fetchall():
                        submission = QuizSubmission.from_dict(
                            pickle.loads(Row["submission"]), cache=copy(self)
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
                    problem = BaseProblem.from_row(row, cache=copy(self))
                    if (
                            problem.guild_id not in guild_ids
                    ):  # Similar logic: Make sure it's there!
                        guild_ids.append(problem.guild_id)
                        guild_problems[
                            problem.guild_id
                        ] = {}  # For quick, cached access?
                    try:
                        guild_problems[problem.guild_id][problem.id] = problem
                    except BaseException as e:
                        raise SQLException(
                            "An error occurred while assigning the problem..."
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
                        pickle.loads(row["submission"]), cache=copy(self)
                    )
                    try:
                        quiz_submissions_dict[submission.quiz_id].append(submission)
                    except KeyError:
                        quiz_submissions_dict[submission.quiz_id] = [submission]

        try:
            global_problems = deepcopy(
                guild_problems[None]
            )  # Must deepcopy or weird warnings will occur
            # TODO: fix this so this doesn't lead to errors
        except KeyError:  # No global problems yet
            global_problems = {}
        # Don't deepcopy the problems
        self.guild_problems = guild_problems
        self.guild_ids = guild_ids
        self.global_problems = global_problems
        self.cached_quizzes = []  # Could cause a race condition
        for _id in quiz_problems_dict.keys():
            has_submissions = _id in list(
                quiz_submissions_dict.keys()
            )  # There could be a quiz with problems but not submissions
            if has_submissions:
                self.cached_quizzes.append(
                    Quiz(
                        _id,
                        quiz_problems=quiz_problems_dict[_id],
                        submissions=quiz_submissions_dict[_id],
                        authors=set(
                            (problem.author for problem in quiz_submissions_dict[_id])
                        ),
                    )
                )

            else:
                self.cached_quizzes.append(
                    Quiz(
                        _id,
                        quiz_problems=quiz_problems_dict[_id],
                        submissions=[],
                        authors=set(
                            (problem.author for problem in quiz_submissions_dict[_id])
                        ),
                    )
                )
        self.cached_submissions = quiz_submissions_dict.values()

    async def get_quizzes_by_func(
            self: "MathProblemCache",
            func: typing.Callable[[Quiz, Any], bool] = lambda quiz: False,
            args: typing.Union[tuple, list] = None,
            kwargs: dict = None,
    ) -> typing.List[Quiz]:
        """Get the quizzes that match the function.
        Function is a function that takes in the quiz, and the provided arguments and keyword arguments.
        Return something True-like to signify you want the quiz in the list, and False-like to signify you don't."""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        await self.update_cache()
        return [quiz for quiz in self.cached_quizzes if func(quiz, *args, **kwargs)]  # type: ignore

    async def get_problems_by_func(
            self: "MathProblemCache",
            func: FunctionType = lambda problem: False,
            args: typing.Optional[typing.Union[tuple, list]] = None,
            kwargs: Optional[dict] = None,
    ) -> typing.List[BaseProblem]:
        """Returns the list of all problems that match the given function. args and kwargs are extra parameters to give to the function"""
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        await self.update_cache()
        guild_problems = []
        for item in self.guild_problems.values():
            guild_problems.extend(
                item.values()
            )  # This could be a list comprehension (but it creates the list of guild problems)
        global_problems_that_meet_the_criteria = [
            problem
            for problem in self.global_problems.values()
            if func(problem, *args, **kwargs)  # type: ignore
        ]
        guild_problems_that_meet_the_criteria = [
            problem for problem in guild_problems if func(problem, *args, **kwargs)  # type: ignore
        ]
        problems_that_meet_the_criteria = global_problems_that_meet_the_criteria
        problems_that_meet_the_criteria.extend(guild_problems_that_meet_the_criteria)
        return problems_that_meet_the_criteria

    async def get_problem(
            self, guild_id: typing.Optional[int], problem_id: int
    ) -> BaseProblem:
        """Gets the problem with this guild id and problem id. If the problem is not found, a ProblemNotFound exception will be raised."""
        # This isn't working
        # Possible causes:
        # The item is of the wrong type
        # Wrong database/table / a SQL feature that I didn't know about
        # Searching by NULL
        log.debug(
            f"Type of guild_id & problem_id: guild_id: {type(guild_id)} {guild_id}, problem_id: {type(problem_id)} {problem_id}"
        )
        assert isinstance(guild_id, int) or guild_id is None
        # The problem: where doesn't work with an 'and' clause
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
                try:
                    return self.global_problems[problem_id]  # global problem?
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
                    except Exception as e:
                        raise MathProblemsModuleException(f"Oh no{'!' * 30}") from e
                    # Theory: the sql statement is not the problem
                    cursor = await conn.cursor()
                    log.debug(
                        f"Getting the problem with guild id {guild_id} and problem_id {problem_id} (types: {type(guild_id)}, {type(problem_id)})"
                    )
                    log.debug("Expected SQL statement:")
                    log.warning(
                        f"""SELECT * FROM problems
 WHERE problem_id = {problem_id})"""
                    )
                    # The problem is most likely not the SQL statement!
                    r = await cursor.execute(
                        """SELECT * FROM problems WHERE problem_id = ?""",
                        # Not sure if making "from" uppercase will change anything (but it selects the problem from the database)
                        (problem_id,),
                    )
                    log.debug(str(r))
                    rows = list(await cursor.fetchall())
                    log.debug(f"{len(rows)} problems found")
                    if len(rows) == 0:
                        raise ProblemNotFound("Problem not found!")
                    elif len(rows) > 1:
                        log.critical("Uh oh; too many problems!")
                        raise TooManyProblems(
                            f"{len(rows)} problems exist with the same guild_id and problem_id, not 1"
                        )
                    await conn.commit()
                    if isinstance(rows[0], sqlite3.Row):
                        row = dict_factory(cursor, rows[0])  #
                    else:
                        row = rows[0]
                    return BaseProblem.from_row(row, cache=copy(self))
            else:
                with mysql_connection(
                        host=self.mysql_db_ip,
                        password=self.mysql_password,
                        user=self.mysql_username,
                        database=self.mysql_db_name,
                ) as connection:
                    cursor = connection.cursor(dictionaries=True)
                    cursor.execute(
                        "SELECT * from problems WHERE problem_id = %s", (problem_id,)
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
            self, guild: disnake.Guild
    ) -> typing.Dict[int, BaseProblem]:
        """Gets the guild problems! Guild must be a Guild object. If you are trying to get global problems, use get_global_problems."""
        assert isinstance(guild, disnake.Guild)
        if self.update_cache_by_default_when_requesting:
            await self.update_cache()
        try:
            return self.guild_problems[guild.id]
        except KeyError:
            return {}

    async def get_problems_by_guild_id(
            self, guild_id: int
    ) -> typing.Dict[int, BaseProblem]:
        if not isinstance(guild_id, int) and guild_id is not None:
            raise AssertionError

        if guild_id is None:
            return await self.get_global_problems()
        try:
            return self.guild_problems[guild_id]
        except KeyError:
            return {}

    async def get_global_problems(self: "MathProblemCache") -> typing.List[BaseProblem]:
        """Returns global problems"""
        if self.update_cache_by_default_when_requesting:
            await self.update_cache()
        return self.global_problems

    def add_empty_guild(self, guild) -> typing.NoReturn:
        """Adds a dictionary that is empty for the guild. Guild must be a disnake.Guild object"""
        raise MathProblemsModuleException(
            "This method has been removed and you should not use it! It doesn't have a purpose anyway!"
        )
        # No longer needed
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
            self, problem_id: int, problem: BaseProblem
    ) -> Optional[BaseProblem]:
        """Adds a problem and returns the added MathProblem"""
        # Preliminary checks -otherwise SQL bugs
        guild_id = problem.guild_id
        if not isinstance(problem_id, int):
            if self.warnings:
                warnings.warn(
                    "problem_id is not a integer.... this may cause an exception"
                )
            else:
                raise TypeError("problem_id is not a integer.")

        # Make sure the problem does not exist!
        try:
            if (await self.get_problem(None, problem_id)) is not None:
                raise MathProblemsModuleException(
                    "Problem already exists! Use update_problem instead"
                )
        except ProblemNotFound:  # an exception raised when the problem does not exist! That means we're good to add the problem!
            pass
        if (
                self.update_cache_by_default_when_requesting
        ):  # Used to determine whether it has reached the limit! Takes O(N) time
            await self.update_cache()
        try:
            if (
                    guild_id is None
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
                problem, BaseProblem
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
                        dict_factory  # Check for name error
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception
                cursor = await conn.cursor()
                # We will raise if the problem already exists!
                await cursor.execute(
                    """INSERT INTO problems (guild_id, problem_id, question, answers, voters, solvers, author)
                VALUES (?,?,?,?,?,?,?)""",
                    (
                        problem.guild_id,  # We expect the problem's guild id to be either an integer or None
                        int(problem.id),
                        problem.get_question(),
                        pickle.dumps(problem.get_answers()),
                        pickle.dumps(problem.get_voters()),
                        pickle.dumps(problem.get_solvers()),
                        int(problem.author),
                    ),
                )

                await conn.commit()
            return problem
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
                VALUES (%s,%s,%s,%b,%b,%b,%s)""",
                    (
                        int(problem.guild_id),
                        int(problem.id),
                        problem.get_question(),
                        pickle.dumps(problem.get_answers()),
                        pickle.dumps(problem.get_voters()),
                        pickle.dumps(problem.get_solvers()),
                        int(problem.author),
                    ),
                )

    async def remove_problem(
            self, guild_id: typing.Optional[int], problem_id: int
    ) -> BaseProblem:
        """Removes a problem. Returns the deleted problem"""
        Problem = await self.get_problem(guild_id, problem_id)
        await self.remove_problem_without_returning(guild_id, problem_id)
        return Problem

    async def remove_problem_without_returning(
            self,
            guild_id: typing.Optional[int],
            problem_id: int,
    ) -> None:
        """Remove a problem without returning! Saves time."""
        assert isinstance(guild_id, int) or guild_id is None
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
                        dict_factory  # Check for name error
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        raise SQLException("Uh oh")
                    else:
                        raise  # Re-raise the exception
                cursor = await conn.cursor()
                await cursor.execute(
                    "DELETE FROM problems WHERE problem_id = ?",
                    (problem_id,),
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
                    "DELETE FROM problems WHERE problem_id = %s",
                    (problem_id,),
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
        """Deletes duplicate problems. Takes O(N^2) time which is slow"""
        if self.use_sqlite:
            async with aiosqlite.connect(
                    self.db_name
            ) as conn:  # Fetch the list of problems
                cursor = await conn.cursor()
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
                        guild_id=problemB.guild_id, problem_id=[problemA].id
                    )  # Delete the problem

    async def get_guilds(
            self, bot: disnake.ext.commands.Bot = None
    ) -> List[Union[int, Optional[disnake.Guild]]]:
        """Get the guilds (due to using sql, it must return the guild id, bot is needed to return guilds. takes O(n) time)"""
        try:
            assert bot is None or isinstance(bot, disnake.ext.commands.Bot)
        except AssertionError:
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
        """Add a quiz"""
        assert isinstance(quiz, Quiz)
        if not quiz.empty:
            num_already_existing_quizzes = await self.get_quizzes_by_func(
                func=lambda _quiz: not _quiz.empty and _quiz.guild_id == quiz.guild_id  # type: ignore
            )
            if len(num_already_existing_quizzes) >= self.cache.max_quizzes_per_guild:
                raise TooManyQuizzesException(len(num_already_existing_quizzes) + 1)
        try:
            await self.get_quiz(quiz.id)
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
                        dict_factory  # Check for name error
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception

                cursor = await conn.cursor()
                for item in quiz.problems:
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
                for item in quiz.problems:
                    cursor.execute(
                        """INSERT INTO quizzes (guild_id, quiz_id, problem_id, question, answer, voters, solvers, author)
                    VALUES ('%s','%s','%s',%s,%s,%s,%s,'%s')""",
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
                    VALUES ('%s','%s','%s',%s)""",
                        (
                            item.guild_id,
                            item.quiz_id,
                            item.user_id,
                            pickle.dumps(item.to_dict()),
                        ),
                    )
        return quiz

    def __str__(self):
        raise NotImplementedError

    async def get_quiz_sessions(self, quiz_id: int) -> List[QuizSolvingSession]:
        """Get the quiz sessions for a quiz"""
        assert isinstance(quiz_id, int)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute(
                    "SELECT * WHERE quiz_id = ?", (quiz_id,)
                )
                # For each row retrieved: use from_sqlite_dict to turn into a QuizSolvingSession and return it
                return [QuizSolvingSession.from_sqlite_dict(item, cache=self) for item in await cursor.fetchall()]
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute("SELECT * FROM quiz_submission_sessions WHERE quiz_id = %s", (quiz_id,))
                # For each row retrieved: turn it into a QuizSolvingSession using from_mysql_dict and return the result
                return [QuizSolvingSession.from_mysql_dict(item, cache=self) for item in cursor.fetchall()]

    async def add_quiz_session(self, session: QuizSolvingSession):
        """Add a QuizSession to the SQL database"""
        assert isinstance(session, QuizSolvingSession)
        try:
            await self.get_quiz_submission_by_special_id(session.special_id)
            raise MathProblemsModuleException("Quiz session already exists")
        except QuizSessionNotFoundException:
            pass

        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute(
                    """INSERT INTO quiz_submission_sessions (user_id, quiz_id, guild_id, is_finished, answers, start_time, expire_time, special_id)
                    VALUES (?,?,?,?,?,?,?,?)""", (
                        session.user_id,
                        session.quiz_id,
                        session.guild_id,
                        int(session.is_finished),
                        pickle.dumps(session.answers),
                        session.start_time,
                        session.expire_time,
                        session.special_id
                    )
                )
                await conn.commit()
                return
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    """INSERT INTO quiz_submission_sessions (user_id, quiz_id, guild_id, is_finished, answers, start_time, expire_time, special_id)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", (
                        session.user_id,
                        session.quiz_id,
                        session.guild_id,
                        int(session.is_finished),
                        pickle.dumps(session.answers),  # TODO: don't use pickle (because RCE)
                        session.start_time,
                        session.expire_time,
                        session.special_id
                    )
                )
                connection.commit()

    async def update_quiz_session(self, special_id: int, session: QuizSolvingSession):
        """Update the quiz session given the special id"""
        assert isinstance(special_id, int)
        assert isinstance(session, QuizSolvingSession)
        try:
            await self.get_quiz_submission_by_special_id(special_id)
        except QuizSessionNotFoundException as quiz_session_not_found_exception:
            raise QuizSessionNotFoundException("Quiz session not found - use add_quiz_session instead") from quiz_session_not_found_exception

        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute(
                    """UPDATE quiz_submission_sessions 
                    SET guild_id = ?, quiz_id = ?, user_id = ?, answers = ?, start_time = ?, expire_time = ?, is_finished = ?, special_id = ? 
                    WHERE special_id = ?""", (
                        session.guild_id,
                        session.quiz_id,
                        session.user_id,
                        pickle.dumps(session.answers),
                        session.start_time,
                        session.expire_time,
                        int(session.is_finished),
                        session.special_id,
                        session.special_id
                    )
                )
                await conn.commit()
                return
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(  # Connect to SQL and actually change it
                    """UPDATE quiz_submission_sessions 
                    SET guild_id = %s, quiz_id = %s, user_id = %s, answers = %s, start_time = %s, expire_time = %s, is_finished = %s, special_id = %s 
                    WHERE special_id = %s""", (
                        session.guild_id,
                        session.quiz_id,
                        session.user_id,
                        pickle.dumps(session.answers),
                        session.start_time,
                        session.expire_time,
                        int(session.is_finished),
                        session.special_id,
                        session.special_id
                    )
                )
                connection.commit()
                return

    async def get_quiz_session_by_special_id(self, special_id: int) -> QuizSolvingSession:
        "Get a quiz submission by its special id"
        assert isinstance(special_id, int) # Basic type-checking

        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = await conn.cursor()
                await cursor.execute("SELECT * FROM quiz_submission_sessions WHERE special_id = ?", (special_id,))
                potential_sessions = list(await cursor.fetchall())
                if len(potential_sessions) < 1:
                    raise QuizSessionNotFoundException("There aren't any quiz sessions found with this special id")
                elif len(potential_sessions) > 1:
                    raise MathProblemsModuleException("There are too many quiz sessions with this special id")
                else:
                    return QuizSolvingSession.from_sqlite_dict(potential_sessions[0])
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute("SELECT * FROM quiz_submission_sessions WHERE special_id = %s", (special_id,))
                potential_sessions = list(cursor.fetchall())
                if len(potential_sessions) < 1:
                    raise QuizSessionNotFoundException("There aren't any quiz sessions found with this special id")
                elif len(potential_sessions) > 1:
                    raise MathProblemsModuleException("There are too many quiz sessions with this special id")
                else:
                    return QuizSolvingSession.from_mysql_dict(potential_sessions[0])



    async def get_quiz(self, quiz_id: int) -> Optional[Quiz]:
        """Get the quiz with the id specified. Returns None if not found"""
        assert isinstance(quiz_id, int)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for name error
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
                    "SELECT * FROM quizzes WHERE quiz_id=?", (quiz_id,)
                )
                problems = list(await cursor.fetchall())
                if len(problems) == 0:
                    raise QuizNotFound(f"Quiz id {quiz_id} not found")

                await cursor.execute(
                    "SELECT submissions FROM quiz_submissions WHERE quiz_id = ?"
                )
                submissions = await cursor.fetchall()
                submissions = [
                    QuizSubmission.from_dict(pickle.loads(item[0]), cache=copy(self))
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
                cursor.execute("SELECT * FROM quizzes WHERE quiz_id = '%s'", (quiz_id,))
                problems = [
                    QuizProblem.from_row(row, copy(self)) for row in cursor.fetchall()
                ]
                cursor.execute(
                    "SELECT * FROM submissions WHERE quiz_id = '%s'", (quiz_id,)
                )
                submissions = [
                    QuizSubmission.from_dict(pickle.loads(row[0]), cache=copy(self))
                    for row in cursor.fetchall()
                ]
        authors = set((problem.author for problem in problems))
        quiz = Quiz(quiz_id, problems, submissions, cache=copy(self), authors=authors)  # type: ignore
        return quiz

    async def update_problem(self, problem_id: int, new: BaseProblem) -> None:
        """Update the problem stored with the given guild id and problem id. This replaces the problem with the new problem"""
        assert isinstance(problem_id, int)
        assert isinstance(new, BaseProblem) and not isinstance(new, QuizProblem)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                try:
                    conn.row_factory = dict_factory  # Make sure the row_factory can be set to dict_factory
                except BaseException as exc:
                    # Not writeable?
                    try:
                        dict_factory  # Check for name error
                    except NameError as exc2:
                        raise MathProblemsModuleException(
                            "dict_factory could not be found"
                        ) from exc2
                    if isinstance(exc, AttributeError):  # Can't set attribute
                        pass
                    else:
                        raise  # Re-raise the exception
                cursor = await conn.cursor()
                # We will raise if the problem already exists!
                await cursor.execute(
                    """UPDATE problems 
                    SET guild_id = ?, problem_id = ?, question = ?, answers = ?, voters = ?, solvers = ?, author = ?
                    WHERE problem_id = ?;""",
                    (
                        new.guild_id,
                        int(new.id),
                        new.get_question(),
                        pickle.dumps(new.get_answers()),
                        pickle.dumps(new.get_voters()),
                        pickle.dumps(new.get_solvers()),
                        int(new.author),
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
                    SET guild_id = '%s', problem_id = '%s', question = %s, answer = %s, voters = %s, solvers = %s, author = '%s'
                    WHERE AND problem_id = '%s'""",
                    (
                        int(new.guild_id),
                        int(new.id),
                        new.question,
                        pickle.dumps(new.get_answers()),
                        pickle.dumps(new.voters),
                        pickle.dumps(new.solvers),
                        int(new.author),
                        problem_id,
                    ),
                )

    async def update_quiz(self, quiz_id: int, new: Quiz) -> None:
        """Update the quiz with the id given"""
        # Because quizzes consist of multiple rows, it would be hard/impossible to replace each row one at a time
        assert isinstance(quiz_id, int)
        assert isinstance(new, Quiz)
        assert new.id == quiz_id
        await self.delete_quiz(quiz_id)

        await self.add_quiz(new)

    async def delete_quiz(self, quiz_id: int):
        """Delete a quiz!"""
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    "DELETE FROM quizzes WHERE quiz_id = ?", (quiz_id,)
                )  # Delete the quiz's problems
                await cursor.execute(
                    "DELETE FROM quiz_submissions WHERE quiz_id=?", (quiz_id,)
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
                    "DELETE FROM quiz_submissions WHERE quiz_id='?'", (quiz_id,)
                )  # Delete the submissions as well.

    async def get_all_by_author_id(self, author_id: int) -> dict:
        """Return a dictionary containing everything that was created by the author"""
        assert isinstance(author_id, int)  # Make sure it is of type integer
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
                    QuizSubmission.from_dict(pickle.loads(item[0]), cache=copy(self))
                    for item in await cursor.fetchall()
                ]  # For each item: load it from bytes into a dictionary and
                # convert the dictionary into a QuizSubmission! However, I should just pickle it directly.

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
                cursor.execute(
                    "SELECT * FROM quizzes WHERE author = '%s'", (author_id,)
                )
                quiz_problems = [
                    QuizProblem.from_row(row, cache=copy(self))
                    for row in cursor.fetchall()
                ]
                cursor.execute(
                    "SELECT submissions FROM quiz_submissions WHERE user_id = '%s'",
                    (author_id,),
                )
                quiz_submissions = [
                    QuizSubmission.from_dict(submission, cache=copy(self))
                    for submission in [
                        pickle.loads(item["submissions"]) for item in cursor.fetchall()
                    ]
                ]
                cursor.execute(
                    "SELECT * FROM problems WHERE author = '%s'", (author_id,)
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
        """Delete all data stored under a given user id"""
        assert isinstance(user_id, int)
        await self.del_user_data(user_id)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    "DELETE FROM problems WHERE author = ?", (user_id,)
                )  # Delete all problems submitted by the author
                await cursor.execute(
                    "DELETE FROM quizzes WHERE author = ?", (user_id,)
                )  # Delete all quiz problems submitted by the author
                await cursor.execute(
                    "DELETE FROM quiz_submissions WHERE user_id = ?", (user_id,)
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
                cursor.execute("DELETE FROM problems WHERE author = '%s'", (user_id,))
                cursor.execute("DELETE FROM quizzes WHERE author = '%s'", (user_id,))
                cursor.execute(
                    "DELETE FROM quiz_submissions WHERE author = '%s'", (user_id,)
                )
                connection.commit()

    async def delete_all_by_guild_id(self, guild_id: int) -> None:
        """Delete all data stored by a given guild. This deletes all problems & quizzes & quiz submissions under that guild!"""
        if guild_id is None:
            raise MathProblemsModuleException(
                "You are not allowed to delete global problems!"
            )
        assert isinstance(guild_id, int)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    "DELETE FROM problems WHERE guild_id = ?", (guild_id,)
                )  # Delete all problems from the guild
                await cursor.execute(
                    "DELETE FROM quizzes WHERE guild_id = ?", (guild_id,)
                )  # Delete all quiz problems from the guild
                await cursor.execute(
                    "DELETE FROM quiz_submissions WHERE guild_id = ?", (guild_id,)
                )  # Delete all quiz submissions from the guild!
                await conn.commit()  # Otherwise, nothing happens!
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(
                    "DELETE FROM problems WHERE guild_id = %s", (guild_id,)
                )  # Remove all guild problems from this guild
                cursor.execute(
                    "DELETE FROM quizzes WHERE guild_id = %s", (guild_id,)
                )  # Remove all quizzes from the guild
                cursor.execute(
                    "DELETE FROM quiz_submissions WHERE guild_id = ?", (guild_id,)
                )  # Remove all quiz submissions as well
                connection.commit()

    def __bool__(self):
        """Return bool(self)"""
        return True

    async def run_sql(self, sql: str) -> dict:
        """Run arbitrary SQL. Only used in /sql"""
        assert isinstance(sql, str)
        if self.use_sqlite:
            async with aiosqlite.connect(self.db_name) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute(sql)
                await conn.commit()
                return await cursor.fetchall()
        else:
            with mysql_connection(
                    host=self.mysql_db_ip,
                    password=self.mysql_password,
                    user=self.mysql_username,
                    database=self.mysql_db_name,
            ) as connection:
                cursor = connection.cursor(dictionaries=True)
                cursor.execute(sql)
                connection.commit()
                return cursor.fetchall()
