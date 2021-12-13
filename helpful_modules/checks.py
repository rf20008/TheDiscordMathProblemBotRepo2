<<<<<<< HEAD
import dislash, nextcord
=======
from disnake.ext import commands
>>>>>>> disnake

bot = None


def setup(_bot):
    global bot
    bot = _bot
    return "Success!"


<<<<<<< HEAD
class CustomCheckFailure(dislash.InteractionCheckFailure):
=======
class CustomCheckFailure(commands.CheckFailure):
>>>>>>> disnake
    "Raised when a custom check fails. Some checks raise exceptions inherited from this."
    pass


class NotTrustedUser(CustomCheckFailure):
    "Raised when trying to run a command that requires trusted user permissions but you aren't a trusted user"
    pass


class BlacklistedException(CustomCheckFailure):
    "Raised when trying to run a command, but something you are trying to use is blacklisted"
    pass


def custom_check(
    function=lambda inter: True, args: list = [], exceptionToRaiseIfFailed=None
):
    "A check template :-)"

    def predicate(inter):
        f = function(*args)
        if not f:
            raise exceptionToRaiseIfFailed
        return True

<<<<<<< HEAD
    return dislash.check(predicate)
=======
    return commands.check(predicate)
>>>>>>> disnake


def trusted_users_only():
    def predicate(inter):
        if bot == None or bot.trusted_users == []:
            return False
        if inter.author.id in bot.trusted_users:
            return True
        raise NotTrustedUser(
            f"You aren't a trusted user, {inter.author.mention}. Therefore, you do not have permission to run this command!"
        )

<<<<<<< HEAD
    return dislash.check(predicate)
=======
    return commands.check(predicate)
>>>>>>> disnake


def administrator_or_trusted_users_only():
    "Checks if the user has administrator permission or is a bot trusted user."

    def predicate(inter):

        if (
            inter.author.guild_permissions.adminstrator
            or inter.author.id in bot.trusted_users
        ):
            return True
        raise CustomCheckFailure(
<<<<<<< HEAD
            "Insufficient permissions (administrator permission or bot trusted user required. If this happens again and you have the administrator permissio, report this)"
        )

    return dislash.check(predicate)
=======
            "Insufficient permissions (administrator permission or bot trusted user required. If this happens again and you have the administrator permission, report this)"
        )

    return commands.check(predicate)
>>>>>>> disnake


def always_failing_check():
    "This check will never pass"

    def predicate(inter):
        raise CustomCheckFailure("This check (test) will never pass")

<<<<<<< HEAD
    return dislash.check(predicate)
=======
    return commands.check(predicate)
>>>>>>> disnake


def is_not_blacklisted():
    "Check to make sure the user is not blacklisted"

    def predicate(inter):
        if inter.author.id in bot.blacklisted_users:
            raise BlacklistedException(
                "You are blacklisted from the bot. This should not happen (as there is no way to blacklist people at runtime, and the blacklisted users list clears upon restarts. Please report this with a Github Issue! )"
            )
        return True

<<<<<<< HEAD
    return dislash.check(predicate)
=======
    return commands.check(predicate)
>>>>>>> disnake
