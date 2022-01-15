import time
import typing
from asyncio import run

from .quiz import Quiz
from .quiz_problem import QuizProblem
from .quiz_submissions import QuizSubmission, QuizSubmissionAnswer


# Not fully implemented
class QuizSolvingSession:
    def __init__(self, user_id: int, quiz_id: int, cache):
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.is_final = False
        self.cache = cache
        self.answers: typing.Dict[int, QuizSubmissionAnswer] = {}
        self.start_time = time.time()
        self._quiz = self._get_quiz()
        try:
            self.expire_time: int = self.start_time + self._quiz.time_limit
        except AttributeError:
            raise NotImplementedError(
                "Quiz descriptions + other metadata needs to be fully implemented!"
            )

        try:
            self.guild_id = self._quiz.guild_id
        except MathProblemsModuleException as MPME:
            raise RuntimeError(
                "This quiz does not have a guild id, or it is None."
            ) from MPME

        self._reset()

    def _reset(self):
        """Reset myself"""
        pass

    def _get_quiz(self) -> Quiz:
        """Get the quiz for this QuizSubmissionSession and return it"""
        return asyncio.run(self.cache.get_quiz(self.quiz_id))

    def add_submission_answer(self, submission_answer: QuizSubmissionAnswer):
        """Add a submission answer to this session!"""
        problem_num = submission_answer.problem_id
        self.answers[problem_num] = submission_answer
        return submission_answer

    def _get_submission_answer(self, problem_num: int):
        """Get this submission answer or raise KeyError if it isn't found"""
        return self.answers[problem_num]

    @property
    def is_overtime(self: QuizSolvingSession) -> bool:
        return time.time() > self.expire_time

