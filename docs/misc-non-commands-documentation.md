<! For you Github PR People, this file is dynamically generated from documentation.json. You should consider editing that instead :)># Legend - global
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.

⚠: Only useable by global trusted users (such as /raise_error)

**: Not a bot/slash command (Documentation is here for purposes of me, and those who wish to fork my project/contribute with pull requests :))

***: This is a module/class. Cannot be called.

No Mark: This is a command without user restrictions
# Why does thiis document exist? Users won't need it.

This is here for people who want to see how my bot works, or people who want to contribute :)


# Misc. Non-Command-Functions (not in main.py)



## save_files.FileSaver***
Exists to clean up the code.
### __init__**
save_files.FileSaver.__init__(self,name=None,enabled=False,printSuccessMessagesByDefault=False,math_problems_file_name="math_problems.json",guild_math_problems_file_name="guild_math_problems.json",trusted_users_file_name="trusted_users.txt",vote_threshold_file_name="vote_threshold.txt"):

This method creates a new FileSaver object with the name specified.
By default, it is not enabled and does not print messages by default.
The other 4 parameters are the file names. These should not be specified (they are default), unless the file names are not the ones specified.

### __str__**


This method returns its name. Takes no parameters.

### enable
This method enables the FileSaver object.

### disable**
Disables the FileSaver. Attempting to call save_files or load_files while the FileSaver is not enabled will raise a RuntimeError.
### load_files**
Actually loads the files. Returns the loaded files in a dictionary.
The keys are the same as the variable names (except they are strings.)

Raises a RuntimeError if attempting to call this method on a non-enabled object.
Takes one default argument (printSuccessMessages), which is set to None by default, if so it defaults to the printSuccessMessagesByDefault attribute set in __init__.

### change_name**
Changes self.name to the new name specified (1 argument, name = new_name, not keyword-only)

### save_files**
This method saves the files. As this is in a different function, the global keyword may not work, so the things to save must be specified. However, the argument names are different (except for vote_threshold)
guildMathProblems's argument is guild_math_problems_dict.
vote_threshold's argument name is vote_threshold.
mathProblem's argument name is math_problems_dict.
trusted_users's argument name is math_problems_dict.

Raises a RuntimeError if this object is not enabled when this method is called.
Also takes an additional argument (printSuccessMessages, before the dictionary names) which defaults to None and takes the printSuccessMessagesByDefault argument specified in __init__.
### my_id**
Returns self.id (the filesaver number). Takes no arguments.

### goodbye**
Returns self.id (the filesaver number). Takes no arguments.

## return_indents***


### return_indents.return_indents**
This function returns the bot's intents.
## user_error


### user_error.UserError***

Inherits from the Exception class. Used in /raise_error (which is a trusted users only command, used for debugging on_slash_command_error.)

#### user_error.UserError._raise()**
Takes no arguments. Raises self.
## the_documentation_file_loader**
Custom module I made for loading documentation.json into real documentation.

### DocumentationException***
The base exception for the_documentation_file_loader module

#### the_documentation_file_loader.DocumentationNotFound._raise**
Takes no arguments. Raises self.
### DocumentationNotFound***
This exception, or subclasses of it, is raised when Documentation is not found. Is a subclass of DocumentationException.
### DocumentationFileNotFound***
A custom exception that is raised when a documentation file is not found.
### DocumentationFileLoader**


#### __init__**
Takes no arguments and creates a new DocumentationFileLoader object.
#### _load_documentation_file**
Loads the documentation.json file and returns the dictionary-ify'd version of it

#### load_documentation_into_readable_files
Loads the documentation from the file into readable files.
#### get_documentation
Fetches the documentation and returns it.
## custom_embeds***

This module exists so I can include embeds easier :)

### custom_embeds.SimpleEmbed***
A subclass of Embed, with 3 arguments: title, description, and color.
(Basically just discord.Embed, but its arguments are in a different order.)
### custom_embeds.ErrorEmbed***
Inherits from custom_embeds.SimpleEmbed. Also takes 3 arguments, except the color is by default set to red, is the second argument, and the title argument is custom_title and is the 3rd argument.
### custom_embeds.SuccessEmbed***
Basically the same as ErrorEmbed. Except the title argument is called successTitle and the default color is green.

# # Misc. Non-Command-Functions in main.py



## the_daemon_file_saver**
A function that runs in a different thread (lines 43, 45 starts the thread) that saves the files every 45 seconds. Runs using a save_files.FileSaver() object.

When it is started, it creates a FileSaver object which is enabled and prints messages by default. It then loads the files and saves them to the dictionary. Every 45 seconds, it saves the dictionaries to the files using FileSaver's save_files() method.
## generate_new_id**
Generates a random number from 1 to 10,000,000,000 and returns it. Used for generating problem id's. Takes no arguments.