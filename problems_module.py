import nextcord, json, warnings
from copy import deepcopy

# This is a module containing MathProblem and MathProblemCache objects. (And exceptions as well!) This may be useful outside of this discord bot so feel free to use it :) Just follow the MIT+GNU license
class MathProblemsModuleException(Exception):
    "The base exception for problems_module."
class TooLongArgument(MathProblemsModuleException):
    '''Raised when an argument passed into MathProblem() is too long.'''
    pass
class TooLongAnswer(TooLongArgument):
    """Raised when an answer is too long."""
    pass
class TooLongQuestion(TooLongArgument):
    """Raised when a question is too long."""

class GuildAlreadyExistsException(MathProblemsModuleException):
    "Raised when MathProblemCache.add_empty_guild tries to run on a guild that already has problems."
class ProblemNotFoundException(MathProblemsModuleException):
  "Raised when a problem is not found."

class MathProblem:
    "For readability purposes :)"
    def __init__(self,question,answer,id,author,guild_id="null",voters=[],solvers=[]):
        if guild_id != "null" and not isinstance(guild_id, int):
            raise TypeError("guild_id is not an integer")
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
        if len(question) > 250:
            raise TooLongQuestion(f"Your question is {len(question) - 250} characters too long. Questions may be up to 250 characters long.")
        self.question = question
        if len(answer) > 100:
            raise TooLongAnswer(f"Your answer is {len(question) - 100} characters too long. Answers may be up to 100 characters long.")
        self.answer = answer
        self.id = id
        self.guild_id = guild_id
        self.voters = voters
        self.solvers=solvers
        self.author=author
    def edit(self,question=None,answer=None,id=None,guild_id=None,voters=None,solvers=None,author=None):
        """Edit a math problem."""
        if guild_id not in [None,"null"] and not isinstance(guild_id, int):
            raise TypeError("guild_id is not an integer")
        if not isinstance(id, int) and id != None:
            raise TypeError("id is not an integer")
        if not isinstance(question, str) and question != None:
            raise TypeError("question is not a string")
        if not isinstance(answer, str) and answer != None:
            raise TypeError("answer is not a string")
        if not isinstance(author, int) and author != None:
            raise TypeError("author is not an integer")
        if not isinstance(voters, list) and voters != None:
            raise TypeError("voters is not a list")
        if not isinstance(solvers, list) and solvers != None:
            raise TypeError("solvers is not a list")
        if id != None or guild_id != None or voters != None or solvers != None or author != None:
            warnings.warn("You are changing one of the attributes that you should not be changing.", category=RuntimeWarning)
        if question != None:
            if len(question) > 250:
                raise TooLongQuestion(f"Your question is {len(question) - 250} characters too long. Questions may be up to 250 characters long.")
            self.question = question
        if answer != None:
            if len(answer) > 100:
                raise TooLongAnswer(f"Your answer is {len(question) - 100} characters too long. Answers may be up to 100 characters long.")
            self.answer = answer
        if id != None:
            self.id = id
        if guild_id != None:
            self.guild_id = guild_id
        if voters != None:
            self.voters = voters
        if solvers != None:
            self.solvers = solvers
        if author != None:
            self.author = author
    def convert_to_dict(self):
        """Convert self to a dictionary"""

        return {
            "question": self.question,
            "answer": self.answer,
            "id": str(self.id),
            "guild_id": str(self.guild_id),
            "voters": self.voters,
            "solvers": self.solvers,
            "author": self.author
        }
    def add_voter(self,voter):
        """Adds a voter. Voter must be a nextcord.User object or nextcord.Member object."""
        if not isinstance(voter,nextcord.User) and not isinstance(voter,nextcord.Member):
            raise TypeError("User is not a User object")
        if not self.is_voter(voter):
            self.voters.append(voter.id)
    def add_solver(self,solver):
        """Adds a solver. Solver must be a nextcord.User object or nextcord.Member object."""
        if not isinstance(solver,nextcord.User) and not isinstance(solver,nextcord.Member):
            raise TypeError("Solver is not a User object")
        if not self.is_solver(solver):
            self.solvers.append(solver.id)
    def get_answer(self):
        "Return my answer."
        return self.answer
    def get_question(self):
        "Return my question."
        return self.question
    def check_answer_and_add_checker(self,answer,potentialSolver):
        "Checks the answer. If it's correct, it adds potentialSolver to the solvers."
        if not isinstance(potentialSolver,nextcord.User) and not isinstance(potentialSolver,nextcord.Member):
            raise TypeError("potentialSolver is not a User object")
        if self.check_answer(answer):
            self.add_solver(potentialSolver)
    def check_answer(self,answer):
        "Checks the answer. Returns True if it's correct and False otherwise."
        return answer == self.get_answer()
    def my_id(self):
        "Returns id & guild_id in a list. id is first and guild_id is second."
        return [self.id, self.guild_id]
    def get_voters(self):
        "Returns self.voters"
        return self.voters
    def get_num_voters(self):
        "Returns the number of solvers."
        return len(self.get_voters())
    def is_voter(self,User):
        "Returns True if user is a voter. False otherwise. User must be a nextcord.User or nextcord.Member object."
        if not isinstance(User,nextcord.User) and not isinstance(User,nextcord.Member):
            raise TypeError("User is not actually a User")
        return User.id in self.get_voters()
    def get_solvers(self):
        "Returns self.solvers"
        return self.solvers
    def is_solver(self,User):
        "Returns True if user is a solver. False otherwise. User must be a nextcord.User or nextcord.Member object."
        if not isinstance(User,nextcord.User) and not isinstance(User,nextcord.Member):
            raise TypeError("User is not actually a User")
        return User.id in self.get_solvers()
    def __str__(self):
        "Return str(self) by converting it to a dictionary and converting the dictionary to a string"
        return str(self.convert_to_dict)
    def get_author(self):
        "Returns self.author"
        return self.author
    def is_author(self,User):
        "Returns if the user is the author"
        if not isinstance(User,nextcord.User) and not isinstance(User,nextcord.Member):
            raise TypeError("User is not actually a User")
        return User.id == self.get_author()
    def __eq__(self,other):
        try:
            return self.question == other.question and other.answer == self.answer
        except:
            return False

