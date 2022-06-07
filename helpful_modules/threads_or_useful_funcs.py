import logging
import pathlib
import random
import subprocess
import traceback
import types
import typing
from copy import deepcopy
from logging import handlers
from sys import exc_info, stderr
from time import asctime, sleep
from typing import Callable, Optional

import disnake
from disnake.ext import commands

from ._error_logging import log_error
from .cooldowns import OnCooldown
from .custom_embeds import *
from .the_documentation_file_loader import DocumentationFileLoader

# Licensed under GPLv3

REQUIRED_LOGS = ("" "bot", "disnake")

log = logging.getLogger(__name__)


def generate_new_id():
    """Generate a random number from 0 to 2**53-1"""
    return random.randint(0, 2**53 - 1)


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


async def base_on_error(
    inter: typing.Union[
        disnake.ApplicationCommandInteraction,
        disnake.MessageInteraction,
        disnake.ModalInteraction,
        disnake.Interaction,
    ],
    error: BaseException,
):
    """The base on_error event. Call this and use the dictionary as keyword arguments to print to the user"""
    error_traceback = "\n".join(traceback.format_exception(error))
    if isinstance(error, BaseException) and not isinstance(error, Exception):
        # Errors that do not inherit from Exception are not meant to be caught
        await inter.bot.close()
        raise
    if isinstance(error, (OnCooldown, disnake.ext.commands.CommandOnCooldown)):
        # This is a cooldown exception
        cooldown = error.cooldown
        content = (
            f"This command is on cooldown; please retry in {cooldown.per} seconds."
        )
        return {"content": content}
    if isinstance(error, (disnake.Forbidden,)):
        extra_content = """There was a 403 error. This means either
        1) You didn't give me enough permissions to function correctly, or
        2) There's a bug! If so, please report it!
        
        The error traceback is below."""
        return {"content": extra_content + error_traceback}

    if isinstance(error, commands.NotOwner):
        return {"embed": ErrorEmbed("You are not the owner of this bot.")}
    if isinstance(error, disnake.ext.commands.errors.CheckFailure):
        return {"embed": ErrorEmbed(str(error))}
    # Embed = ErrorEmbed(custom_title="⚠ Oh no! Error: " + str(type(error)), description=("Command raised an exception:" + str(error)))
    logging.error("Uh oh! An error occurred!", exc_info=exc_info())
    print(
        "\n".join(traceback.format_exception(error)),  # python 3.10 only!
        file=stderr,
    )
    log_error(error)  # Log the error
    error_msg = """An error occurred!
    
    Steps you should do:
    1) Please report this bug to me! (Either create a github issue, or report it in the support server)
    2) If you are a programmer, please suggest a fix by creating a Pull Request.
    3) Please don't use this command until it gets fixed in a later update!
    
    The error traceback is shown below; this may be removed/DMed to the user in the future.
    
    """ + disnake.utils.escape_markdown(
        error_traceback
    )  # TODO: update when my support server becomes public & think about providing the traceback to the user
    try:
        embed = disnake.Embed(
            colour=disnake.Colour.red(),
            description=error_msg,
            title="Oh, no! An error occurred!",
        )
    except (TypeError, NameError) as e:

        # send as plain text
        plain_text = (
            """Oh no! An Exception occurred! And it couldn't be sent as an embed!```"""
        )
        plain_text += error_traceback
        plain_text += f"```Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"

        plain_text += f"Error that occurred while attempting to send it as an embed: {''.join(traceback.format_exception(e))}"
        the_new_exception = deepcopy(e)
        the_new_exception.__cause__ = error
        if len(plain_text) > 2000:
            # uh oh
            raise RuntimeError(
                "An error occurred; could not send it as an embed nor as plain text!"
            ) from the_new_exception

        return {"content": plain_text}
    footer = f"Time: {str(asctime())} Commit hash: {get_git_revision_hash()} The stack trace is shown for debugging purposes. The stack trace is also logged (and pushed), but should not contain identifying information (only code which is on github)"
    embed.set_footer(text=footer)
    return {"embed": embed}


def get_log(name: Optional[str]) -> logging.Logger:
    _log = logging.getLogger(name)
    TRFH = handlers.TimedRotatingFileHandler(
        filename="logs/bot.log", when="midnight", encoding="utf-8", backupCount=300
    )
    _log.addHandler(TRFH)
    return _log


def _generate_special_id(guild_id, quiz_id, user_id, attempt_num):
    return str(
        {
            "quiz_id": quiz_id,
            "guild_id": guild_id,
            "user_id": user_id,
            "attempt_num": attempt_num,
        }
    )


def _generate_appeal_id(user_id, appeal_num):
    return str({"appeal_num": appeal_num, "user_id": user_id})


def async_wrap(func):
    """Turn a sync function into an asynchronous function
    Source: https://dev.to/0xbf/turn-sync-function-to-async-python-tips-58nn

    """

    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run


def modified_async_wrap(func):
    assert isinstance(func, types.FunctionType)
    if asyncio.iscoroutinefunction(func):
        return func
    return async_wrap(func)


def make_sure_log_dir_exists(log_maker: Callable[[str], logging.Logger]):
    try:
        logs_folder = pathlib.Path("logs")
        logs_folder.mkdir(exist_ok=True)
        for log_needed in REQUIRED_LOGS:
            log = log_maker(log_needed + ".log")
    except:
        print("I don't have permission to create a logs folder so logs may be missing!")

import random


def miller_rabin_primality_test(n: int, certainty: int = 1000):
    """An implementation of the Miller-Rabin primality test. Return whether the number is probably prime!

    Lots of credit to https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test"""
    if n<=1:
        return False
    if n==2:
        return True
    if n==3:
        return True
    
    d=n
    numFactorsof2=0
    while d % 2== 0:
        d= d//2
        numFactorsof2+=1
    for i in range(certainty):
        a = random.randint(2,d-2)
        x = pow(a,d,n)
        if x==1 or x==n-1:
            continue
        witnessFound=False
        for j in range(numFactorsof2):
            x=pow(x,2,n)
            if x==n-1:
                witnessFound=True
                break
        if witnessFound:
            return False
    return True

def miller_robin_primality_test(n: int, certainty:int=1000)-> bool:
    return miller_rabin_primality_test(n,certainty)



def attempt_to_import_orjson() -> tuple[typing.Optional[types.ModuleType], bool]:
    """attempt_to_import_orjson()
    
    Attempt to import orjson and catch the ImportError

    Parameters
    -----------------
    There are no parameters

    Returns
    ------------
    Returns a tuple. The first element of the tuple is orjson or None.
    The second element is a bool representing whether orjson could be succesfully imported
    """
    try:
        import orjson
        return (orjson, True)
    except ImportError:
        return (None, False)
