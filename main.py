chec# Written by @rf20008
# Licensed under GPLv3
# Feel free to contribute! :-)
# Python 3.10+ is required.
from sys import exit

from helpful_modules import constants_loader

if (
    not __debug__
):  # __debug__ must be true for the bot to run (because assert statements)
    exit("__debug__ must be True for the bot to run! (Don't run with -o or -OO)")
del exit
# imports - standard library
import asyncio
import copy
import os
import logging
import typing
import warnings
from time import sleep, time, asctime
import subprocess
import traceback
import threading
from sys import stderr, exc_info, stdout
from asyncio import sleep as asyncio_sleep
from copy import copy

# Imports - 3rd party

import disnake  # https://github.com/DisnakeDev/disnake
import aiosqlite  # https://github.com/omnilib/aiosqlite


# Imports - My own files
from disnake.ext import commands
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules import _error_logging, checks, cooldowns
from helpful_modules import custom_embeds, problems_module
from helpful_modules import save_files, the_documentation_file_loader, return_intents
from helpful_modules.problems_module.errors import *
from helpful_modules.threads_or_useful_funcs import *

from cogs import *
from helpful_modules.cooldowns import check_for_cooldown, OnCooldown
from helpful_modules._error_logging import log_error
from helpful_modules.custom_embeds import *
from helpful_modules.checks import is_not_blacklisted, setup
from helpful_modules.the_documentation_file_loader import *
from helpful_modules.constants_loader import *

VERSION = "0.0.5a2"
try:
    import dotenv  # https://pypi.org/project/python-dotenv/

    assert hasattr(dotenv, "load_dotenv") and hasattr(dotenv, "find_dotenv")
except (ModuleNotFoundError, AssertionError):
    raise RuntimeError("Dotenv could not be found, therefore cannot load .env")
dotenv.find_dotenv()
dotenv.load_dotenv(dotenv.find_dotenv())
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", None)
if DISCORD_TOKEN is None:
    raise RuntimeError("Cannot start bot; no discord_token environment variable")


def the_daemon_file_saver():
    "Auto-save files!"
    global bot, guildMathProblems, trusted_users, vote_threshold
    print("Initializing the filesaver")
    FileSaverObj = save_files.FileSaver(
        name="The Daemon File Saver", enabled=True, printSuccessMessagesByDefault=True
    )
    print("Loading files...")
    FileSaverDict = FileSaverObj.load_files(bot.cache, True)
    (guildMathProblems, bot.trusted_users, bot.vote_threshold) = (
        FileSaverDict["guildMathProblems"],
        FileSaverDict["trusted_users"],
        int(FileSaverDict["vote_threshold"]),
    )
    while True:
        sleep(45)
        print("Saving files")
        FileSaverObj.save_files(
            bot.cache,
            False,
            guildMathProblems,
            bot.vote_threshold,
            bot.trusted_users,
        )


warnings.simplefilter("default")  # unnecessary, probably will be removed
# constants

trusted_users = []
try:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    assert DISCORD_TOKEN is not None
except (KeyError, AssertionError):
    raise RuntimeError(
        "You haven't setup the .env file correctly! You need DISCORD_TOKEN=<your token>"
    )
bot_constants = BotConstants(dotenv.find_dotenv())
main_cache = problems_module.MathProblemCache(
    max_answer_length=2000,
    max_question_limit=250,
    max_guild_problems=125,
    warnings_or_errors="errors",
    db_name="MathProblemCache1.db",
    update_cache_by_default_when_requesting=True,
    use_cached_problems=False,
    mysql_username=bot_constants.MYSQL_USERNAME,
    mysql_password=bot_constants.MYSQL_PASSWORD,
    mysql_db_ip=bot_constants.MYSQL_DB_IP,
    mysql_db_name=bot_constants.MYSQL_DB_NAME,
    use_sqlite=bot_constants.USE_SQLITE,
)  # Generate a new cache for the bot!
vote_threshold = 0  # default
mathProblems = {}
guildMathProblems = {}
guild_maximum_problem_limit = 125
erroredInMainCode = False


def loading_documentation_thread():
    "This thread reloads the documentation."
    d = DocumentationFileLoader()
    d.load_documentation_into_readable_files()
    del d


loader = threading.Thread(target=loading_documentation_thread)
loader.start()


def get_git_revision_hash() -> str:
    "A method that gets the git revision hash. Credit to https://stackoverflow.com/a/21901260 for the code :-)"
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode("ascii")
        .strip()[:7]
    )  # [7:] is here because of the commit hash, the rest of this function is from stack overflow


# @bot.event
async def on_ready(bot):
    "Ran when the disnake library detects that the bot is ready"
    print("The bot is now ready!")


