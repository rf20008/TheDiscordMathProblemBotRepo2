import typing
from typing import List

from helpful_modules.problems_module import BaseProblem

from .quiz_description import QuizDescription
from .quiz_problem import QuizProblem
from .quiz_submissions import QuizSubmission
from .QuizSolvingSession import QuizSolvingSession
from .related_enums import QuizIntensity, QuizTimeLimit


class Quiz(list):
    """Represents a quiz.
    but it has an additional attribute submissions which is a list of QuizSubmissions"""

    def __init__(
        self,
        id: int,
        authors: List[int],
        quiz_problems: List[QuizProblem],
        submissions: List[QuizSubmission] = None,
        existing_sessions=None,  # This is a list of QuizSessions
        cache=None,
        description=None,
    ) -> None:
        """Create a new quiz. id is the quiz id and iter is an iterable of QuizMathProblems"""
        assert isinstance(existing_sessions, list) or existing_sessions is None
        assert isinstance(authors, list)
        self._description = description
        self._time_limit = description.time_limit
        self.license = description.license
        self.intensity = description.intensity
        self.category = category
        self.category = category
        self.authors = authors
        self.existing_sessions = (
            existing_sessions if existing_sessions is not None else []
        )
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

    async def add_problem(
        self, problem: QuizProblem, insert_location: typing.Optional[int] = None
    ):
        """Add a problem to this quiz."""
        if len(self.problems) + 1 > self._cache.max_problems_per_quiz:
            raise TooManyProblems(
                f"""There is already the maximum number of problems on this quiz. Therefore, adding a new quiz is prohibited to save memory. 
            Because this is a FOSS bot, there is no premium version and thus no way to increase the number of problems you can have on a quiz!"""
            )
        if insert_location is None:
            insert_location = len(self.problems) - 1
        assert isisntance(problem, QuizProblem)  # Type-checking
        self.problems.insert(problem, insert_location)
        await self.update_self()

    @property
    def quiz_problems(self):
        return self.problems

    @property
    def submissions(self):
        return self._submissions

    @property
    def id(self):
        return self._id

    @property
    def guild_id(self):
        if self.empty:
            raise MathProblemsModuleException("This quiz is empty!")
        return self.problems[0].guild_id

    @property
    def empty(self) -> bool:
        return len(self.problems) == 0 and len(self.submissions) == 0

    @classmethod
    def from_dict(cls, _dict: dict):
        problems_as_type = []
        submissions = []
        Problems = _dict["problems"]
        for p in Problems:
            problems_as_type.append(QuizProblem.from_dict(p))
        problems_as_type.sort(key=lambda problem: problem.id)

        for s in _dict["submissions"]:
            submissions.append(QuizSubmission.from_dict(s))  # type: ignore
        c = cls(quiz_problems=problems_as_type, id=_dict["id"])  # type: ignore

        c._submissions = submissions
        c._id = _dict["id"]
        return c

    def to_dict(self) -> dict:
        """Convert this instance into a Dictionary!"""
        problems = [problem.to_dict() for problem in self.problems]
        submissions = [submission.to_dict for submission in self.submissions]
        return {
            "problems": problems,
            "submissions": submissions,
            "id": self._id,
            "existing_sessions": [
                session.to_dict() for session in self.existing_sessions
            ],
            'description': self._description.to_dict()
        }

    async def update_self(self):
        """Update myself!"""
        await self._cache.update_quiz(self._id, self)

    @classmethod
    def from_data(
        cls,
        problems: typing.List[QuizProblem],
        authors: typing.List[int],
        existing_sessions: typing.List[QuizSolvingSession],
        submissions: typing.List[QuizSubmission],
        cache: "MathProblemCache",
    ):
        return cls(
            quiz_problems=problems,
            authors=authors,
            existing_sessions=existing_sessions,
            submissions=submissions,
            cache=cache,
        )  # type: ignore
