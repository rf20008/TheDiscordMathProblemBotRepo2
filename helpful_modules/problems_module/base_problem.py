import warnings
import nextcord, dislash
from sqlite3 import Row
from .errors import *
import pickle
import traceback
import sys
from helpful_modules.dict_factory import dict_factory


class BaseProblem:
    "For readability purposes :) This also isn't an ABC."

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
    ):
        if guild_id != None and not isinstance(guild_id, str):
            raise TypeError("guild_id is not an string")
        if not isinstance(id, int):
            raise TypeError("id is not an integer")
        if not isinstance(question, str):
            raise TypeError("question is not a string")
        if not isinstance(answer, str):
            raise TypeError("answer is not a string")
        if not isinstance(author, int):
            raise TypeError("author is not an integer")
        if not isinstance(voters, list):
            raise TypeError("voters is not a list")
        if not isinstance(solvers, list):
            raise TypeError("solvers is not a list")
        if not isinstance(answers, list):
            raise TypeError("answers isn't a list")

        if cache is None:
            warnings.warn("_cache is None. This may cause errors", RuntimeWarning)
        # if not isinstance(cache,MathProblemCache) and cache is not None:
        #    raise TypeError("_cache is not a MathProblemCache.")
        if len(question) > 250:
            raise TooLongQuestion(
                f"Your question is {len(question) - 250} characters too long. Questions may be up to 250 characters long."
            )
        self.question = question
        if len(answer) > 100:
            raise TooLongAnswer(
                f"Your answer is {len(question) - 100} characters too long. Answers may be up to 100 characters long."
            )
        self.answer = answer
        self.id = id
        self.guild_id = guild_id
        self.voters = voters
        self.solvers = solvers
        self.author = author
        self._cache = cache
        self.answers = answers

    async def edit(
        self,
        question=None,
        answer=None,
        id=None,
        guild_id=None,
        voters=None,
        solvers=None,
        author=None,
        answers=None,
    ) -> None:
        """Edit a math problem. The edit is in place"""
        if guild_id not in [None, None] and not isinstance(guild_id, int):
            raise TypeError("guild_id is not an integer")
        if not isinstance(id, int) and id is not None:
            raise TypeError("id is not an integer")
        if not isinstance(question, str) and question is not None:
            raise TypeError("question is not a string")
        if not isinstance(answer, str) and answer is not None:
            raise TypeError("answer is not a string")
        if not isinstance(author, int) and author is not None:
            raise TypeError("author is not an integer")
        if not isinstance(voters, list) and voters is not None:
            raise TypeError("voters is not a list")
        if not isinstance(solvers, list) and solvers is not None:
            raise TypeError("solvers is not a list")
        if not isinstance(answers, list) and answers is not None:
            raise TypeError("answers is not a list")
        if (
            id is not None
            or guild_id is not None
            or voters is not None
            or solvers is not None
            or author is not None
        ):
            warnings.warn(
                "You are changing one of the attributes that you should not be changing.",
                category=RuntimeWarning,
            )
        if question is not None:
            if (
                self._cache is not None
                and len(question) > self._cache.max_question_length
            ) or (len(question) > 250 and self._cache is None):
                if self._cache is not None:
                    raise TooLongQuestion(
                        f"Your question is {len(question) - self._cache.max_question_length} characters too long. Questions may be up to {self._cache.max_question_length} characters long."
                    )
                else:
                    raise TooLongQuestion(
                        f"Your question is {len(question) - 250} characters too long. Questions may be up to 250 characters long."
                    )
            self.question = question
        if (
            self._cache is not None and len(question) > self._cache.max_question_length
        ) or (len(answer) > 100 and self._cache is None):
            if self._cache is not None:
                raise TooLongAnswer(
                    f"Your answer is {len(question) - self._cache.max_answer_length} characters too long. Answers may be up to {self._cache.max_answer_length} characters long."
                )
            else:
                raise TooLongAnswer(
                    f"Your answer is {len(question) - 100} characters too long. Answers may be up to 100 characters long."
                )
        for answer in answers:
            if self._cache is not None:
                if len(answer) > 100:
                    raise TooLongAnswer(
                        f"Answer #{answer} is {len(answers[answer])-100} characters too long. Answers can be up to a 100 characters long"
                    )
            else:
                if len(answer) > self._cache.max_answer_length:
                    raise TooLongAnswer(
                        f"Answer #{answer} is {len(answers[answer]) - self._cache.max_answer_length} characters too long. Answers can be up to {self._cache.max_answer_length} characters long."
                    )
        if answer is not None:
            self.answer = answer
        if id is not None:
            self.id = id
        if guild_id is not None:
            self.guild_id = guild_id
        if voters is not None:
            self.voters = voters
        if solvers is not None:
            self.solvers = solvers
        if author is not None:
            self.author = author

        await self.update_self()

    async def update_self(self):
        "A helper method to update the cache with my version"
        if self._cache is not None:
            await self._cache.update_problem(self.guild_id, self, id, self)

    @classmethod
    def from_row(cls, row, cache=None):
        "Convert a dictionary-ified row into a MathProblem"
        if not isinstance(row, dict):
            raise MathProblemsModuleException(
                "The problem has not been dictionary-ified"
            )

        try:
            answers = pickle.loads(
                row["answers"]
            )  # Load answers from bytes to a list (which should contain only pickleable objects)!
            voters = pickle.loads(row["voters"])  # Do the same for voters and solvers
            solvers = pickle.loads(row["voters"])
            _Row = {
                "guild_id": row["guild_id"],  # Could be None
                "problem_id": row["guild_id"],
                "answer": Exception,  # Placeholder,
                "answers": answers,
                "voters": voters,
                "solvers": solvers,
                "author": row["author"],
            }
            return cls.from_dict(_Row, cache=cache)
        except BaseException as e:
            traceback.print_exception(
                type(e), e, e.__traceback__, file=sys.stderr
            )  # Log to stderr
            raise SQLException(
                "Uh oh..."
            ) from e  # Re-raise the exception to the user (so that they can help me debug (error_logs/** is gitignored))

    @classmethod
    def from_dict(cls, _dict, cache=None):
        "Convert a dictionary to a math problem. cache must be a valid MathProblemCache"
        assert isinstance(_dict, (dict, Row))
        if isinstance(_dict, Row):
            _dict = dict_factory(_dict)  # Dict-ification :-)
        problem = _dict
        guild_id = problem["guild_id"]
        if guild_id == None:
            guild_id = None
        elif (
            guild_id == "null"
        ):  # Remove the guild_id null (used for global problems), which is not used anymore because of conflicts with SQL

            Problem = cls(
                question=problem["question"],
                answer=problem["answer"],
                id=int(problem["id"]),
                guild_id=None,
                voters=problem["voters"],
                solvers=problem["solvers"],
                author=problem["author"],
                cache=cache,
            )  # Problem-ify the problem, but set the guild_id to _global
            # Then remove the problem from SQL, because it says the guild_id is null
            cache.remove_problem_without_returning(
                Problem.guild_id, Problem.id
            )  # There will be a recursion error if I normally delete a problem
            # Add the problem again
            cache.add_problem(Problem.guild_id, Problem.id, Problem)
            return Problem
        problem2 = cls(
            question=problem["question"],
            answer=problem["answer"],
            id=int(problem["id"]),
            guild_id=int(guild_id),
            voters=problem["voters"],
            solvers=problem["solvers"],
            author=problem["author"],
            cache=cache,
        )
        return problem2

    def to_dict(self, show_answer=True):
        "An alias for convert_to_dict"
        return self.convert_to_dict(show_answer)

    def convert_to_dict(self, show_answer=True):
        """Convert self to a dictionary"""
        _dict = {
            "type": "MathProblem",
            "question": self.question,
            "id": str(self.id),
            "guild_id": str(self.guild_id),
            "voters": self.voters,
            "solvers": self.solvers,
            "author": self.author,
        }
        if show_answer:
            _dict["answers"] = self.get_answers()
        return _dict

    def add_voter(self, voter):
        """Adds a voter. Voter must be a nextcord.User object or nextcord.Member object."""
        if not isinstance(voter, nextcord.User) and not isinstance(
            voter, nextcord.Member
        ):
            raise TypeError("User is not a User object")
        if not self.is_voter(voter):
            self.voters.append(voter.id)
        self.update_self()

    def add_solver(self, solver):
        """Adds a solver. Solver must be a nextcord.User object or nextcord.Member object."""
        if not isinstance(solver, nextcord.User) and not isinstance(
            solver, nextcord.Member
        ):
            raise TypeError("Solver is not a User object")
        if not self.is_solver(solver):
            self.solvers.append(solver.id)
        self.update_self()

    def get_answer(self):
        "Return my answer. This has been deprecated"
        return self.answer

    def get_answers(self):
        "Return my possible answers"
        return [self.answer, *self.answers]

    def get_question(self):
        "Return my question."
        return self.question

    def check_answer_and_add_checker(self, answer, potentialSolver):
        "Checks the answer. If it's correct, it adds potentialSolver to the solvers."
        if not isinstance(potentialSolver, nextcord.User) and not isinstance(
            potentialSolver, nextcord.Member
        ):
            raise TypeError("potentialSolver is not a User object")
        if self.check_answer(answer):
            self.add_solver(potentialSolver)

    def check_answer(self, answer):
        "Checks the answer. Returns True if it's correct and False otherwise."
        return answer in self.get_answers()

    def my_id(self):
        "Returns id & guild_id in a list. id is first and guild_id is second."
        return [self.id, self.guild_id]

    def get_voters(self):
        "Returns self.voters"
        return self.voters

    def get_num_voters(self):
        "Returns the number of solvers."
        return len(self.get_voters())

    def is_voter(self, User):
        "Returns True if user is a voter. False otherwise. User must be a nextcord.User or nextcord.Member object."
        if not isinstance(User, nextcord.User) and not isinstance(
            User, nextcord.Member
        ):
            raise TypeError("User is not actually a User")
        return User.id in self.get_voters()

    def get_solvers(self):
        "Returns self.solvers"
        return self.solvers

    def is_solver(self, User):
        "Returns True if user is a solver. False otherwise. User must be a nextcord.User or nextcord.Member object."
        if not isinstance(User, nextcord.User) and not isinstance(
            User, nextcord.Member
        ):
            raise TypeError("User is not actually a User")
        return User.id in self.get_solvers()

    def get_author(self):
        "Returns self.author"
        return self.author

    def is_author(self, User):
        "Returns if the user is the author"
        if not isinstance(User, nextcord.User) and not isinstance(
            User, nextcord.Member
        ):
            raise TypeError("User is not actually a User")
        return User.id == self.get_author()

    def __eq__(self, other):
        "Return self==other"
        if not isinstance(self, type(other)):
            return False
        try:
            return self.question == other.question and other.answer == self.answer
        except AttributeError:
            return False

    def __repr__(self):
        "A method that when called, returns a string, that when executed, returns an object that is equal to this one. Also implements repr(self)"
        return f"""problems_module.MathProblem(question={self.question},
        answer = {self.answer}, id = {self.id}, guild_id={self.guild_id},
        voters={self.voters},solvers={self.solvers},author={self.author},cache={None})"""  # If I stored the problems, then there would be an infinite loop

    def __str__(self, include_answer=False):
        "Implement str(self)"
        _str = f"""Question: {self.question}, 
        id: {self.id}, 
        guild_id: {self.guild_id}, 
        solvers: {[f'<@{id}>' for id in self.solvers]},
        author: <@{self.author}>"""
        if include_answer:
            _str += f"\nAnswer: {self.answer}"
        return str(_str)
