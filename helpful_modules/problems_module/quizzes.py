import sqlite3
import sys
import traceback
from typing import *

from .base_problem import BaseProblem
from .errors import *


class QuizSubmissionAnswer:
    """A class that represents an answer for a singular problem"""

    def __init__(self, answer: str = "", problem_id: int = None, quiz_id: int = 10):
        self.answer = answer
        self.problem_id = problem_id
        self.grade = 0
        self.quiz_id = quiz_id

    def set_grade(self, grade):
        self.grade = grade

    def __str__(self):
        return f"<QuizSubmission quiz_id = {self.quiz_id} answer = {self.answer} grade = {self.grade}>"


class QuizSubmission:
    """A class that represents someone's submission to a graded quiz"""

    def __init__(self, user_id, quiz_id, cache):
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.mutable = True
        self.answers = [
            QuizSubmissionAnswer(problem_id=question.id, quiz_id=quiz_id)
            for question in self.get_my_quiz()
        ]
        self.cache = cache

    @property
    def quiz(self):
        """Return my quiz!"""
        return self.get_my_quiz()

    def get_my_quiz(self):
        """Return my Quiz!"""
        return self.cache.get_quiz(self.quiz_id)

    def set_answer(self, problem_id: int, answer: str) -> None:
        """Set the answer of a quiz problem"""
        if not self.mutable:
            raise RuntimeError("This instance is not mutable")
        for problem_answer in self.answers:
            if problem_answer.problem_id == problem_id:
                problem_answer.answer = answer

    def to_dict(self):
        t = {
            "mutable": self.mutable,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "answer": [],
        }
        for answer in self.answers:
            t["answer"].append(
                {"problem_id": answer.problem_id, "answer": answer.answer}
            )
        return t

    @classmethod
    def from_dict(cls, dict_, cache) -> "QuizSubmission":
        """Convert a dictionary into a QuizSubmission"""
        c = cls(user_id=dict_["user_id"], quiz_id="quiz_id", cache=cache)
        for answer in dict_["answers"]:
            c.answers.append(
                QuizSubmissionAnswer(answer["answer"], problem_id=answer["problem_id"])
            )
        c.mutable = dict_["mutable"]
        return c

    def submit(self) -> True:
        self.mutable = False
        if self in self.quiz.submissions:
            raise QuizAlreadySubmitted
        self.quiz.submissions.append(self)
        return True


class QuizProblem(BaseProblem):
    """A class that represents a Quiz Math Problem"""

    def __init__(
        self,
        question: str,
        id: int,
        author: int,
        answer: str = "",
        guild_id: int = None,
        voters: List[int] = None,
        solvers: List[int] = None,
        cache=None,
        answers: List[str] = None,
        is_written: bool = False,
        quiz_id: int = None,
        max_score: int = -1,
        quiz=None,
    ):
        """A method that allows the creation of new QuizMathProblems"""
        if not isinstance(quiz, Quiz):
            raise TypeError(
                f"quiz is of type {quiz.__class.__name}, not Quiz"
            )  # Here to help me debug
        if voters is None:
            voters = []
        if solvers is None:
            solvers = []
        if answers is None:
            answers = []
        super().__init__(
            question, answer, id, author, guild_id, voters, solvers, cache, answers
        )  #
        self.is_written = is_written
        if quiz is not None:
            self.quiz_id = quiz.id
        else:
            self.quiz_id = quiz_id
        self.max_score = max_score
        self.min_score = 0
        self.cache = cache

    @property
    def quiz(self):
        """Return my quiz"""
        if self.cache is None:
            return None  # I don't have a cache to get my quiz from!
        else:
            return self.cache.get_quiz(self.quiz_id)

    def edit(
        self,
        question=None,
        answer=None,
        id=None,
        guild_id=None,
        voters=None,
        solvers=None,
        author=None,
        answers=None,
        is_written=None,
        quiz=None,
        max_score: int = -1,
    ):
        """Edit a problem!"""
        super().edit(question, answer, id, guild_id, voters, solvers, author, answers)
        if not isinstance(quiz, Quiz):
            raise TypeError(
                f"quiz is of type {quiz.__class.__name}, not Quiz"
            )  # Here to help me debug
        if self.cache:
            self.cache.update_quiz(self.quiz_id, quiz)
        if not isinstance(is_written, bool):
            raise TypeError("is_written is not of type bool")
        self.update_self()

    def to_dict(self, show_answer: bool = False):
        d = {
            "type": "QuizMathProblem",
            "question": self.question,
            "id": str(self.id),
            "guild_id": str(self.guild_id),
            "voters": self.voters,
            "solvers": self.solvers,
            "author": self.author,
            "quiz_id": self.quiz_id,
            "is_written": self.is_written,
            "max_score": self.max_score,
        }
        if show_answer:
            d["answer"] = self.answers
        return d

    @classmethod
    def from_dict(cls, _dict: dict, cache=None):
        """Convert a dictionary to a QuizProblem. Even though the bot uses SQL, this is used in the from_row method"""
        _dict.pop("type")
        return cls(**_dict, cache=cache)

    @classmethod
    def from_row(cls, row: dict, cache=None):
        if isinstance(row, sqlite3.Row):
            raise TypeError("Oh no.")
        try:
            _dict = {
                "quiz_id": row["quiz_id"],
                "guild_id": row["guild_id"],
                "voters": row["voters"],
            }
            return cls.from_dict(_dict, cache=cache)
        except BaseException as e:
            traceback.print_exception(
                type(e), e, e.__traceback__, file=sys.stderr
            )  # Log to stderr
            raise MathProblemsModuleException(
                "Oh no... conversion from row failed"
            ) from e  # Re-raise (which wil log)

    def update_self(self):
        """Update myself"""
        if self.cache is not None:
            self.quiz.update_self()


class Quiz(list):
    """Represents a quiz.
    but it has an additional attribute submissions which is a list of QuizSubmissions"""

    def __init__(
        self,
        id: int,
        authors: List[int],
        quiz_problems: List[QuizProblem],
        submissions: List[QuizSubmission] = None,
        cache=None,
    ) -> None:
        """Create a new quiz. id is the quiz id and iter is an iterable of QuizMathProblems"""
        assert isinstance(authors, list)
        self.authors = authors
        if not submissions:
            submissions = []
        self.problems = quiz_problems
        self.sort(key=lambda problem: problem.id)

        self._cache = cache
        self._submissions = submissions
        self._id = id

    async def add_submission(self, submission: QuizSubmission):
        assert isinstance(submission, QuizSubmission)
        submission.mutable = False
        self._submissions.append(submission)
        await self.update_self()

    @property
    def submissions(self):
        return self._submissions

    @property
    def id(self):
        return self._id

    @classmethod
    def from_dict(cls, _dict: dict):
        problems_as_type = []
        submissions = []
        Problems = _dict["problems"]
        for p in Problems:
            problems_as_type.append(QuizProblem.from_dict(p))
        problems_as_type.sort(key=lambda problem: problem.id)

        for s in _dict["submissions"]:
            submissions.append(QuizSubmission.from_dict(s))
        c = cls(quiz_problems=problems_as_type, id=_dict["id"])
        c._submissions = submissions
        c._id = _dict["id"]
        return c

    def to_dict(self) -> dict:
        """Convert this instance into a Dictionary!"""
        problems = [problem.to_dict() for problem in self.problems]
        submissions = [submission.to_dict for submission in self.submissions]
        return {"problems": problems, "submissions": submissions, "id": self._id}

    async def update_self(self):
        """Update myself!"""
        await self._cache.update_quiz(self._id, self)
