<!This file is dynamically generated from documentation.json. If you want to contribute/this is your fork, edit that instead :)>
# Legend - global
        
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.

⚠: Only useable by global trusted users (such as /raise_error)

**: Not a bot/slash command (Documentation is here for purposes of me, and those who wish to fork my project/contribute with pull requests :))

***: This is a module/class. Cannot be called.

No Mark: This is a command without user restrictions
# Empty messages?
This bot  utilizes embeds for its messages. If you deny that permission, most messages will be empty (and there may be 403 errors.)

# Math Problem Related

## show_problem_info
Shows the problem info of a problem, excluding its answer (unless the user is a global trusted user/ has the Administrator permission in the guild and the problem is a guild problem  and the show_all_data option is set to True).

Raw: Whether to send it as a dictionary.


## list_all_problem_ids
List all the problem ids of the problems stored withthe bot. Takes a few arguments (show_only_guild_problems: whether to show only guild problems. Otherwise shows only global math problems)
## generate_new_problems ⚠
Generates new 4 function math problems (up to 200 at a time)
## delallbotproblems ⚠

Deletes all bot-generated problems (generated via /generate_new_problems)

## new_problem

Submit a new problem! You may specify a question (up to 250 characters) and an answer (up to 100 characters). Note that the limitations may be shorter due to restrictions on slash commands.


## check_answer
Check your answer to a specified problem! You need to specify its id, the answer you are giving and whether it is a guild problem (defaults to global).
## list_all_problems
Lists as many math problems as it can but does not list all problems due to Discord character limitations (1930 characters max.) If it does not list all of them, the problems it lists are in the order it iterates over the dictionary (which should be the order in which they were added, oldest to youngest, but if you are forking this bot it may be random.)
Takes 3 options
show_solved_problems: whether to show problems that you have already solved
show_guild_problems: whether to show guild problems
show_only_guild_problems: whether to only show guild problems and not global ones. Will show nothing if this is set to true but show_guild_problems is not.
## vote
Vote for the deletion of a bad problem!
The options needed should be self-explanatory.
## unvote
Takes away a deletion vote of a problem.
## delete_problem
Deletes a problem. You must be a global trusted user or have the Administrator permission (and the target must be a guild problem.)
# Miscellaneous Commands


Miscellaneous commands I added for testing/fun/things that might be necessary. Most of them are restricted to trusted users.

## force_load_files ⚠
Forcefully loads the dictionary of math problems, the dictionary of guild math problems, the list of trusted users, and the vote threshold from the files. Useful for debugging. Restricted to global trusted users. Runs by creating a FileSaver object and calling its load_files function, saving the result to the variables.
## force_save_files ⚠
Forcefully saves the dictionary of math problems, the dictionary of guild math problems, the list of trusted users, and the vote threshold to the files.
## list_trusted_users
Lists the trusted users by mentioning them in an ephemeral message.

Why is this message ephemeral? This is so that they don't actually get pinged. This seems counter-intuitive, but it's the best solution :)
## set_vote_threshold ⚠
Sets the global vote threshold for problems need to get deleted via vote.
## add_trusted_user ⚠
Adds a trusted user. Takes one parameter (the user). Mention the user (don't worry, the user should not get pinged)
## remove_trusted_user ⚠
Removes trusted user status from a user.
## ping
Returns the bot's latency
## what_is_vote_threshold
Print's the global vote threshold for the deletion of math problems :)
## github_repo
Prints the list to the github repository :)
## raise_error
Raises an error. Useful for debugging.
## documentation
Help with the documentation of this bot
## debug
Provides helpful debug information :-)