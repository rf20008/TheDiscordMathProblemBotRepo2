from helpful_modules.problems_module import *

from ..helper_cog import HelperCog
import typing


async def get_quiz_submission(
    self: HelperCog,
    user_id: int,
    quiz_id: int,
    attempt_num: typing.Optional[int] = None,
) -> typing.Optional[typing.Union[QuizSolvingSession, typing.List[QuizSolvingSession]]]:
    quiz: Quiz = await self.cache.get_quiz(quiz_id)

    def check(session: QuizSolvingSession) -> bool:
        works: bool = True
        if attempt_num is not None:
            works = session.attempt_num == attempt_num
        return session.user_id == user_id and works

    sessions = filter(check, quiz.existing_sessions)
    if sessions is []:
        raise problems_module.QuizSessionNotFoundException("Quiz session not found")

    return (
        sessions[0]
        if len(sessions) == 1
        else max(sessions, key=lambda session: session.attempt_num)
    )


async def get_attempt_num_for_user(self: HelperCog, user_id: int, quiz_id: int) -> int:
    """Get the latest attempt number for the user for this quiz"""
    quiz: Quiz = await self.cache.get_quiz(quiz_id)

    def check(session: QuizSolvingSession) -> bool:
        """A function to determine whether this submission should be included"""
        return session.user_id == user_id

    # basically: use filter() to make sure the sessions we check only are from the user.
    # From that, we use list comprehension to create a list of the attempt numbers of the sessions given
    # Then we use max() to find the maximum of that created list and return it
    return max([item.attempt_num for item in filter(check, quiz.existing_sessions)])

def setup(*args):
    pass