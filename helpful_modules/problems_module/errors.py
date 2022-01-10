"""Licensed under GPLv3"""
import mysql.connector


class MathProblemsModuleException(Exception):
    """The base exception for problems_module."""

    pass


class TooLongArgument(MathProblemsModuleException):
    """Raised when an argument passed into MathProblem() is too long."""

    pass


class TooLongAnswer(TooLongArgument):
    """Raised when an answer is too long."""

    pass


class TooLongQuestion(TooLongArgument):
    """Raised when a question is too long."""

    pass


class GuildAlreadyExistsException(MathProblemsModuleException):
    """Raised when MathProblemCache.add_empty_guild tries to run on a guild that already has problems."""

    pass


class TooManyProblems(MathProblemsModuleException):
    """Raised when trying to add problems when there is already the maximum number of problems."""

    pass


class ProblemNotFound(KeyError, MathProblemsModuleException):
    """Raised when a problem isn't found"""

    pass


class ProblemNotFoundException(ProblemNotFound):
    """Raised when a problem is not found."""

    pass


class ProblemNotWrittenException(MathProblemsModuleException):
    """Raised when trying to grade a written problem but the problem is not a written problem"""

    pass


class QuizAlreadySubmitted(MathProblemsModuleException):
    """Raised when trying to submit a quiz that has already been submitted"""

    pass


class SQLException(MathProblemsModuleException):
    """Raised when an error happens relating to SQL!"""

    pass


class MySQLException(SQLException, mysql.connector.Error):
    """A generic MYSQL exception"""

    def __init__(self, message, base_error):
        SQLException.__init__(self, message)
        self.base_error = base_error


class QuizNotFound(MathProblemsModuleException):
    """Raised when a quiz isn't found"""

    pass


class IsRowException(MathProblemsModuleException):
    """Raised when expecting a dictionary but got a row instead."""

    pass


class TooMuchUserDataException(MathProblemsModuleException):
    """Raised when there is too much user data!"""

    pass


class UserDataNotExistsException(MathProblemsModuleException):
    """Raised by MathProblemCache.set_user_data when user data does not exist!"""
    pass


class TooManyQuizzesException(MathProblemsModuleException):
    """Raised a guild has too many quizzes"""
    def __init__(self, num_quizzes: int):
        message: str = f"The guild already has {num_quizzes} quizzes, which is too much!"
        super().__init__(message)
