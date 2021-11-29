# Written by @rf20008
# Licensed under CC-BY-SA 4.0/GPL v3.0
# Feel free to contribute! :-)
# Python 3.8+ is required.
# Python 3.10 might not work with the bot, because it can't connect to Discord

if (
    not __debug__
):  # __debug__ must be true for the bot to run (because assert statements)
    raise RuntimeError(
        "__debug__ must be True for the bot to run! (Don't run with -o or -OO)"
    )

# imports - standard library
import asyncio
import copy
import random
import os
import warnings
from time import sleep, time, asctime
import subprocess
import traceback
import threading
from sys import stderr, exc_info, stdout

# Imports - 3rd party
import discord
import dislash  # https://github.com/EQUENOS/dislash.py
from dislash import InteractionClient, Option, OptionType, NotOwner, OptionChoice
import nextcord  # https://github.com/nextcord/nextcord
import nextcord.ext.commands as nextcord_commands
import aiosqlite
from asyncio import sleep as asyncio_sleep
from copy import copy

from nextcord.ext.commands.cooldowns import BucketType

# Imports - My own files
from helpful_modules import _error_logging, checks, cooldowns
from helpful_modules import custom_embeds, problems_module
from helpful_modules import save_files, the_documentation_file_loader, return_intents
from helpful_modules.threads_or_useful_funcs import *

# might be replaced with from helpful_modules import * and using __all__

import cogs
from cogs import *
from helpful_modules.cooldowns import check_for_cooldown, OnCooldown
from helpful_modules._error_logging import log_error
from helpful_modules.custom_embeds import *
from helpful_modules.checks import is_not_blacklisted, setup
from helpful_modules.the_documentation_file_loader import *

try:
    import dotenv  # https://pypi.org/project/python-dotenv/

    assert hasattr(dotenv, "load_dotenv")
except (ModuleNotFoundError, AssertionError):
    raise RuntimeError("Dotenv could not be found, therefore cannot load .env")
dotenv.load_dotenv()
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", None)
if DISCORD_TOKEN is None:
    raise ValueError("Cannot start bot; no discord_token environment variable")
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
        print('Saving files')
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
main_cache = problems_module.MathProblemCache(
    max_answer_length=2000,
    max_question_limit=250,
    max_guild_problems=125,
    warnings_or_errors="errors",
    db_name="MathProblemCache1.db",
    update_cache_by_default_when_requesting=True,
    use_cached_problems=False,
)  # Generate a new cache for the bot!
vote_threshold = 0 #default
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


# Bot creation

asyncio.set_event_loop(asyncio.new_event_loop())  # Otherwise, weird errors will happen
bot = nextcord_commands.Bot(
    command_prefix=" ",
    intents=return_intents.return_intents(),
    application_id=845751152901750824,
    status=nextcord.Status.idle,
    # activity = nextcord.CustomActivity(name="Making sure that the bot works!", emoji = "🙂") # This didn't work anyway, will set the activity in on_connect
)

setup(bot)
bot.cache = main_cache
bot.trusted_users = copy(trusted_users)
bot._transport_modules = {
    "problems_module": problems_module,
    "save_files": save_files,
    "the_documentation_file_loader": the_documentation_file_loader,
    "check_for_cooldown": check_for_cooldown,
    "custom_embeds": custom_embeds,
    "checks": checks,
}
bot.add_check(is_not_blacklisted)
bot.vote_threshold = copy(vote_threshold)
bot.blacklisted_users = []
_the_daemon_file_saver = threading.Thread(
    target=the_daemon_file_saver, name="The File Saver", daemon=True # Make sure that the bot object passed to the_daemon_file_saver is the same one used by the rest of the program
)
_the_daemon_file_saver.start()
# bot.load_extension("jishaku")


slash = InteractionClient(client=bot, sync_commands=True)
bot.slash = slash
bot.add_cog(DeveloperCommands(bot))
bot.add_cog(ProblemsCog(bot))
bot.add_cog(QuizCog(bot))
bot.add_cog(MiscCommandsCog(bot))

print("Bots successfully created.")

# Events


@bot.event
async def on_connect():
    "Run when the bot connects"
    print("The bot has connected to Discord successfully.")
    await asyncio_sleep(0.5)
    await bot.change_presence(
        activity=nextcord.CustomActivity(
            name="Making sure that the bot works!", emoji="🙂"
        ),
        status=nextcord.Status.idle,
    )


