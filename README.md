[![Powered by Nextcord](https://custom-icon-badges.herokuapp.com/badge/-Powered%20by%20Nextcord-0d1620?logo=nextcord)](https://github.com/nextcord/nextcord "Powered by Nextcord Python API Wrapper")

# License


This discord bot and all of its code is licensed under the combined terms of the GNU license and the MIT license. (due to nextcord being licensed under the MIT license)


# If you run into issues
If you run into any issues create an issue or DM me (ay136416#2707)). 


# Contribute :-)

If you open a PR/Issue, I'll look at it and maybe merge it! 

# Invite my bot!

Recommended invite: https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147568640&scope=bot%20applications.commands

# Documentation

https://github.com/rf20008/TheDiscordMathProblemBotRepo/tree/master/docs

# Attribution
https://stackoverflow.com/a/21901260 for the get_git_revision_hash :-)
nextcord + discord devs for their libraries
SQLDict: https://github.com/skylergrammer/sqldict


# Help for self-hosting my bot (or )
My code is open source, so you can! There are bugs, so you should probably help me instead. I won't stop you from self-hosting though.

## steps
(This assumes you already have knowledge of the command line and how to make a new discord application)
1. Create a new Discord application with a bot user. Save the token (you will need it later)
2. Update Python to 3.9/3.10
3. Create a venv (execute ``python3.10 -m venv /path/to/new/virtual/environment``)
4. move to your new venv (use the cd command)
5. Install poetry, a dependency installer (``pip3 install git+https://github.com/python-poetry/poetry.git``). You can also optionally install it outside.
6. Clone my repo (``git clone https://github.com/rf20008/TheDiscordMathProblemBotRepo``)
7. move to the new directory containing the repository you cloned (which should be this one. The folder name is the same name as the repository name)
8. Create a .env file inside the repository folder. Inside it, you need to put 
``DISCORD_TOKEN = `<your discord token>` `` (Replace `<your discord token>`) with the discord bot token you got from the bot user you made.
9. Run the main.py file (```python3.10 main.py```)
