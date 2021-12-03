"Admin-related commands"
import random
import dislash
import typing
import nextcord
import nextcord.ext.commands as nextcord_commands
from dislash import *
from nextcord.mentions import AllowedMentions

from .helper_cog import HelperCog
from helpful_modules import checks, cooldowns, the_documentation_file_loader
from helpful_modules.custom_embeds import *

from helpful_modules.save_files import FileSaver
from helpful_modules import problems_module
from helpful_modules.threads_or_useful_funcs import generate_new_id

slash = None


class DeveloperCommands(HelperCog):
    def __init__(self, bot):
        global checks

        super().__init__(bot)
        self.bot = bot
        self.slash = bot.slash
        # checks = self.checks
        checks.setup(bot)

    @dislash.cooldown(1, 5)
    @slash_command(
        name="force_load_files",
        description="Force loads files to replace dictionaries. THIS WILL DELETE OLD DICTS!",
    )
    @checks.trusted_users_only()
    async def force_load_files(self, inter) -> None:
        "Forcefully load files"

        if inter.author.id not in self.bot.trusted_users:
            await inter.reply(
                ErrorEmbed(
                    """You aren't a trusted user.
                    Therefore, you don't have permission to force-load files."""
                )
            )
            return
        try:
            FileSaver3 = FileSaver(enabled=True, printSuccessMessagesByDefault=False)
            FileSaverDict = FileSaver3.load_files(self.bot.cache)
            (guildMathProblems, self.bot.trusted_users, self.bot.vote_threshold) = (
                FileSaverDict["guildMathProblems"],
                FileSaverDict["trusted_users"],
                FileSaverDict["vote_threshold"],
            )
            FileSaver3.goodbye()
            del guildMathProblems
            await inter.reply(
                embed=SuccessEmbed("Successfully forcefully loaded files!")
            )
            return
        except RuntimeError:
            await inter.reply(embed=ErrorEmbed("Something went wrong..."))
            # return
            raise  # I actually want to fix this bug!

    @dislash.cooldown(1, 5)
    @slash_command(
        name="force_save_files",
        description="Forcefully saves files (can only be used by trusted users).",
    )
    @checks.trusted_users_only()
    async def force_save_files(self, inter):

        """Forcefully saves files. Takes no arguments. Mostly for debugging purposes"""

        if inter.author.id not in self.bot.trusted_users:
            await inter.reply(
                embed=ErrorEmbed(
                    "You aren't trusted and therefore don't have permission to forcesave files."
                )
            )
            return
        try:
            FileSaver2 = FileSaver(enabled=True)
            FileSaver2.save_files(
                self.bot.cache,
                True,
                {},
                self.bot.vote_threshold,
                {},
                self.bot.trusted_users,
            )
            FileSaver2.goodbye()
            await inter.reply(embed=SuccessEmbed("Successfully saved 4 files!"))
        except RuntimeError as exc:
            await inter.reply(embed=ErrorEmbed("Something went wrong..."))
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
    async def raise_error(self, inter, error_type, error_description=None) -> None:
        """/raise_error {error_type: str|Exception} [error_description: str = None]
        This command raises an error (of type error_type) that has the description of the error_description.
        You must be a trusted user and the bot owner to run this command!
        The purpose of this command is to test the bot's on_slash_command_error event!"""
        if (
            inter.author.id not in self.bot.trusted_users
        ):  # Check that the user is a trusted user
            await inter.send(
                embed=ErrorEmbed(
                    f"⚠ {inter.author.mention}, you do not have permission to intentionally raise errors for debugging purposes.",
                    custom_title="Insufficient permission to raise errors.",
                ),
                allowed_mentions=nextcord.AllowedMentions(
                    everyone=False, users=[], roles=[], replied_user=False
                ),
            )
            return
        if error_description == None:
            error_description = f"Manually raised error by {inter.author.mention}"
        if error_type == "Exception":
            error = Exception(error_description)
        else:
            raise RuntimeError(f"Unknown error: {error_type}")
        await inter.send(
            embed=SuccessEmbed(
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
    @nextcord_commands.cooldown(1, 5, nextcord_commands.BucketType.user)
    @nextcord_commands.cooldown(500, 750, nextcord_commands.BucketType.default)
    async def documentation(
        self, inter, documentation_type, help_obj
    ) -> typing.Optional[nextcord.Message]:
        """/documentation {documentation_type: str|documentation_link|command_help|function_help} {help_obj}

        Prints documentation :-). If the documentation is a command, it attempts to get its docstring.
        Otherwise, it gets the cached documentation.
        Legend (for other documentation)
        /command_name: the command
        {argument_name: type |choice1|choice2|...} (for a required argument with choices of type type, and the avaliable choices are choice1, choice 2, etc)
        {argument_name: type |choice1|choice2|... = default} (an optional argument that defaults to default if not specified. Arguments must be a choice specified(from choice 1 etc) and must be of the type specified.)
        [argument_name: type = default] (an argument with choices of type type, and defaults to default if not specified. Strings are represented without quotation marks.)
        (argument_name: type) A required argument of type type"""
        if documentation_type == "documentation_link":
            await inter.reply(
                embed=SuccessEmbed(
                    f"""<@{inter.author.id}> [Click here](https://github.com/rf20008/TheDiscordMathProblemBotRepo/tree/master/docs) for my documentation.
        """
                ),
                ephemeral=True,
            )
            return None
        if documentation_type == "command_help":
            # Might fail
            commands = self.bot.slash.slash_commands
            try:
                command_func = commands[help_obj]
                command_docstring = command_func.__doc__
                if command_docstring is None:
                    return await inter.reply(
                        "Either there is a bug in the bot... or in the dislash library... or your command does not have documentation... or all 3. Anyway, if this happens, please report it!"
                    )
                return await inter.reply(
                    embed=SuccessEmbed(description=str(command_docstring))
                )
            except KeyError:
                return await inter.reply(
                    embed=ErrorEmbed(
                        custom_title="I couldn't find your command!",
                        description=":x: Could not find the command specified. ",
                    )
                )
            except AttributeError as exc:
                # My experiment failed
                raise Exception("uh oh...") from exc  # My experiment failed!
        documentation_loader = the_documentation_file_loader.DocumentationFileLoader()
        try:
            _documentation = documentation_loader.get_documentation(
                {
                    "function_help": "docs/misc-non-commands-documentation.md",
                }[documentation_type],
                help_obj,
            )
        except the_documentation_file_loader.DocumentationNotFound as e:
            if isinstance(e, the_documentation_file_loader.DocumentationFileNotFound):
                await inter.reply(
                    embed=ErrorEmbed(
                        "Documentation file was not found. Please report this error!"
                    )
                )
                return None
            await inter.reply(embed=ErrorEmbed(str(e)))
            return None
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
        ] = self.bot.cache.max_guild_problems  # the problem limit
        debug_dict["reached_max_problems?"] = (
            "✅"
            if len(await self.bot.cache.get_guild_problems(guild))
            >= self.bot.cache.max_guild_problems
            else "❌"
        )
        debug_dict["num_guild_problems"] = len(
            await self.bot.cache.get_guild_problems(inter.guild)
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

    @slash_command(
        name="generate_new_problems",
        description="Generates new problems",
        options=[
            Option(
                name="num_new_problems_to_generate",
                description="the number of problems that should be generated",
                type=OptionType.INTEGER,
                required=True,
            )
        ],
    )
    async def generate_new_problems(self, inter, num_new_problems_to_generate):
        "Generate new Problems"
        await cooldowns.check_for_cooldown(
            inter, "generate_new_problems", 30
        )  # 30 second cooldown!
        await inter.create_response(type=5)

        if inter.author.id not in self.bot.trusted_users:
            await inter.reply(embed=ErrorEmbed("You aren't trusted!", ephemeral=True))
            return
        if num_new_problems_to_generate > 200:
            await inter.reply(
                "You are trying to create too many problems. Try something smaller than or equal to 200.",
                ephemeral=True,
            )

        for i in range(num_new_problems_to_generate):  # basic problems for now.... :(
            operation = random.choice(["+", "-", "*", "/", "^"])
            if operation == "^":
                num1 = random.randint(1, 20)
                num2 = random.randint(1, 20)
            else:
                num1 = random.randint(-1000, 1000)
                num2 = random.randint(-1000, 1000)
                while num2 == 0 and operation == "/":  # Prevent ZeroDivisionError
                    num2 = random.randint(-1000, 1000)

            if operation == "^":
                try:
                    answer = num1 ** num2
                except OverflowError:
                    continue
            elif operation == "+":
                answer = num1 + num2
            elif operation == "-":
                answer = num1 - num2
            elif operation == "*":
                answer = num1 * num2
            elif operation == "/":
                answer = round(num1 * 100 / num2) / 100

        while True:
            problem_id = generate_new_id()
            if problem_id not in [
                problem.id for problem in await self.cache.get_global_problems()
            ]:  # All problem_ids
                break
        question = (
            f"What is {num1} "
            + {
                "*": "times",
                "+": "times",
                "-": "minus",
                "/": "divided by",
                "^": "to the power of",
            }[operation]
            + f" {str(num2)}?"
        )
        Problem = problems_module.BaseProblem(
            question=question,
            answer=str(answer),
            author=845751152901750824,
            guild_id=None,
            id=problem_id,
            cache=self.cache,
        )
        await self.cache.add_problem(None, problem_id, Problem)
        await inter.reply(
            embed=SuccessEmbed(
                f"Successfully created {str(num_new_problems_to_generate)} new problems!"
            ),
            ephemeral=True,
        )


def setup(bot):
    global problems_module, SuccessEmbed, ErrorEmbed, the_documentation_file_loader, slash

    bot.add_cog(DeveloperCommands(bot))


def teardown(bot):
    bot.remove_cog("DeveloperCommands")