@bot.event
async def on_ready():
    "Ran when the nextcord library detects that the bot is ready"
    print("The bot is now ready!")


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
async def on_slash_command_error(inter, error, print_stack_traceback=[True, stderr]):
    "Function called when a slash command errors, which will inevitably happen"
    if print_stack_traceback[0]:
        # print the traceback to the file
        print(
            "\n".join(
                traceback.format_exception(
                    etype=type(error), value=error, tb=error.__traceback__
                )
            ),
            file=print_stack_traceback[1],
        )
    if isinstance(error, BaseException) and not isinstance(error, Exception):
        # Errors that do not inherit from Exception are not meant to be caught
        raise
    if isinstance(error, OnCooldown):
        await inter.reply(str(error))
        return
    error_traceback_as_obj = traceback.format_exception(
        etype=type(error), value=error, tb=error.__traceback__
    )
    log_error(error)  # Log the error
    if isinstance(error, NotOwner):
        await inter.reply(embed=ErrorEmbed("You are not the owner of this bot."))
        return
    # Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))

    error_traceback = "\n".join(error_traceback_as_obj)
    try:
        embed = discord.Embed(
            colour=discord.Colour.red(),
            description=nextcord.utils.escape_markdown(error_traceback),
            title="Oh, no! An error occurred!",
        )
    except TypeError:
        # send as plain text
        plain_text = (
            "__**Oh no! An Exception occured! And it couldn't be sent as an embed!\n```"
        )
        plain_text += nextcord.utils.escape_markdown(error_traceback)
        plain_text += f"```Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"
        await inter.reply(plain_text)
        return
    assert isinstance(embed, discord.Embed)
    footer = f"Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"
    embed.set_footer(text=footer)
    try:
        await inter.reply(embed=embed)
    except discord.errors.InvalidArgument:  # not an embed
        plain_text = (
            "__**Oh no! An Exception occured! And it couldn't be sent as an embed!\n```"
        )
        plain_text += nextcord.utils.escape_markdown(error_traceback)
        plain_text += f"```Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"
        await inter.reply(plain_text)


##@bot.command(help = """Adds a trusted user!
##math_problems.add_trusted_user <user_id>
##adds the user's id to the trusted users list
##(can only be used by trusted users)""",
##brief = "Adds a trusted user")


@slash.slash_command(
    name="delete_problem",
    description="Deletes a problem",
    options=[
        Option(
            name="problem_id",
            description="Problem ID!",
            type=OptionType.INTEGER,
            required=True,
        ),
        Option(
            name="is_guild_problem",
            description="whether deleting a guild problem",
            type=OptionType.USER,
            required=False,
        ),
    ],
)
async def delete_problem(inter, problem_id, is_guild_problem=False):
    "Delete a math problem"
    await check_for_cooldown(inter, "unvote", 0.5)
    guild_id = inter.guild.id
    if is_guild_problem:
        if guild_id is None:
            await inter.reply(
                embed=ErrorEmbed(
                    "Run this command in the discord server which has the problem you are trying to delete, or switch is_guild_problem to False."
                )
            )
            return
        if problem_id not in main_cache.get_guild_problems(inter.guild).keys():
            await inter.reply(
                embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True
            )
            return
        if not (
            inter.author.id in bot.trusted_users
            or not (main_cache.get_problem(str(guild_id), str(problem_id)).is_author())
            or (inter.author.guild_permissions.administrator)
        ):
            await inter.reply(
                embed=ErrorEmbed("Insufficient permissions"), ephemeral=True
            )
            return
        await main_cache.remove_problem(guild_id, problem_id)
        await inter.reply(
            embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"),
            ephemeral=True,
        )
    if guild_id is None:
        await inter.reply(
            embed=ErrorEmbed(
                "Run this command in the discord server which has the problem, or switch is_guild_problem to False."
            )
        )
        return
    if problem_id not in main_cache.get_guild_problems(inter.guild).keys():
        await inter.reply(
            embed=ErrorEmbed("That problem doesn't exist."), ephemeral=True
        )
        return
    if not (
        inter.author.id in bot.trusted_users
        or not (main_cache.get_problem(guild_id, problem_id).is_author())
        or inter.author.guild_permissions.administrator
    ):  # Not
        await inter.reply(embed=ErrorEmbed("Insufficient permissions!"), ephemeral=True)
        return
    main_cache.remove_problem("null", problem_id)
    await inter.reply(
        embed=SuccessEmbed(f"Successfully deleted problem #{problem_id}!"),
        ephemeral=True,
    )


@slash.slash_command(
    name="add_trusted_user",
    description="Adds a trusted user",
    options=[
        Option(
            name="user",
            description="The user you want to give super special bot access to",
            type=OptionType.USER,
            required=True,
        )
    ],
)
async def add_trusted_user(inter, user):
    """/add_trusted_user [user: User]
    This slash commands adds a trusted user!
    You must be a trusted user to add a trusted user, and the user you are trying to make a trusted user must not be a trusted user.
    You must also share a server with the new trusted user."""
    await check_for_cooldown(inter, "add_trusted_user", 600)
    if inter.author.id not in bot.trusted_users:
        await inter.reply(
            embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True
        )
        return
    if user.id in bot.trusted_users:
        await inter.reply(
            embed=ErrorEmbed(f"{user.name} is already a trusted user!"), ephemeral=True
        )
        return
    bot.trusted_users.append(user.id)
    await inter.reply(
        embed=ErrorEmbed(f"Successfully made {user.nick} a trusted user!"),
        ephemeral=True,
    )


