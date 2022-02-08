from disnake.ext import commands
import disnake
from .custom_bot import TheDiscordMathProblemBot
from .problems_module.user_data import UserData

bot = None


def setup(_bot):
    global bot
    bot = _bot
    return "Success!"


class CustomCheckFailure(commands.CheckFailure):
    """Raised when a custom check fails. Some checks raise exceptions inherited from this."""

    pass


class NotTrustedUser(CustomCheckFailure):
    """Raised when trying to run a command that requires trusted user permissions but the user isn't trusted"""

    pass


class BlacklistedException(CustomCheckFailure):
    """Raised when trying to run a command, but something you are trying to use is blacklisted"""

    pass


def custom_check(
        function=lambda inter: True, args: list = [], exceptionToRaiseIfFailed=None
):
    """A check template :-)"""

    def predicate(inter):
        f = function(inter)
        if not f:
            raise exceptionToRaiseIfFailed
        return True

    return commands.check(predicate)


def trusted_users_only():
    async def predicate(inter):
        if inter.bot is None:
            raise CustomCheckFailure("Bot is None")
        if not isinstance(inter.bot, TheDiscordMathProblemBot):
            raise TypeError("Uh oh; inter.bot isn't TheDiscordMathProblemBot")
        if await inter.bot.is_trusted(inter.author):
            return True

        raise NotTrustedUser(
            f"You aren't a trusted user, {inter.author.mention}. Therefore, you do not have permission to run this command!"
        )

    return commands.check(predicate)


def administrator_or_trusted_users_only():
    """Checks if the user has administrator permission or is a bot trusted user."""

    async def predicate(inter):
        if inter.author.guild_permissions.adminstrator:
            return True
        else:
            if not isinstance(inter.bot, TheDiscordMathProblemBot):
                raise TypeError("Uh oh")
            if await inter.bot.is_trusted(inter.author):
                return True

        raise CustomCheckFailure(
            "Insufficient permissions (administrator permission or bot trusted user required. If this happens again and you have the administrator permission, report this)"
        )

    return commands.check(predicate)


def always_failing_check():
    """This check will never pass"""

    def predicate(inter):
        raise CustomCheckFailure("This check (test) will never pass")

    return commands.check(predicate)


def is_not_blacklisted():
    """Check to make sure the user is not blacklisted"""

    async def predicate(inter):
        if not isinstance(inter.bot, TheDiscordMathProblemBot):
            raise TypeError("Uh oh!")
        user_data: UserData = await inter.bot.cache.get_user_data(
            user_id=inter.author.id,
            default=UserData(user_id=inter.author.id, trusted=False, blacklisted=False),
        )
        if user_data.blacklisted:
            raise BlacklistedException("You are blacklisted from the bot!")
        return True

    return commands.check(predicate)


def guild_not_blacklisted():
    """Check to make sure a command isn't being executed in a blacklisted guild -- instead, we will say the guild has been blacklisted & leave the guild"""

    async def predicate(inter: disnake.ApplicationCommandInteraction):
        """The actual check"""
        if not isinstance(inter.bot, TheDiscordMathProblemBot):
            raise TypeError("Uh oh! inter.bot isn't TheDiscordMathProblemBot")
        if await inter.bot.is_guild_blacklisted(inter.guild):
            await inter.send("This guild has just been blacklisted -- therefore I'm leaving."
                             f"However, my source code is available at {inter.bot.constants.SOURCE_CODE_LINK}",
                             ephemeral=True)
            await inter.bot.notify_guild_on_guild_leave_because_guild_blacklist(inter.guild)
            return False
        return True

    return commands.check(predicate)
