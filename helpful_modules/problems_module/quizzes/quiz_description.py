import typing as t
from dataclasses import dataclass

from .related_enums import QuizIntensity, QuizTimeLimit


@dataclass
class QuizDescription:
    """A dataclass that holds quiz description"""

    category: str
    intensity: t.Union[QuizIntensity, int]
    description: str
    license: str
    cache: "MathProblemCache"
    time_limit: t.Union[int, QuizTimeLimit]
    guild_id: int
    author: int
    solvers_can_view_quiz: bool

    def __init__(
        self,
        *,
        cache: "MathProblemCache",
        quiz_id: int,
        author: int,
        guild_id: int,
        category: str = "Unspecified",
        intensity: t.Union[QuizIntensity, float] = QuizIntensity.IMPOSSIBLE,
        description="No description given",
        license="Unspecified (the default is GNU GDL)",
        time_limit=QuizTimeLimit.UNLIMITED,
        solvers_can_view_quiz: bool = False,
    ):
        self.solvers_can_view_quiz = solvers_can_view_quiz
        self.guild_id = guild_id
        self.author = author
        self.quiz_id = quiz_id
        self.cache = cache
        self.category = category
        self.intensity = intensity
        self.description = description
        self.license = license
        self.time_limit = time_limit

    @classmethod
    def from_dict(cls, data: dict, cache: "MathProblemCache") -> "QuizDescription":
        return cls(
            author=data["author"],
            quiz_id=data["quiz_id"],
            cache=cache,
            category=data["category"],
            intensity=data["intensity"],
            description=data["description"],
            license=data["license"],
            time_limit=data["timelimit"],
            guild_id=data["guild_id"],
            solvers_can_view_quiz=bool(data["solvers_can_view_quiz"]),
        )

    def to_dict(self) -> dict:
        return {
            "author": self.author,
            "quiz_id": self.quiz_id,
            "category": self.category,
            "intensity": self.intensity,
            "description": self.description,
            "license": self.license,
            "time_limit": self.time_limit,
            "guild_id": self.guild_id,
            "solvers_can_view_quiz": self.solvers_can_view_quiz,
        }

    def time_limit_to_int(self) -> int:
        if isinstance(self.time_limit, int):
            return self.time_limit
        return self.time_limit.value

    def __str__(self) -> str:
        return f"""**Quiz ID:** {self.quiz_id},
**Time Limit:** {self.time_limit_to_int()} seconds
**Description:** {self.description}
**License:** {self.license}
**Guild ID:** {self.guild_id},
**Author:** <@{self.author}>
**Category:** {self.category.name}
**Solvers Can View Quiz:** {self.solvers_can_view_quiz}"""
