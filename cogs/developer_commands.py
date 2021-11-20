#
import random, os, warnings, threading, copy, nextcord, subprocess
import dislash, traceback

import nextcord.ext.commands as nextcord_commands
from dislash import *
from time import sleep, time, asctime

from .helper_cog import HelperCog
from helpful_modules import checks, cooldowns, the_documentation_file_loader
from helpful_modules.custom_embeds import *

from helpful_modules.save_files import FileSaver

from . import *

slash = None


class DeveloperCommands(HelperCog):
    def __init__(self, bot):
        global checks
        
        super().__init__(bot)
        self.bot = bot
        self.slash = bot.slash
        checks = self.checks
        checks.setup(bot)

    @dislash.cooldown(1, 5)
    @slash_command(
        name="force_load_files",
        description="Force loads files to replace dictionaries. THIS WILL DELETE OLD DICTS!",
    )
    @checks.trusted_users_only()
    async def force_load_files(self, inter):
        "Forcefully load files"

        if inter.author.id not in self.bot.trusted_users:
            await inter.reply(
                self.custom_embeds.ErrorEmbed(
                    "You aren't trusted and therefore don't have permission to forceload files."
                )
            )
            return
        try:
            FileSaver3 = FileSaver(enabled=True, printSuccessMessagesByDefault=False)
            FileSaverDict = FileSaver3.load_files(self.bot.main_cache)
            (guildMathProblems, self.bot.trusted_users, self.bot.vote_threshold) = (
                FileSaverDict["guildMathProblems"],
                FileSaverDict["trusted_users"],
                FileSaverDict["vote_threshold"],
            )
            FileSaver3.goodbye()
            await inter.reply(
                embed=self.custom_embeds.SuccessEmbed(
                    "Successfully forcefully loaded files!"
                )
            )
            return
        except RuntimeError:
            await inter.reply(
                embed=self.custom_embeds.ErrorEmbed("Something went wrong...")
            )
            return

    @dislash.cooldown(1, 5)
    @slash_command(
        name="force_save_files",
        description="Forcefully saves files (can only be used by trusted users).",
    )
    @checks.trusted_users_only()
    async def force_save_files(self, inter):
        "Forcefully saves files. Takes no arguments. Mostly for debugging purposes"
        if (
            inter.guild != None
            and inter.guild.id not in self.bot.main_cache.get_guilds()
        ):
            self.bot.main_cache.add_empty_guild(inter.guild)
        if inter.author.id not in self.bot.trusted_users:
            await inter.reply(
                embed=self.custom_embeds.ErrorEmbed(
                    "You aren't trusted and therefore don't have permission to forcesave files."
                )
            )
            return
        try:
            FileSaver2 = FileSaver(enabled=True)
            FileSaver2.save_files(
                self.bot.main_cache,
                True,
                {},
                self.bot.vote_threshold,
                {},
                self.bot.trusted_users,
            )
            FileSaver2.goodbye()
            await inter.reply(
                embed=self.custom_embeds.SuccessEmbed("Successfully saved 4 files!")
            )
        except RuntimeError as exc:
            await inter.reply(
                embed=self.custom_embeds.ErrorEmbed("Something went wrong...")
            )
            raise exc
    @dislash.is_owner()
    @dislash.cooldown(1, 5, type=BucketType.user)
    @slash_command(
        name="raise_error",
        description="⚠ This command will raise an error. Useful for testing on_slash_command_error",
        options=[
            Option(
                name="error_type",
                description="The type of error",
                choices=[OptionChoice(name="Exception", value="Exception")],
                required=True,
            ),
            Option(
                name="error_description",
                description="The description of the error",
                type=OptionType.STRING,
                required=False,
            ),
        ],
    )
    async def raise_error(self, inter, error_type, error_description=None):
        "Intentionally raise an Error. Useful for debugging... :-)"
        if inter.author.id not in self.bot.trusted_users:
            await inter.send(
                embed=self.custom_embeds.ErrorEmbed(
                    f"⚠ {inter.author.mention}, you do not have permission to intentionally raise errors for debugging purposes.",
                    custom_title="Insufficient permission to raise errors.",
                )
            )
            return
        if error_description == None:
            error_description = f"Manually raised error by {inter.author.mention}"
        if error_type == "Exception":
            error = Exception(error_description)
        else:
            raise RuntimeError(f"Unknown error: {error_type}")
        await inter.send(
            embed=self.custom_embeds.SuccessEmbed(
                f"Successfully created error: {str(error)}. Will now raise the error.",
                successTitle="Successfully raised error.",
            )
        )
        raise error

    @dislash.cooldown(1, 0.1)
    @slash_command(
        name="documentation",
        description="Returns help!",
        options=[
            Option(
                name="documentation_type",
                description="What kind of help you want",
                choices=[
                    OptionChoice(name="documentation_link", value="documentation_link"),
                    OptionChoice(name="command_help", value="command_help"),
                    OptionChoice(name="function_help", value="function_help"),
                ],
                required=True,
            ),
            Option(
                name="help_obj",
                description="What you want help on",
                required=True,
                type=OptionType.STRING,
            ),
        ],
    )
    async def documentation(self, inter, documentation_type, help_obj):
        "Prints documentation :-)"
        await cooldowns.check_for_cooldown(inter, "documentation", 0.1)
        if documentation_type == "documentation_link":
            await inter.reply(
                embed=self.custom_embeds.SuccessEmbed(
                    f"""<@{inter.author.id}> [Click here](https://github.com/rf20008/TheDiscordMathProblemBotRepo/tree/master/docs) for my documentation.
        """
                ),
                ephemeral=True,
            )
            return None
        documentation_loader = the_documentation_file_loader.DocumentationFileLoader()
        try:
            _documentation = documentation_loader.get_documentation(
                {
                    "command_help": "docs/commands-documentation.md",
                    "function_help": "docs/misc-non-commands-documentation.md",
                }[documentation_type],
                help_obj,
            )
        except the_documentation_file_loader.DocumentationNotFound as e:
            if isinstance(e, the_documentation_file_loader.DocumentationFileNotFound):
                await inter.reply(
                    embed=self.custom_embeds.ErrorEmbed(
                        "Documentation file was not found. Please report this error!"
                    )
                )
                return
            await inter.reply(embed=self.custom_embeds.ErrorEmbed(str(e)))
            return
        await inter.reply(_documentation)

    @dislash.cooldown(1, 0.1)
    @slash_command(
        name="debug",
        description="Helpful for debugging :-)",
        options=[
            Option(
                name="raw",
                description="raw debug data?",
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name="send_ephermally",
                description="Send the debug message ephermally?",
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ],
    )
    async def debug(self, inter, raw=False, send_ephermally=True):
        "Provides helpful debug information :-)"
        guild = inter.guild  # saving me typing trouble!
        if inter.guild is None:
            await inter.reply("This command can only be ran in servers!")
            return
        me = guild.me
        my_permissions = me.guild_permissions
        debug_dict = {}
        debug_dict["guild_id"] = inter.guild.id
        debug_dict["author_id"] = inter.author.id
        debug_dict[
            "problem_limit"
        ] = self.bot.main_cache.max_guild_problems  # the problem limit
        debug_dict["reached_max_problems?"] = (
            "✅"
            if len(self.bot.main_cache.get_guild_problems(guild))
            >= self.bot.main_cache.max_guild_problems
            else "❌"
        )
        debug_dict["num_guild_problems"] = len(
            self.bot.main_cache.get_guild_problems(inter.guild)
        )
        correct_permissions = {
            "read_message_history": "✅" if my_permissions.read_messages else "❌",
            "read_messages": "✅"
            if my_permissions.read_messages
            else "❌",  # can I read messages?
            "send_messages": "✅"
            if my_permissions.send_messages
            else "❌",  # can I send messages?
            "embed_links": "✅"
            if my_permissions.embed_links
            else "❌",  # can I embed links?
            "use_application_commands": "✅"
            if my_permissions.use_slash_commands
            else "❌",
        }
        debug_dict["correct_permissions"] = correct_permissions
        if raw:
            await inter.reply(str(debug_dict), ephemeral=send_ephermally)
            return
        else:
            text = ""
            for item in debug_dict:
                if not isinstance([item], dict):
                    text += f"{item}: {debug_dict.get(item)}\n"
                else:
                    for item2 in item:
                        if not isinstance(item2, dict):
                            text += f"{item.get(item2)}: {debug_dict[item]}"
                        else:
                            raise RecursionError from Exception("***Nested too much***")

        await inter.reply(text, ephemeral=send_ephermally)

def setup(bot):
    global problems_module, SuccessEmbed, ErrorEmbed, the_documentation_file_loader, slash

    bot.add_cog(DeveloperCommands(bot))


def teardown(bot):
    bot.remove_cog("DeveloperCommands")
