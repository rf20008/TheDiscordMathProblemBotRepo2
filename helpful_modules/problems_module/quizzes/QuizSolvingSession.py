from .quiz import Quiz
from .quiz_problem import QuizProblem
from .quiz_submissions import QuizSubmission, QuizSubmissionAnswer
import typing


class QuizSolvingSession:
    def __init__(self, user_id, quiz_id):
        self.user_id = user_id
        self.quiz_id = quiz_id
        self.is_final = False
        self.answers: typing.List[QuizSubmissionAnswer] = []

        self._reset()

