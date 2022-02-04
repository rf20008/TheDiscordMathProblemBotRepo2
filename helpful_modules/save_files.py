import json

from . import problems_module

numFileSavers = 0


class FileSaver:
    """A class that saves files"""

    def __init__(
        self,
        name=None,
        enabled=False,
        printSuccessMessagesByDefault=False,
    ):

        """Creates a new FileSaver object."""
        global numFileSavers
        numFileSavers += 1
        if name is None:
            name = "FileSaver" + str(numFileSavers)
        self.id = numFileSavers
        self.printSuccessMessagesByDefault = printSuccessMessagesByDefault
        self.enabled = True
        self.name = name

    def __str__(self):
        return self.name

    def enable(self):
        """Enables self."""
        self.enabled = True

    def disable(self):
        """Disables self"""
        self.enabled = False

    def load_files(self, main_cache, printSuccessMessages=None):
        """Loads files from file names specified in self.__init__."""
        if not isinstance(main_cache, problems_module.MathProblemCache):
            raise TypeError("main_cache is not a MathProblemCache.")
        if not self.enabled:
            raise RuntimeError("I'm not enabled! I can't load files!")
        trusted_users = []
        if (
            printSuccessMessages
            or printSuccessMessages is None
            and self.printSuccessMessagesByDefault
        ):
            print(
                f"{str(self)}: Attempting to load vote_threshold from vote_threshold.txt, trusted_users_list from trusted_users.txt, and math_problems  from math_problems.json..."
            )
        vote_threshold = False
        with open("vote_threshold.txt", "r") as file3:
            for line in file3:
                if str(
                    line
                ).isnumeric():  # Make sure that an empty string does not become the new vote threshold
                    vote_threshold = int(line)
        if not vote_threshold:
            raise RuntimeError("vote_threshold not found!!!")

        if (
            printSuccessMessages
            or printSuccessMessages is None
            and self.printSuccessMessagesByDefault
        ):
            print(f"{self.name}: Successfully loaded files.")

        return {
            "vote_threshold": vote_threshold,
        }

    def save_files(
        self,
        main_cache=None,
        printSuccessMessages=None,
        vote_threshold: int=3,
    ):
        """Saves files to file names specified in __init__."""

        if not isinstance(main_cache, problems_module.MathProblemCache):
            raise TypeError("main_cache is not a MathProblemCache.")
        if not self.enabled:
            raise RuntimeError("I'm not enabled! I can't load files!")
        if (
            printSuccessMessages
            or printSuccessMessages is None
            and self.printSuccessMessagesByDefault
        ):
            print(
                f"{str(self)}: Attempting to save math problems vote_threshold to vote_threshold.txt, trusted_users_list to  trusted_users.txt..."
            )
        # main_cache.update_file_cache() #Removed method
        if not isinstance(vote_threshold, int):
            raise RuntimeError("Vote Threshold is not an integer!")
        with open("vote_threshold.txt", "w") as file3:
            file3.write(str(vote_threshold))
        if (
            printSuccessMessages
            or printSuccessMessages is None
            and self.printSuccessMessagesByDefault
        ):
            print(f"{self.name}: Successfully saved files.")

    def change_name(self, new_name):
        self.name = new_name

    def my_id(self):
        return self.id

    def goodbye(self):
        print(str(self) + ": Goodbye.... :(")
        del self
