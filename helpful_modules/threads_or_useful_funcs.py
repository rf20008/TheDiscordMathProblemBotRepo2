import disnake
import logging
import random
import subprocess
import traceback
from disnake.ext import commands
from sys import stderr, exc_info
from time import asctime
from time import sleep

from ._error_logging import log_error
from .cooldowns import OnCooldown
from .custom_embeds import *
from .the_documentation_file_loader import DocumentationFileLoader

# Licensed under GPLv3

log = logging.getLogger(__name__)


def generate_new_id():
    """Generate a random number from 0 to 2**53-1"""
    return random.randint(0, 2 ** 53 - 1)


def get_git_revision_hash() -> str:
    """A method that gets the git revision hash. Credit to https://stackoverflow.com/a/21901260 for the code :-)"""
    return (
        subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("ascii")
            .strip()[:7]
    )  # [7:] is here because of the commit hash, the rest of this function is from stack overflow


def loading_documentation_thread():
    """This thread reloads the documentation."""
    d = DocumentationFileLoader()
    d.load_documentation_into_readable_files()
    del d


async def base_on_error(inter, error):
    """The base on_error event. Call this and use the dictionary as keyword arguments to print to the user"""
    error_traceback = "\n".join(traceback.format_exception(error))
    if isinstance(error, BaseException) and not isinstance(error, Exception):
        # Errors that do not inherit from Exception are not meant to be caught
        raise
    if isinstance(error, (OnCooldown, disnake.ext.commands.CommandOnCooldown)):
        # This is a cooldown exception
        return {"content": str(error)}
    if isinstance(error, (disnake.Forbidden,)):
        extra_content = """There was a 403 error. This means either
        1) You didn't give me enough permissions to function correctly, or
        2) There's a bug! If so, please report it!
        
        The error traceback is below."""
        return {"content": extra_content + error_traceback}

    if isinstance(error, commands.NotOwner):
        return {"embed": ErrorEmbed("You are not the owner of this bot.")}
    if isinstance(error, disnake.ext.commands.errors.CheckFailure):
        return {
            "embed": ErrorEmbed(
                str(error)
                + " You probably aren't allowed to run this command. If this is a bug, please report it :-)"
            )
        }
    # Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))
    logging.error("Uh oh - an error occured ", exc_info=exc_info())
    print(
        "\n".join(traceback.format_exception(error)),  # python 3.10 only!
        file=stderr,
    )
    log_error(error)  # Log the error
    try:
        embed = disnake.Embed(
            colour=disnake.Colour.red(),
            description=disnake.utils.escape_markdown(error_traceback),
            title="Oh, no! An error occurred!",
        )
    except TypeError as e:

        # send as plain text
        plain_text = (
            "Oh no! An Exception occurred! And it couldn't be sent as an embed!```"
        )
        plain_text += error_traceback
        plain_text += f"```Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"

        plain_text += f"Error that occurred while attempting to send it as an embed: {''.join(traceback.format_exception(e))}"
        return {"content": plain_text}
    footer = f"Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"
    embed.set_footer(text=footer)
    return {"embed": embed}
