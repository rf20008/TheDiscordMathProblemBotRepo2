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
from .quizzes.quiz_description import QuizDescription
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
        self.cached_submissions_organized_by_dict = None
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
        self.cached_sessions = {}



