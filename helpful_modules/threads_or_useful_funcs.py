from . import save_files
from time import sleep
import subprocess, random
from .the_documentation_file_loader import DocumentationFileLoader
import nextcord
import traceback
from .custom_embeds import *
from dislash import *
from time import asctime
from ._error_logging import log_error
from .cooldowns import OnCooldown
from sys import stderr

# Licensed under GPLv3


def generate_new_id():
    "Generate a random number from 0 to 10^14"
    return random.randint(0, 10 ** 14)


def get_git_revision_hash() -> str:
    "A method that gets the git revision hash. Credit to https://stackoverflow.com/a/21901260 for the code :-)"
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"])
        .decode("ascii")
        .strip()[:7]
    )  # [7:] is here because of the commit hash, the rest of this function is from stack overflow


def loading_documentation_thread():
    "This thread reloads the documentation."
    d = DocumentationFileLoader()
    d.load_documentation_into_readable_files()
    del d


async def base_on_error(inter, error):
    "The base on_error event. Call this and use the dictionary as keyword arguments to print to the user"
    print(
        "\n".join(
            traceback.format_exception(
                etype=type(error), value=error, tb=error.__traceback__
            )
        ),
        file=stderr,
    )
    log_error(error)  # Log the error
    error_traceback = "\n".join(
        traceback.format_exception(
            etype=type(error), value=error, tb=error.__traceback__
        )
    )
    if isinstance(error, BaseException) and not isinstance(error, Exception):
        # Errors that do not inherit from Exception are not meant to be caught
        raise
    if isinstance(error, (OnCooldown, nextcord.ext.commands.CommandOnCooldown)):
        # This is a cooldown exception
        return {"content": str(error)}
    if isinstance(error, (nextcord.Forbidden,)):
        extra_content = """There was a 403 error. This means either
        1) You didn't give me enough permissions to function correctly, or
        2) There's a bug! If so, please report it!
        
        The error traceback is below."""
        return {"content": extra_content + error_traceback}

    if isinstance(error, NotOwner):
        return {"embed": ErrorEmbed("You are not the owner of this bot.")}
    # Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))

    try:
        embed = disnake.Embed(
            colour=nextcord.Colour.red(),
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
        return {"content": plain_text}
    footer = f"Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"
    embed.set_footer(text=footer)
    return {"embed": embed}
