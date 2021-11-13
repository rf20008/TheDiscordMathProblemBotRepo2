from typing import List
import pickle
import sys
import traceback
import sqlite3

import nextcord

from .errors import *
from .base_problem import BaseProblem


class QuizSubmissionAnswer:
    "A class that represents an answer for a singular problem"

    def __init__(self, answer: str = "", problem_id: int = None, quiz_id: int = 10):
        self.answer = answer
        self.problem_id = problem_id
        self.grade = 0
        self.quiz_id = quiz_id

    def set_grade(self, grade):
        self.grade = grade

    def __str__(self):
        return str(self.answer)


class QuizSubmission:
    "A class that represents someone's submission to a graded quiz"

    def __init__(self, user: nextcord.User, quiz_id, cache):
        self.user_id = user.id
        self.quiz_id = quiz_id
        self.mutable = True
        self.answers = [
            QuizSubmissionAnswer(problem=question, quiz_id=quiz_id)
            for question in self.get_my_quiz()
        ]
        self.cache = cache

    @property
    def quiz(self):
        "Return my quiz!"
        return self.get_my_quiz()

    def get_my_quiz(self):
        "Return my Quiz!"
        return self.cache.get_quiz(self.quiz_id)

    def set_answer(self, problem_id, Answer) -> None:
        "Set the answer of a quiz problem"
        if not self.mutable:
            raise RuntimeError("This instance is not mutable")
        for answer in self.answers:
            if answer.problem.id == problem_id:
                answer.answer = Answer

    def to_dict(self):
        t = {
            "mutable": self.mutable,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "answer": [],
        }
        for answer in self.answers:
            t["answer"].append(
                {"problem_id": answer.problem.id, "answer": answer.answer}
            )
        return t

    @classmethod
    def from_dict(cls, dict_):
        "Convert a dictionary into a QuizSubmission"
        c = cls(user_id=dict_["user_id"], quiz_id="quiz_id")
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
    "A class that represents a Quiz Math Problem"

    def __init__(
        self,
        question,
        answer,
        id,
        author,
        guild_id=None,
        voters=[],
        solvers=[],
        cache=None,
        answers=[],
        is_written=False,
        quiz_id=None,
        max_score=-1,
        quiz=None,
    ):
        "A method that allows the creation of new QuizMathProblems"
        if not isinstance(quiz.Quiz):
            raise TypeError(
                f"quiz is of type {quiz.__class.__name}, not Quiz"
            )  # Here to help me debug

        super().__init__(
            question, answer, id, author, guild_id, voters, solvers, cache, answers
        )  #
        self.is_written = False
        if quiz is not None:
            self.quiz_id = quiz.id
        else:
            self.quiz_id = quiz_id
        self.max_score = max_score
        self.min_score = 0

    @property
    def quiz(self):
        "Return my quiz"
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
        "Edit a problem!"
        super().edit(question, answer, id, guild_id, voters, solvers, author, answers)
        if not isinstance(quiz, Quiz):
            raise TypeError(
                f"quiz is of type {quiz.__class.__name}, not Quiz"
            )  # Here to help me debug
        self.quiz = Quiz
        if not isinstance(is_written, bool):
            raise TypeError("is_written is not of type bool")
        self.update_self()

    def to_dict(self):
        return {
            "type": "QuizMathProblem",
            "question": self.question,
            "answer": self.answer,
            "id": str(self.id),
            "guild_id": str(self.guild_id),
            "voters": self.voters,
            "solvers": self.solvers,
            "author": self.author,
            "quiz_id": self.quiz_id,
            "is_written": self.is_written,
            "max_score": self.max_score,
        }

    @classmethod
    def from_dict(cls, Dict, cache=None):
        "Convert a dictionary to a QuizProblem. Even though the bot uses SQL, this is used in the from_row method"
        Dict.pop("type")
        return cls(*Dict, cache=cache)

    @classmethod
    def from_row(cls, row, cache=None):
        if isinstance(row, sqlite3.Row):
            raise
        try:
            voters = pickle.loads(row["voters"])
            _dict = {
                "quiz_id": row["quiz_id"],
                "guild_id": row["guild_id"],
                "voters": row["voters"],
            }
            return cls.from_dict(_dict, cache=cache)
        except BaseException as e:
            traceback.print_exception(
                type(e), e, e.__traceback, file=sys.stderr
            )  # Log to stderr
            raise MathProblemsModuleException(
                "Oh no... conversion from row failed"
            ) from e  # Re-raise (which wil log)

    def update_self(self):
        "Update myself"
        if self.cache is not None:
            self.quiz.update_self()


class Quiz(list):
    "Essentially a list, so it implements everything that a list does, but it has an additional attribute submissions which is a list of QuizSubmissions"

    def __init__(
        self,
        id: int,
        iter: List[QuizProblem],
        submissions: List[QuizSubmission] = [],
        cache=None,
    ) -> "Quiz":
        """Create a new quiz. id is the quiz id and iter is an iterable of QuizMathProblems"""
        super().__init__(iter)
        self.sort(key=lambda problem: problem.id)

        self._cache = cache
        self._submissions = submissions
        self._id = id

    async def add_submission(self, submission):
        assert isinstance(submission, QuizSubmission)
        submission.mutable = False
        self._submissions.append(submission)
        await self.update_self()

    @property
    def submissions(self):
        return self._submissions

    @classmethod
    def from_dict(cls, _dict: dict):
        problemsAsType = []
        submissions = []
        Problems = _dict["problems"]
        for p in Problems:
            problemsAsType.append(QuizProblem.from_dict(p))
        problemsAsType.sort(key=lambda problem: problem.id)

        for s in _dict["submissions"]:
            submissions.append(QuizSubmission.from_dict(s))
        c = cls([])
        c.extend(problemsAsType)
        c._submissions = submissions
        c._id = _dict["id"]
        return c

    def to_dict(self):
        "Convert this instance into a Dictionary to be stored in SQL"
        Problems = [problem.to_dict() for problem in self]
        Submissions = [submission.to_dict for submission in self.submissions]
        return {"problems": Problems, "submissions": Submissions, "id": self._id}

    async def update_self(self):
        "Update myself in the sqldict"
        await self._cache.update_quiz(self._id, self)