# Bot creation

asyncio.set_event_loop(asyncio.new_event_loop())  # Otherwise, weird errors will happen
bot = TheDiscordMathProblemBot(
    command_prefix=commands.when_mentioned,
    intents=return_intents.return_intents(),
    application_id=845751152901750824,
    status=disnake.Status.idle,
    cache=main_cache,
    constants=bot_constants,
    trusted_users=copy(trusted_users),
    tasks={},
    on_ready_func=on_ready
    # activity = nextcord.CustomActivity(name="Making sure that the bot works!", emoji = "🙂") # This didn't work anyway, will set the activity in on_connect
)
# TODO: move bot events + initializing to custom_bot.py
bot._sync_commands_debug = True
# setup(bot)
bot._transport_modules = {
    "problems_module": problems_module,
    "save_files": save_files,
    "the_documentation_file_loader": the_documentation_file_loader,
    "check_for_cooldown": check_for_cooldown,
    "custom_embeds": custom_embeds,
    "checks": checks,
}
bot.add_check(
    disnake.ext.commands.bot_has_permissions(
        send_messages=True,
        read_messages=True,
        embed_links=True,
    )
)
bot.blacklisted_users = []  # TODO: user_status dict
_the_daemon_file_saver = threading.Thread(
    target=the_daemon_file_saver,
    name="The File Saver",
    daemon=True,  # Make sure that the bot object passed to the_daemon_file_saver is the same one used by the rest of the program
)
_the_daemon_file_saver.start()
# bot.load_extension("jishaku")

# slash = InteractionClient(client=bot, sync_commands=True)
# bot.slash = slash
# Add the commands
bot.add_cog(DeveloperCommands(bot))
bot.add_cog(ProblemsCog(bot))
bot.add_cog(QuizCog(bot))
bot.add_cog(MiscCommandsCog(bot))
bot.add_cog(TestCog(bot))
bot.CONSTANTS = bot_constants
print("Bots successfully created.")

# Events


@bot.event
async def on_connect():
    "Run when the bot connects"
    print("The bot has connected to Discord successfully.")
    await asyncio_sleep(0.5)
    await bot.change_presence(
        activity=disnake.CustomActivity(
            name="Making sure that the bot works!", emoji="🙂"
        ),
        status=disnake.Status.idle,
    )
    bot.log.debug(
        "Deleting data from guilds the bot was kicked from while it was offline"
    )
    bot_guild_ids = [guild.id for guild in bot.guilds]
    for (
        guild_id
    ) in (
        await bot.cache.get_guilds()
    ):  # Obtain all guilds the cache stores data (will need to be upgraded.)
        if guild_id not in bot_guild_ids:  # It's not in!
            bot.log.debug("The bot is deleting data from a guild it has left.")
            await bot.cache.remove_all_by_guild_id(guild_id)  # Delete the data


@bot.event
async def on_error(event, *args, **kwargs):
    error = exc_info()
    if True:
        # print the traceback to the file
        print(
            "\n".join(traceback.format_exception(*error)),
            file=stderr,
        )

    error_traceback_as_obj = "\n".join(traceback.format_exception(*error))
    # Log the error?
    log_error(error[1])
    # We don't have an interaction/context, so I can't tell the user that an error happened
    print("Oh no! An exception occured!", flush=True, file=stdout)

    print(error_traceback_as_obj, flush=True, file=stdout)


@bot.event
async def on_slash_command_error(inter, error):
    "Function called when a slash command errors, which will inevitably happen. All of the functionality was moved to base_on_error :-)"
    # print the traceback to the file
    dict_args = await base_on_error(inter, error)
    print(dict_args)
    try:
        return await inter.send(**dict_args)
    except AttributeError:
        return await inter.send()


##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")


@bot.event
async def on_guild_join(guild):
    "Ran when the bot joins a guild!"
    if guild.id == None:  # Should never happen
        raise Exception("Uh oh!")  # This is probably causing the bot to do stuff
        await guild.leave()  # This will mess up stuff
        print("Oh no")
        raise RuntimeError(
            "Oh no..... there is a guild with id None... this will mess up the bot!"
        )  # Make sure that a guild with id _global doesn't mess up stuff


@bot.event
async def on_guild_remove(guild):
    await bot.cache.remove_all_by_guild_id(guild.id)  # Remove all guild-related stuff
    # uh oh?


if __name__ == "__main__":
    print("The bot has finished setting up and will now run.")
    # slash.run(DISCORD_TOKEN)
    for command in bot.global_slash_commands:
        # raise
        if len(command.name) > 100:
            raise Exception(f"This command: {command.name} is too long")
    bot.run(DISCORD_TOKEN)
