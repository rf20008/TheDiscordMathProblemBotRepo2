# Legend - global
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.
⚠: Only useable by global trusted users (such as /raise_error)
**: Not a bot/slash command (Documentation is here for purposes of me, and those who wish to fork my project/contribute with pull requests :))
***: This is a module/class. Cannot be called.
No Mark: This is a command without user restrictions

# Empty messages?

This bot heavily utilizes embeds for its messages. If you deny that permission, the bot will not be able to send its messages.

# Math Problem Related

## show_problem_info
Shows the problem info of a problem, excluding its answer (unless the user is a global trusted user/ has the Administrator permission in the guild and the problem is a guild problem  and the show_all_data option is set to True).

Raw: Whether to send it as a dictionary.

## list_all_problem_ids

List all the problem ids of the problems stored withthe bot. Takes a few arguments (show_only_guild_problems: whether to show only guild problems. Otherwise shows only global math problems)

## generate_new_problems ⚠

Generates new 4 function math problems (up to 200 at a time)

## delallbotproblems ⚠




# Miscellaneous Commands

Miscellaneous commands I added for testing/fun/things that might be necessary.

## test_embeds

Prints some test embeds. Will be removed soon.

## force_load_files ⚠

Forcefully loads the dictionary of math problems, the dictionary of guild math problems, the list of trusted users, and the vote threshold from the files. Useful for debugging. Restricted to global trusted users. Runs by creating a FileSaver object and calling it's load_files function, saving the result to the variables.

## force_save_files ⚠

Forcefully saves the dictionary of math problems, the dictionary of guild math problems, the list of trusted users, and the vote threshold to the files.

