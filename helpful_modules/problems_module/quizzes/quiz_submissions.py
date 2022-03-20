class QuizSubmissionAnswer:
    """A class that represents an answer for a singular problem"""

    def __init__(
        self,
        answer: str = "",
        problem_id: int = None,
        quiz_id: int = 10,
        reasoning: str = None,
    ):
        self.answer = answer
        self.problem_id = problem_id
        self.grade = grade
        self.quiz_id = quiz_id
        self.reasoning = reasoning

    def set_grade(self, grade):
        self.grade = grade

    def __str__(self):
        return f"<QuizSubmission quiz_id = {self.quiz_id} answer = {self.answer} grade = {self.grade}>"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            answer=data["answer"],
            problem_id=data["problem_id"],
            grade=data["grade"],
            quiz_id=data["quiz_id"],
            reasoning=data["reasoning"],
        )

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "problem_id": self.problem_id,
            "grade": self.grade,
            "quiz_id": self.quiz_id,
            "reasoning": self.reasoning,
        }


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
