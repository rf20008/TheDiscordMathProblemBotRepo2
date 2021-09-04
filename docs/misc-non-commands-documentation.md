# Legend - global
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.
⚠: Only useable by global trusted users (such as /raise_error)
**: Not a command (Documentation is here for purposes of me, and those who wish to fork my project/contribute with pull requests :))
No Mark: Useable by everyone

# Misc. Non-Command-Functions 

## save_files.FileSaver

### __init__**
save_files.FileSaver.__init__(self,name=None,enabled=False,printSuccessMessagesByDefault=False,math_problems_file_name="math_problems.json",guild_math_problems_file_name="guild_math_problems.json",trusted_users_file_name="trusted_users.txt",vote_threshold_file_name="vote_threshold.txt"):

This method creates a new FileSaver object with the name specified.
By default, it is not enabled and does not print messages by default.
The other 4 parameters are the file names. These should not be specified (they are default), unless the file names are not the ones specified.

### __str__**

This method returns its name. Takes no parameters.

### enable**
This method enables the FileSaver object.

### disable**
Disables the FileSaver. Attempting to call save_files or load_files while the FileSaver is not enabled will raise a RuntimeError.

### load_files**

Actually loads the files. Returns the loaded files in a dictionary.
The keys are the same as the variable names (except they are strings.)

Raises a RuntimeError if attempting to call this method on a non-enabled object.
Takes one default argument (printSuccessMessages), which is set to None by default, if so it defaults to the printSuccessMessagesByDefault attribute set in __init__.

### save_files**

This method saves the files. As this is in a different function, the global keyword may not work, so the things to save must be specified. However, the argument names are different (except for vote_threshold):

guildMathProblems's argument is guild_math_problems_dict.
vote_threshold's argument name is vote_threshold.
mathProblem's argument name is math_problems_dict.
trusted_users's argument name is math_problems_dict.

Raises a RuntimeError if this object is not enabled when this method is called.
Also takes an additional argument (printSuccessMessages, before the dictionary names) which defaults to None and takes the printSuccessMessagesByDefault argument specified in __init__.

### change_name**

Changes self.name to the new name specified (1 argument, name = new_name, not keyword-only)

### my_id**

Returns self.id (the filesaver number). Takes no arguments.

### goodbye*

Deletes the FileSaver object and prints a "Goodbye" message



