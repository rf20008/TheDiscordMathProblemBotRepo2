from dataclasses import dataclass
from .related_enums import QuizIntensity, QuizTimeLimit
import typing as t


@dataclass
class QuizDescription:
    category: str
    intensity: t.Union[QuizIntensity, int]
    description: str
    license: str
    cache: "MathProblemCache"
    time_limit: t.Union[int, QuizTimeLimit]

    def __init__(self,
                 *,
                 cache: "MathProblemCache",
                 quiz_id: int,
                 author: int,
                 category: str = "Unspecified",
                 intensity: t.Union[QuizIntensity, float] = QuizIntensity.IMPOSSIBLE,
                 description="No description given",
                 license="Unspecified (the default is GNU GDL)",
                 time_limit=QuizTimeLimit.UNLIMITED
                 ):
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
            author=data['author'],
            quiz_id=data['quiz_id'],
            cache=cache,
            category=data['category'],
            intensity=data['intensity'],
            description=data['description'],
            license=data['license'],
            time_limit=data['timelimit']
        )
