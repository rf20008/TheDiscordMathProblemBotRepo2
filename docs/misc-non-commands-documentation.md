# Legend
*: Only useable by users with the Administrator (considering changing it to Manage Server) permission and global trusted users can use.
⚠: Only useable by global trusted users (such as /raise_error)
No Mark: Useable by everyone

# Misc. Functions

## FileSaver

### __init__
save_files.FileSaver.__init__(self,name=None,enabled=False,printSuccessMessagesByDefault=False,math_problems_file_name="math_problems.json",guild_math_problems_file_name="guild_math_problems.json",trusted_users_file_name="trusted_users.txt",vote_threshold_file_name="vote_threshold.txt"):

This method creates a new FileSaver object with the name specified.
By default, it is not enabled and does not print messages by default.
The other 4 parameters are the file names. These should not be specified (they are default), unless the file names are not the ones specified.

### __str__

This method returns its name.

### enable:
This method 