@slash.slash_command(
    name="remove_trusted_user",
    description="removes a trusted user",
    options=[
        Option(
            name="user",
            description="The user you want to take super special bot access from",
            type=OptionType.USER,
            required=True,
        )
    ],
)
async def remove_trusted_user(inter, user):
    """/remove_trusted_user [user: User]
    Remove a trusted user. You must be a trusted user to do this."""
    await check_for_cooldown(inter, "remove_trusted_user", 600)
    if inter.author.id not in bot.trusted_users:
        await inter.reply(
            embed=ErrorEmbed("You aren't a trusted user!"), ephemeral=True
        )
        return
    if user.id not in bot.trusted_users:
        await inter.reply(
            embed=ErrorEmbed(f"{user.name} isn't a trusted user!", ephemeral=True)
        )
        return
    bot.trusted_users.pop(user.id)
    await inter.reply(
        embed=ErrorEmbed(f"Successfully made {user.nick} no longer a trusted user!"),
        ephemeral=True,
    )


@slash.slash_command(
    name="submit_a_request",
    description="Submit a request. I will know!",
    options=[
        Option(
            name="offending_problem_guild_id",
            description="The guild id of the problem you are trying to remove. The guild id of a global problem is null",
            type=OptionType.INTEGER,
            required=False,
        ),
        Option(
            name="offending_problem_id",
            description="The problem id of the problem. Very important (so I know which problem to check)",
            type=OptionType.INTEGER,
            required=False,
        ),
        Option(
            name="extra_info",
            description="A up to 5000 character description (about 2 pages) Use this wisely!",
            type=OptionType.STRING,
            required=False,
        ),
        Option(
            name="copyrighted_thing",
            description="The copyrighted thing that this problem is violating",
            type=OptionType.STRING,
            required=False,
        ),
        Option(
            name="type",
            description="Request type",
            required=False,
            type=OptionType.BOOLEAN,
        ),
    ],
)
async def submit_a_request(
    inter,
    offending_problem_guild_id=None,
    offending_problem_id=None,
    extra_info=None,
    copyrighted_thing=None,
    type="",
):
    "Submit a request! I will know! It uses a channel in my discord server and posts an embed"
    cooldowns.check_for_cooldown("submit_a_request", 5)  # 5 seconds cooldown
    if (
        extra_info is None
        and type == ""
        and copyrighted_thing is not Exception
        and offending_problem_guild_id is None
        and offending_problem_id is None
    ):
        await inter.reply(embed=ErrorEmbed("You must specify some field."))
    if extra_info is None:
        await inter.reply(embed=ErrorEmbed("Please provide extra information!"))
    assert len(extra_info) <= 5000
    try:
      channel = await bot.fetch_channel(
          901464948604039209
      )  # CHANGE THIS IF YOU HAVE A DIFFERENT REQUESTS CHANNEL! (the part after id)
    except (nextcord.ext.commands.ChannelNotReadable, nextcord.Forbidden):
        raise RuntimeError("The bot cannot send messages to the channel!")
    try:
        Problem = await bot.cache.get_problem(
            offending_problem_guild_id, offending_problem_id
        )
        problem_found = True
    except (TypeError, KeyError, problems_module.ProblemNotFound):
        # Problem not found
        problem_found = False
    content = bot.owner_id
    embed = nextcord.Embed(
        title=f"A new {type} request has been recieved from {inter.author.name}#{inter.author.discriminator}!",
        description="",
    )

    if problem_found:
        embed.description = f"Problem_info:{ str(Problem)}"
    embed.description += f"""Copyrighted thing: (if legal): {copyrighted_thing}
    Extra info: {extra_info}"""
    if problem_found:
        embed.set_footer(text=str(Problem) + asctime())
    else:
        embed.set_footer(text=str(asctime()))

    content = "A request has been submitted."
    for (
        owner_id
    ) in (
        bot.owner_ids
    ):  # Mentioning owners: may be removed (you can also remove it as well)
        content += f"<@{owner_id}>"
    content += f"<@{bot.owner_id}>"
    await channel.send(embed=embed, content=content)
    await inter.reply("Your request has been submitted!")


@bot.event
async def on_guild_join(guild):

    if guild.id == "_global":  # Should never happen

        await guild.leave()
        print("Oh no")
        raise RuntimeError(
            "Oh no..... there is a guild with id _global... this will mess up the bot!"
        )  # Make sure that a guild with id _global doesn't mess up stuff


if __name__ == "__main__":
    print("The bot has finished setting up and will now run.")
    # slash.run(DISCORD_TOKEN)

    bot.run(DISCORD_TOKEN)