class MathProblemCache:
    def __init__(self):
        self._dict = {}
        self.update_cache()


    def convert_dict_to_math_problem(self,problem):
        "Convert a dictionary into a math problem. It must be in the expected format."
        try:
            assert isinstance(problem,dict)
        except AssertionError:
            print(problem)
            raise TypeError("problem is not actually a Dictionary")
        guild_id = problem["guild_id"]
        if guild_id == "null":
            guild_id = "null"
        else:
            guild_id = int(guild_id)
        problem2 = MathProblem(
            question=problem["question"],
            answer=problem["answer"],
            id = int(problem["id"]),
            guild_id = guild_id,
            voters = problem["voters"],
            solvers=problem["solvers"],
            author=problem["author"]
        )
        return problem2
    def update_cache(self):
        "This method replaces the new cache with the cache from the file."
        with open("math_problems.json","r") as file:
            dict = json.loads("".join([str(thing) for thing in file]))
        for item in dict.keys():
            self._dict[item] = {}
            for item2 in dict[item].keys():
                self._dict[item][item2] = self.convert_dict_to_math_problem(dict[item][item2])
    def update_file_cache(self):
        "This method updates the file cache."
        e = {}
        for guild_id in self._dict.keys():
            e[guild_id] = {}
            for problem_id in self._dict[guild_id].keys():
                e[guild_id][problem_id] = self._dict[guild_id][problem_id].convert_to_dict()
        with open("math_problems.json", "w") as file:
            file.write(json.dumps(e))
    def get_problem(self,guild_id,problem_id):
        "Gets the problem with this guild id and problem id"
        if not isinstance(guild_id, str):
            warnings.warn("guild_id is not a string", category=RuntimeWarning)
        if not isinstance(problem_id,str):
            warnings.warn("problem_id is not a string",category=RuntimeWarning)
        try:
            guild_id_dict = self._dict[guild_id]
            
        except:
            raise MathProblemsModuleException(f"Guild_id {guild_id} was not found in the cache.")
        try:
            return guild_id_dict[problem_id]
        except:
            raise ProblemNotFound("*** Problem not found. Aborting search... ***")
    def fetch_problem(self,guild_id,problem_id):
        "Reloads the cache with the file and then loads the problem."
        self.update_cache()
        return self.get_problem(guild_id, problem_id)
    def get_guild_problems(self,Guild):
        """Gets the guild problems! Guild must be a Guild object. If you are trying to get global problems, use get_global_problems."""
        if not isinstance(Guild, nextcord.Guild):
            raise TypeError("Guild is not actually a Guild")
        if not Guild.id in self._dict.keys():
            raise MathProblemsModuleException("Guild id not found.")
        return self._dict[Guild.id]
    def get_global_problems(self):
        "Returns global problems"
        try:
            return self._dict['null'].values()
        except:
            self._dict['null'] = {}
            return {}
    def add_empty_guild(self,Guild):
        "Adds an dictionary that is empty for the guild. Guild must be a nextcord.Guild object"
        if not isinstance(Guild, nextcord.Guild):
            raise TypeError("Guild is not actually a Guild")
        try:
            if self._dict[Guild.id] != {}:
                raise GuildAlreadyExistsException
        except:
            pass
            
        self._dict[Guild.id] = {}
    def add_problem(self,guild_id,problem_id,Problem):
        "Adds a problem and returns the added MathProblem"
        if not isinstance(Problem,(MathProblem, dict)):
            raise TypeError("Problem is not a valid MathProblem object.")
        if isinstance(Problem,dict):
            try:
                Problem = self.convert_dict_to_math_problem(Problem)
            except Exception:
                raise Exception("Not a valid problem!")
        try:
            if self._dict[guild_id][problem_id] != None:
                raise Exception("Problem already exists")
        except:
            try:
                self._dict[guild_id][problem_id] = Problem
            except KeyError as e:
                self._dict[guild_id][problem_id]["null"] = Problem

#        if guild_id != 'null':
#            try:
#                if self._dict[guild_id] != {}:
#                    raise GuildAlreadyExistsException
#                else:
#                    self._dict[guild_id] = {}
#            except:
#                self._dict[guild_id] = {}
        
        return Problem
    def remove_problem(self,guild_id,problem_id):
        "Removes a problem. Returns the deleted problem"
        Problem = self.get_problem(guild_id,problem_id)
        del self._dict[guild_id][problem_id]
        return Problem
    def remove_duplicate_problems(self):
        "Deletes duplicate problems"
        problemsDeleted = 0
        c = deepcopy(self._dict)
        d = deepcopy(c)
        for g1 in self._dict.keys():
            for p1 in self._dict[g1].keys():
                for g2 in c.keys():
                    for p3 in c[g2].keys():
                        if self._dict[g1][p1] == c[g2][p3] and not (g1 == g2 and p1 != p3):
                            try:
                                del d[g1][p1]
                            except KeyError:
                                continue
                            problemsDeleted += 1
        self._dict = d
        return problemsDeleted
    def get_guilds(self):
      return self._dict.keys()

main_cache = MathProblemCache()
def get_main_cache():
    "Returns the main cache."
    return main_cache
