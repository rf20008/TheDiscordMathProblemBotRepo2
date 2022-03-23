import json
import typing
from asyncio import sleep as asyncio_sleep
from copy import copy
from io import BytesIO  # For file submitting!
from os import cpu_count
from sys import version, version_info
from time import asctime
from typing import Union

import disnake
from disnake.ext import commands

from .deletion_view import GuildDataDeletionView
from helpful_modules import checks, problems_module, the_documentation_file_loader
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules.custom_buttons import BasicButton, ConfirmationButton, MyView
from helpful_modules.custom_embeds import SimpleEmbed, SuccessEmbed, ErrorEmbed
from helpful_modules.save_files import FileSaver
from helpful_modules.threads_or_useful_funcs import get_git_revision_hash

from .helper_cog import HelperCog

CAN_SEND_MESSAGES_TO = (
    disnake.MessageInteraction,
    disnake.ApplicationCommandInteraction,
    disnake.Interaction,
    disnake.abc.Messageable,
    disnake.TextChannel,
    disnake.PartialMessageable,
    commands.Context,
    disnake.VoiceChannel,
    disnake.Thread,
    disnake.abc.GuildChannel,
)
GUILD_DATA_DELETION_TIMEOUT = 250


class MiscCommandsCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)
        checks.setup(bot)  # Sadly, Interactions do not have a bot parameter
        self.bot: TheDiscordMathProblemBot = bot
        self.cache: problems_module.MathProblemCache = bot.cache

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.slash_command(
        name="info",
        description="Bot info!",
        options=[
            disnake.Option(
                name="include_extra_info",
                description="Whether to include extra, technical info",
                required=False,
                type=disnake.OptionType.boolean,
            )
        ],
    )
    async def info(
        self,
        inter: disnake.ApplicationCommandInteraction,
        include_extra_info: bool = False,
    ):
        """/info [include_extra_info: bool = False]
        Show bot info. include_extra_info shows technical information!"""
        embed = SimpleEmbed(title="Bot info", description="")
        embed = embed.add_field(
            name="Original Bot Developer", value="ay136416#2707", inline=False
        )  # Could be sufficient for attribution (except for stating changes).
        embed = embed.add_field(
            name="Github Repository Link", value=self.bot.constants.SOURCE_CODE_LINK
        )
        embed = embed.add_field(
            name="Latest Git Commit Hash",
            value=str(get_git_revision_hash()),
            inline=False,
        )
        embed = embed.add_field(
            name="Current Latency to Discord",
            value=f"{round(self.bot.latency * 10000) / 10}ms",
            inline=False,
        )
        current_version_info = version_info
        python_version_as_str = f"""Python {
        current_version_info.major
        }.{
        current_version_info.minor
        }.{
        current_version_info.micro}{
        current_version_info.releaselevel
        }"""

        embed = embed.add_field(
            name="Python version", value=python_version_as_str, inline=False
        )  # uh oh
        if include_extra_info:
            embed = embed.add_field(
                name="Python version given by sys.version", value=str(version)
            )

            # embed = embed.add_field(
            #    name="Nextcord version", value=str(disnake.__version__)
            # )
            embed = embed.add_field(
                name="Disnake version", value=str(disnake.__version__)
            )
            embed = embed.add_field(
                name="""CPU count 
                (which may not necessarily be the amount of CPU available to the bot due to a Python limitation)""",
                value=str(cpu_count()),
            )
            embed = embed.add_field(
                name="License",
                value="""This bot is licensed under GPLv3. 
                Please see [the official GPLv3 website that explains the GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html) for more details.""",
                # noqa: E501
            )
            embed = embed.add_field(
                name="Uptime",
                value=(
                    f"""The bot started at" 
                    f"{disnake.utils.format_dt(self.bot.timeStarted)}"
                    f"and has been up for {round(self.bot.uptime)} seconds."""
                ),
            )

        await inter.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)  # 5 second user cooldown
    @commands.cooldown(
        20, 50, commands.BucketType.default
    )  # 20 times before a global cooldown of 50 seconds is established
    @commands.guild_only()  # Due to bugs, it doesn't work in DM's
    @commands.slash_command(
        name="list_trusted_users", description="list all trusted users"
    )
    async def list_trusted_users(self, inter):
        """/list_trusted_users
        List all trusted users in username#discriminator format (takes no arguments)"""
        # await inter.send(type=5)  # Defer
        # Deferring might be unnecessary & and cause errors
        # We might not be able to respond in time because of the 100ms delay between user fetching
        # This is to respect the API rate limit.

        # We don't need a try/except
        result = await self.cache.run_sql("SELECT * FROM user_data")
        trusted_users = []
        for item in result:
            if item["trusted"]:
                trusted_users.append(item["user_id"])
        if len(trusted_users) == 0:
            await inter.send("There are no trusted users.")
            return
            # raise Exception("There are no trusted users!")

        __trusted_users = ""

        for user_id in trusted_users:
            try:
                user = await self.bot.fetch_user(user_id)
                __trusted_users += f"""{user.name}#{user.discriminator}
            """
            except (disnake.NotFound, disnake.NotFound):
                # A user with this ID does not exist
                try:
                    user_data = await self.bot.cache.get_user_data(
                        user_id, default=problems_module.UserData.default()
                    )
                    user_data.trusted = False
                    await self.cache.set_user_data(user_id, user_data)

                    try:
                        del f
                    except NameError:
                        pass
                except BaseException as e:
                    raise RuntimeError(
                        "Could not save the files after removing the nonexistent trusted user!!"
                    ) from e
            except (
                disnake.Forbidden,
                disnake.Forbidden,
            ) as exc:  # Cannot fetch this user!
                raise RuntimeError("Cannot fetch users") from exc
            else:
                await asyncio_sleep(
                    0.1
                )  # 100 ms between fetching to respect the rate limit (and to prevent spam)

        await inter.send(__trusted_users, ephemeral=True)

    @checks.has_privileges(blacklisted=False)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.slash_command(
        name="ping", description="Prints latency and takes no arguments"
    )
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """Ping the bot which returns its latency! This command does not take any arguments."""
        # TODO: round-trip latency, etc
        await inter.send(
            embed=SuccessEmbed(
                f"Pong! My latency is {round(self.bot.latency * 1000)}ms."
            ),
            ephemeral=True,
        )

    @checks.is_not_blacklisted()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="what_is_vote_threshold",
        description="Prints the vote threshold and takes no arguments",
    )
    async def what_is_vote_threshold(
        self, inter: disnake.ApplicationCommandInteraction
    ):
        """/what_is_vote_threshold
        Returns the vote threshold. Takes no arguments.
        There is a 5-second cooldown on this command."""
        await inter.send(
            embed=SuccessEmbed(f"The vote threshold is {self.bot.vote_threshold}."),
            ephemeral=True,
        )

    @checks.has_privileges(blacklisted=False)
    @commands.slash_command(
        name="generate_invite_link",
        description="Generates a invite link for this bot! Takes no arguments",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def generate_invite_link(self, inter: disnake.ApplicationCommandInteraction):
        """/generate_invite_link
        Generate an invite link for the bot. Takes no arguments"""
        await inter.send(
            embed=SuccessEmbed(
                disnake.utils.oauth_url(
                    client_id=self.bot.application_id,
                    permissions=disnake.Permissions(
                        send_messages=True,
                        read_messages=True,
                        embed_links=True,
                        use_slash_commands=True,
                        attach_files=True,
                    ),
                    scopes=["bot", "applications.commands"],
                )
            ),
            ephemeral=True,
        )

    @commands.slash_command(
        name="github_repo", description="Returns the link to the github repo"
    )
    @commands.cooldown(2, 120, commands.BucketType.user)
    async def github_repo(self, inter: disnake.ApplicationCommandInteraction):
        """/github_repo
        Gives you the link to the bot's GitHub repo.
        If you fork this, you must link the new source code link due to the GPL.
        There is a 2-minute cooldown on this command (after it has been executed 2 times)
        """
        await inter.send(
            embed=SuccessEmbed(
                f"[Repo Link:]({self.bot.constants.SOURCE_CODE_LINK})",
                successTitle="Here is the Github Repository Link.",
            )
        )

    @checks.trusted_users_only()
    @commands.cooldown(
        1, 50, commands.BucketType.user
    )  # Don't overload the bot (although trusted users will probably not)
    @commands.cooldown(
        15, 500, commands.BucketType.default
    )  # To prevent wars! If you want your own version, self host it :-)
    @commands.slash_command(
        name="set_vote_threshold",
        description="Sets the vote threshold",
        options=[
            disnake.Option(
                name="threshold",
                description="the threshold you want to change it to",
                type=disnake.OptionType.integer,
                required=True,
            )
        ],
    )
    async def set_vote_threshold(
        self, inter: disnake.ApplicationCommandInteraction, threshold: int
    ):
        """/set_vote_threshold [threshold: int]
        Set the vote threshold. Only trusted users may do this.
        There is a 50-second cooldown.
        This might cause a race condition"""
        # try:
        #    threshold = int(threshold)
        # except TypeError:  # Conversion failed!
        #    await inter.send(
        #        embed=ErrorEmbed(
        #            "Invalid threshold argument! (threshold must be an integer)"
        #        ),
        #        ephemeral=True,
        #    )
        #    return
        # Unnecessary because the type is an integer
        if threshold < 1:  # Threshold must be greater than 1!
            await inter.send(
                embed=ErrorEmbed("You can't set the threshold to smaller than 1."),
                ephemeral=True,
            )
            return
        vote_threshold = int(threshold)  # Probably unnecessary
        for problem in await self.bot.cache.get_global_problems():
            if problem.get_num_voters() >= vote_threshold:
                # If the number of the voters of the problem exceeds the vote threshold,
                # delete the problem.
                await self.cache.remove_problem(problem.id)
        await inter.send(
            embed=SuccessEmbed(
                f"The vote threshold has successfully been changed to {threshold}!"
            ),
            ephemeral=True,
        )
        return

    @commands.slash_command(description="Interact with your user data")
    async def user_data(self, inter: disnake.ApplicationCommandInteraction):
        """The base command to interact with your user data.
        This doesn't do anything (you need to call a subcommand)"""
        pass

    @checks.has_privileges(blacklisted=False)
    @disnake.ext.commands.cooldown(1, 500, commands.BucketType.user)  # To prevent abuse
    @user_data.sub_command(
        name="delete_all",
        description="Delete all problems, quizzes, and quiz submissions you created!",
        options=[
            disnake.Option(
                name="save_data_before_deletion",
                description=(
                    "Whether to give you your problems or submissions in JSON format!"
                    "Defaults to True"
                ),
                type=disnake.OptionType.boolean,
                required=False,
            ),
            disnake.Option(
                name="delete_votes",
                description="Whether to delete your votes. ",
                type=disnake.OptionType.boolean,
                required=False,
            ),
            disnake.Option(
                name="delete_solves",
                description="Whether to erase whether you have solved a problem or not",
                type=disnake.OptionType.boolean,
                required=False,
            ),
        ],
    )
    async def delete_all(
        self: "MiscCommandsCog",
        inter: disnake.ApplicationCommandInteraction,
        save_data_before_deletion: bool = True,
        delete_votes=False,
        delete_solves=False,
    ):
        """/user_data delete_all [save_data_before_deletion: bool = True] [delete_votes: bool = False] [delete_solves: bool = False]
        Delete all your data. YOU MUST CONFIRM THIS!
        If save_data_before_deletion, the data about you will be sent as a json file
        This has a 500-second cooldown.

        You cannot use this command if you are blacklisted.

        This command will delete your permissions --

        By using this command, you agree to being DMed!"""
        if save_data_before_deletion:
            json_data: dict = await self._get_json_data_by_user(
                inter.author
            )  # Get the data
            file_version = self._file_version_of_item(
                str(json_data), file_name="your_data.json"
            )  # Turn it into a dictionary

        async def confirm_callback(
            Self: ConfirmationButton,
            interaction: disnake.Interaction,
            _extra_data: dict,
        ) -> None:
            """The function that runs when the button gets pressed. This actually deletes the data.
            Time complexity: O(V*N+P+S*M)
            V: number of problems user voted for
            N: number of votes for each problem the user voted for
            S: number of problems user solved
            M: number of solvers for each problem the user solved
            P: number of problems user created
            """
            assert Self.check(interaction)
            kwargs = {
                "content": "Successfully deleted your data! Your data should now be cleared now."
            }
            if "file" in _extra_data.keys():
                # Return the file
                kwargs["file"] = _extra_data["file"]

            await _extra_data["cache"].delete_all_by_user_id(interaction.user.id)
            if _extra_data["delete_votes"]:
                problems_to_remove_votes_for = await _extra_data[
                    "cache"
                ].get_problems_by_func(
                    func=lambda prob, user_id: user_id in prob.voters,  # prob: problem
                    args=[interaction.user.id],
                )
                for problem in problems_to_remove_votes_for:
                    problem.voters.remove(interaction.user.id)
                    await problem.update_self()
            if _extra_data["delete_solves"]:
                problems_to_remove_solves_for = await _extra_data[
                    "cache"
                ].get_problems_by_func(
                    func=lambda problem, user_id: user_id in problem.solvers,
                    args=[interaction.user.id],
                )  # Get all the problems the user voted for
                for problem in problems_to_remove_solves_for:
                    problem.solvers.remove(interaction.user.id)
                    await problem.update_self()

            await interaction.send(**kwargs)
            Self.disable()
            Self.view.stop()
            return

        async def deny_callback(
            button: BasicButton, interaction: disnake.MessageInteraction
        ):
            """A function that runs when the deny button is pressed"""
            await interaction.response.send_message(
                "Your data is safe! It has not been deleted."
            )
            button.disable()
            button.view.stop()
            return

        _extra_data = {
            "cache": copy(self.bot.cache),
            "delete_votes": delete_votes,
            "delete_solves": delete_solves,
        }
        if save_data_before_deletion:
            _extra_data["file"] = file_version

        def check(interaction: disnake.MessageInteraction):
            return interaction.author.id == inter.author.id

        confirmation_button = ConfirmationButton(
            check=check,
            callback=confirm_callback,
            style=disnake.ButtonStyle.danger,
            label="I'm 100% sure I want to delete my data!",
            disabled=False,
            _extra_data=_extra_data,
        )
        deny_button = BasicButton(
            check=check,
            callback=deny_callback,
            style=disnake.ButtonStyle.green,
            disabled=False,
            label="Never mind....",
        )
        view = MyView(timeout=30, items=[confirmation_button, deny_button])
        return await inter.send(
            embed=SimpleEmbed(
                title="Are you sure?", description="This will delete all your data!"
            ),
            view=view,
        )

    async def _get_json_data_by_user(
        self, author: Union[disnake.User, disnake.Member]
    ) -> typing.Dict[str, typing.Any]:
        """
        Return a user's stored data as a dictionary.
        """
        raw_data = await self.cache.get_all_by_author_id(author.id)
        problems_user_voted_for = await self.cache.get_problems_by_func(
            func=lambda problem, user_id: user_id in problem.voters, args=(author,)
        )
        # self.bot.log.trace("Getting problems user voted & solved.")
        problems_user_solved = await self.cache.get_problems_by_func(
            func=lambda problem, user_id: user_id in problem.solvers, args=(author,)
        )
        user_data: problems_module.UserData = await self.bot.cache.get_user_data(
            user_id=author.id,
            default=problems_module.UserData(
                user_id=author.id, trusted=False, blacklisted=False
            ),
        )
        is_trusted_user = user_data.trusted
        is_blacklisted = user_data.blacklisted

        new_data = {
            "Problems": [problem.to_dict() for problem in raw_data["problems"]],
            "Quiz Problems": [
                quiz_problem.to_dict() for quiz_problem in raw_data["quiz_problems"]
            ],
            "Quiz Submissions": [
                submission.to_dict() for submission in raw_data["quiz_submissions"]
            ],
            "Quiz Sessions Created": [
                session.to_dict() for session in raw_data["sessions"]
            ],
            "Descriptions created": [
                description.to_dict()
                for description in raw_data["descriptions_created"]
            ],
            "Problems the user voted for": [
                problem.to_dict(show_answer=False)
                for problem in problems_user_voted_for
            ],
            "Problems the user solved": [
                problem.to_dict() for problem in problems_user_solved
            ],
            "User status": {
                "trusted_user": is_trusted_user,
                "blacklisted": is_blacklisted,
            },
            "Appeals": [appeal.to_dict() for appeal in raw_data["appeals"]],
        }
        return new_data

    @staticmethod
    def _file_version_of_item(item: str, file_name: str) -> disnake.File:
        """
        Return a disnake.File with the specified filename that contains the string provided.
        """
        assert isinstance(item, str)
        return disnake.File(BytesIO(bytes(item, "utf-8")), filename=file_name)

    @disnake.ext.commands.cooldown(1, 100, disnake.ext.commands.BucketType.user)
    @user_data.sub_command(
        name="get_data",
        description="Get a json-ified version of the data stored with this application!",
    )
    async def get_data(self, inter):
        """/user_data get_data
        Get all the data the bot stores about you.
        To prevent spam and getting rate limited, there is a 100-second cooldown."""
        await inter.response.defer()
        file = disnake.File(
            BytesIO(
                bytes(
                    json.dumps(
                        await self._get_json_data_by_user(inter.author), indent=2
                    ),
                    "utf-8",
                )
            ),
            filename="your_data.json",
        )
        # await inter.send(
        #  embed=SuccessEmbed(
        #    "Your json data will be attached in the next message due to API #limitations!"
        #  ),
        #  ephemeral = True
        # )
        try:
            await inter.send(
                embed=SuccessEmbed("Your data has been attached in this message!"),
                file=file,
            )
            # TODO: when discord api allows sending files in interaction replies, send them the file
        except BaseException as e:  # We can't send it for some reason
            raise e

    @commands.slash_command(
        name="submit_a_request",
        description="Submit a request. I will know!",
        options=[
            disnake.Option(
                name="offending_problem_guild_id",
                description="The guild id of the problem you are trying to remove.",
                type=disnake.OptionType.integer,
                required=False,
            ),
            disnake.Option(
                name="offending_problem_id",
                description="The problem id of the problem. Very important (so I know which problem to check)",
                type=disnake.OptionType.integer,
                required=False,
            ),
            disnake.Option(
                name="extra_info",
                description="A up to 5000 character description (about 2 pages) Use this wisely!",
                type=disnake.OptionType.string,
                required=False,
            ),
            disnake.Option(
                name="copyrighted_thing",
                description="The copyrighted thing that this problem is violating",
                type=disnake.OptionType.string,
                required=False,
            ),
            disnake.Option(
                name="type",
                description="Request type",
                required=False,
                type=disnake.OptionType.string,
            ),
        ],
    )
    async def submit_a_request(
        self,
        inter: disnake.ApplicationCommandInteraction,
        offending_problem_guild_id: int = None,
        offending_problem_id: int = None,
        extra_info: str = None,
        copyrighted_thing: str = Exception,
        type: str = "",
    ):
        """/submit_a_request [offending_problem_guild_id: int = None] [offending_problem_id: int = None]

        Submit a request! I will know! It uses a channel in my discord server and posts an embed.
        If you do not provide a guild id, it will be None.
        I will probably deprecate this and replace it with emailing me.
        This command has been deprecated."""
        if (
            extra_info is None
            and type == ""
            and copyrighted_thing is not Exception
            and offending_problem_guild_id is None
            and offending_problem_id is None
        ):
            await inter.send(embed=ErrorEmbed("You must specify some field."))
        if extra_info is None:
            await inter.send(embed=ErrorEmbed("Please provide extra information!"))
        assert len(extra_info) <= 5000
        try:
            channel = await self.bot.fetch_channel(
                901464948604039209
            )  # CHANGE THIS IF YOU HAVE A DIFFERENT REQUESTS CHANNEL! (the part after id)
            # TODO: make this an env var
        except (disnake.ext.commands.ChannelNotReadable, disnake.Forbidden):
            raise RuntimeError("The bot cannot send messages to the channel!")
        try:
            Problem = await self.bot.cache.get_problem(
                offending_problem_guild_id, offending_problem_id
            )
            problem_found = True
        except (TypeError, KeyError, problems_module.ProblemNotFound):
            # Problem not found
            problem_found = False
        embed = disnake.Embed(
            title=(
                f"A new {type} request has been received from {inter.author.name}#{inter.author.discriminator}!"
            ),
            description="",
        )

        if problem_found:
            embed.description = f"Problem_info:{str(problem)}"  # type: ignore
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
            self.bot.owner_ids
        ):  # Mentioning owners: may be removed (you can also remove it as well)
            content += f"<@{owner_id}>"
        content += f"<@{self.bot.owner_id}>"
        await channel.send(embed=embed, content=content)
        await inter.send("Your request has been submitted!")

    @checks.has_privileges(blacklisted=False)
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.slash_command(
        name="documentation",
        description="Returns help!",
        options=[
            disnake.Option(
                name="documentation_type",
                description="What kind of help you want",
                choices=[
                    disnake.OptionChoice(
                        name="documentation_link", value="documentation_link"
                    ),
                    disnake.OptionChoice(name="command_help", value="command_help"),
                    disnake.OptionChoice(name="function_help", value="function_help"),
                    disnake.OptionChoice(name="privacy_policy", value="privacy_policy"),
                    disnake.OptionChoice(
                        name="terms_of_service", value="terms_of_service"
                    ),
                ],
                required=True,
            ),
            disnake.Option(
                name="help_obj",
                description="What you want help on",
                required=False,
                type=disnake.OptionType.string,
            ),
        ],
    )
    async def documentation(
        self,
        inter: disnake.ApplicationCommandInteraction,
        documentation_type: typing.Literal[
            "documentation_link",  # type: ignore
            "command_help",
            "function_help",
            "privacy_policy",
            "terms_of_service",
        ],
        help_obj: str = None,
    ) -> typing.Optional[disnake.Message]:
        """/documentation {documentation_type: str|documentation_link|command_help|function_help} {help_obj}

        Prints documentation :-). If the documentation is a command, it attempts to get its docstring.
        Otherwise, it gets the cached documentation.
        help_obj will be ignored if documentation_type is privacy_policy or documentation_link.
        Legend (for other documentation)
        /command_name: the command
        {argument_name: type |choice1|choice2|...} -
        A required argument with choices of the given type, and the available choices are choice1, choice 2, etc.
        {argument_name: type |choice1|choice2|... = default} -
        An optional argument that defaults to default if not specified.
        Arguments must be a choice specified (from choice 1 etc.) and must be of the type specified.
        [argument_name: type = default] -
        An argument with choices of the given type, and defaults to default if not specified. Strings are represented without quotation marks.
        (argument_name: type) -
        A required argument of the given type"""
        if help_obj is None and documentation_type in ["command_help", "function_help"]:
            return await inter.send(
                embed=ErrorEmbed(
                    "I can't help you with a command or function unless you tell me what you want help on!"
                )
            )
        if documentation_type == "documentation_link":
            await inter.send(
                embed=SuccessEmbed(
                    f"""<@{inter.author.id}> [Click here](https://github.com/rf20008/TheDiscordMathProblemBotRepo/tree/master/docs) for my documentation.
        """
                ),
                ephemeral=True,
            )
            return None
        if documentation_type == "command_help":
            try:
                command = self.bot.get_slash_command(help_obj)  # Get the command
                if command is None:  # command not found
                    return await inter.send(
                        embed=ErrorEmbed(
                            custom_title="I couldn't find your command!",
                            description=":x: Could not find the command specified. ",
                        )
                    )
                command_docstring = command.callback.__doc__
                if command_docstring is None:
                    return await inter.send(
                        "Oh no! This command does not have documentation! Please report this bug."
                    )
                return await inter.send(
                    embed=SuccessEmbed(description=str(command_docstring))
                )
            except AttributeError as exc:
                # My experiment failed
                raise Exception("uh oh...") from exc  # My experiment failed!
        elif documentation_type == "function_help":
            warnings.warn(DeprecationWarning("This has been deprecated"))
            documentation_loader = (
                the_documentation_file_loader.DocumentationFileLoader()
            )
            try:
                _documentation = documentation_loader.get_documentation(
                    {
                        "function_help": "docs/misc-non-commands-documentation.md",
                    }[documentation_type],
                    help_obj,
                )
            except the_documentation_file_loader.DocumentationNotFound as e:
                if isinstance(
                    e, the_documentation_file_loader.DocumentationFileNotFound
                ):
                    await inter.send(
                        embed=ErrorEmbed(
                            "Documentation file was not found. Please report this error!"
                        )
                    )
                    return None
                await inter.send(embed=ErrorEmbed(str(e)))
                return None
            await inter.send(_documentation)
        elif documentation_type == "privacy_policy":
            await inter.send(
                "The link to the privacy policy is [https://github.com/rf20008/TheDiscordMathProblemBotRepo/blob/beta/TERMS_AND_CONDITIONS.md](here)"
            )
            return
        elif documentation_type == "terms_of_service":
            # TODO: soft-code this in a config.json file
            await inter.send(
                "The link to the terms of service is here: [https://github.com/rf20008/TheDiscordMathProblemBotRepo/blob/beta/TERMS_AND_CONDITIONS.md](Terms of Service Link)"
            )
            return

            # with open("TERMS_AND_CONDITIONS.md") as file:
            #    await inter.send(
            #        embed=SuccessEmbed("".join([line for line in file]))
            #    )  # Concatenate the lines in the file + send them
        else:
            raise NotImplementedError(
                "This hasn't been implemented yet. Please contribute something!"
            )

    @checks.has_privileges(blacklisted=False)
    @checks.trusted_users_only()
    @checks.is_not_blacklisted()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.slash_command(
        name="blacklist",
        description="Blacklist someone from the bot!",
        options=[
            disnake.Option(
                name="user",
                description="The user to blacklist",
                type=disnake.OptionType.user,
                required=True,
            )
        ],
    )
    async def blacklist(
        self: "MiscCommandsCog",
        inter: disnake.ApplicationCommandInteraction,
        user: typing.Union[disnake.User, disnake.Member],
    ):
        """/blacklist [user: user]
        Blacklist someone from the bot. You must be a trusted user to do this!
        There is a 1-second cooldown."""
        user_data = await self.cache.get_user_data(
            user_id=user.id,
            default=problems_module.UserData(
                user_id=user.id, trusted=False, blacklisted=False
            ),
        )
        if not user_data.blacklisted:
            bot.log.debug("Can't blacklist user; user already blacklisted")
            return await inter.send("Can't blacklist user; user already blacklisted")
        else:
            user_data.blacklisted = True
            try:
                await self.cache.update_user_data(user_id=user.id, new=user_data)
            except problems_module.MathProblemsModuleException:
                await self.cache.add_user_data(user_id=user.id, new=user_data)
            self.bot.log.info(f"Successfully blacklisted the user with id {user.id}")
            await inter.send("Successfully blacklisted the user!")

            # TODO: what do I do after a user gets blacklisted? Do I delete their data?

    @checks.trusted_users_only()
    @checks.is_not_blacklisted()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.slash_command(
        name="unblacklist",
        description="Remove someone's blacklist",
        options=[
            disnake.Option(
                name="user",
                description="The user to un-blacklist",
                type=disnake.OptionType.user,
                required=True,
            )
        ],
    )
    async def unblacklist(
        self: "MiscCommandsCog",
        inter: disnake.ApplicationCommandInteraction,
        user: typing.Union[disnake.User, disnake.Member],
    ):
        """/unblacklist [user: user]
        Remove a user's bot blacklist. You must be a trusted user to do this!
        There is a 1-second cooldown."""
        user_data = await self.cache.get_user_data(
            user_id=user.id,
            default=problems_module.UserData(
                user_id=user.id, trusted=False, blacklisted=False
            ),
        )
        if not user_data.blacklisted:
            bot.log.debug("Can't un-blacklist user; user not blacklisted")
            return await inter.send("Can't un-blacklist user; user not blacklisted")
        else:
            user_data.blacklisted = False
            try:
                await self.cache.update_user_data(user_id=user.id, new=user_data)
            except problems_module.MathProblemsModuleException:
                await self.cache.add_user_data(user_id=user.id, new=user_data)
            self.bot.log.info(f"Successfully un-blacklisted the user with id {user.id}")
            await inter.send("Successfully un-blacklisted the user!")

            # TODO: what do I do after a user gets blacklisted? Do I delete their data?

    async def documentation(
        self,
        inter: disnake.ApplicationCommandInteraction,
        documentation_type: typing.Literal[
            "documentation_link",  # type: ignore
            "command_help",
            "function_help",
            "privacy_policy",
            "terms_of_service",
        ],
        help_obj: str = None,
    ) -> typing.Optional[disnake.Message]:
        """/documentation {documentation_type: str|documentation_link|command_help|function_help} {help_obj}

        Prints documentation :-). If the documentation is a command, it attempts to get its docstring.
        Otherwise, it gets the cached documentation.
        help_obj will be ignored if documentation_type is privacy_policy or documentation_link.
        Legend (for other documentation)
        /command_name: the command
        {argument_name: type |choice1|choice2|...} -
        A required argument with choices of the given type, and the available choices are choice1, choice 2, etc.
        {argument_name: type |choice1|choice2|... = default} -
        An optional argument that defaults to default if not specified.
        Arguments must be a choice specified (from choice 1 etc.) and must be of the type specified.
        [argument_name: type = default] -
        An argument with choices of the given type, and defaults to default if not specified. Strings are represented without quotation marks.
        (argument_name: type) -
        A required argument of the given type"""
        if help_obj is None and documentation_type in ["command_help", "function_help"]:
            return await inter.send(
                embed=ErrorEmbed(
                    "I can't help you with a command or function unless you tell me what you want help on!"
                )
            )
        if documentation_type == "documentation_link":
            await inter.send(
                embed=SuccessEmbed(
                    f"""<@{inter.author.id}> [Click here](https://github.com/rf20008/TheDiscordMathProblemBotRepo/tree/master/docs) for my documentation.
        """
                ),
                ephemeral=True,
            )
            return None
        if documentation_type == "command_help":
            try:
                command = self.bot.get_slash_command(help_obj)  # Get the command
                if command is None:  # command not found
                    return await inter.send(
                        embed=ErrorEmbed(
                            custom_title="I couldn't find your command!",
                            description=":x: Could not find the command specified. ",
                        )
                    )
                command_docstring = command.callback.__doc__
                if command_docstring is None:
                    return await inter.send(
                        "Oh no! This command does not have documentation! Please report this bug."
                    )
                return await inter.send(
                    embed=SuccessEmbed(description=str(command_docstring))
                )
            except AttributeError as exc:
                # My experiment failed
                raise Exception("uh oh...") from exc  # My experiment failed!
        elif documentation_type == "function_help":
            warnings.warn(DeprecationWarning("This has been deprecated"))
            documentation_loader = (
                the_documentation_file_loader.DocumentationFileLoader()
            )
            try:
                _documentation = documentation_loader.get_documentation(
                    {
                        "function_help": "docs/misc-non-commands-documentation.md",
                    }[documentation_type],
                    help_obj,
                )
            except the_documentation_file_loader.DocumentationNotFound as e:
                if isinstance(
                    e, the_documentation_file_loader.DocumentationFileNotFound
                ):
                    await inter.send(
                        embed=ErrorEmbed(
                            "Documentation file was not found. Please report this error!"
                        )
                    )
                    return None
                await inter.send(embed=ErrorEmbed(str(e)))
                return None
            await inter.send(_documentation)
        elif documentation_type == "privacy_policy":
            await inter.send(
                "The link to the privacy policy is [https://github.com/rf20008/TheDiscordMathProblemBotRepo/blob/beta/TERMS_AND_CONDITIONS.md](here)"
            )
            return
        elif documentation_type == "terms_of_service":
            # TODO: softcode this in a config.json file
            await inter.send(
                "The link to the terms of service is here: [https://github.com/rf20008/TheDiscordMathProblemBotRepo/blob/beta/TERMS_AND_CONDITIONS.md](Terms of Service Link)"
            )
            return

            # with open("TERMS_AND_CONDITIONS.md") as file:
            #    await inter.send(
            #        embed=SuccessEmbed("".join([line for line in file]))
            #    )  # Concatenate the lines in the file + send them
        else:
            raise NotImplementedError(
                "This hasn't been implemented yet. Please contribute something!"
            )

    @checks.has_privileges(blacklisted=False)
    @checks.trusted_users_only()
    @checks.is_not_blacklisted()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.slash_command(
        name="blacklist",
        description="Blacklist someone from the bot!",
        options=[
            disnake.Option(
                name="user",
                description="The user to blacklist",
                type=disnake.OptionType.user,
                required=True,
            )
        ],
    )
    async def blacklist(
        self: "MiscCommandsCog",
        inter: disnake.ApplicationCommandInteraction,
        user: typing.Union[disnake.User, disnake.Member],
    ):
        """/blacklist [user: user]
        Blacklist someone from the bot. You must be a trusted user to do this!
        There is a 1-second cooldown."""
        user_data = await self.cache.get_user_data(
            user_id=user.id,
            default=problems_module.UserData(
                user_id=user.id, trusted=False, blacklisted=False
            ),
        )
        if not user_data.blacklisted:
            bot.log.debug("Can't blacklist user; user already blacklisted")
            return await inter.send("Can't blacklist user; user already blacklisted")
        else:
            user_data.blacklisted = True
            try:
                await self.cache.update_user_data(user_id=user.id, new=user_data)
            except problems_module.MathProblemsModuleException:
                await self.cache.add_user_data(user_id=user.id, new=user_data)
            self.bot.log.info(f"Successfully blacklisted the user with id {user.id}")
            await inter.send("Successfully blacklisted the user!")

            # TODO: what do I do after a user gets blacklisted? Do I delete their data?

    @checks.trusted_users_only()
    @checks.is_not_blacklisted()
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.slash_command(
        name="unblacklist",
        description="Remove someone's blacklist",
        options=[
            disnake.Option(
                name="user",
                description="The user to un-blacklist",
                type=disnake.OptionType.user,
                required=True,
            )
        ],
    )
    async def unblacklist(
        self: "MiscCommandsCog",
        inter: disnake.ApplicationCommandInteraction,
        user: typing.Union[disnake.User, disnake.Member],
    ):
        """/unblacklist [user: user]
        Remove a user's bot blacklist. You must be a trusted user to do this!
        There is a 1-second cooldown."""
        user_data = await self.cache.get_user_data(
            user_id=user.id,
            default=problems_module.UserData(
                user_id=user.id, trusted=False, blacklisted=False
            ),
        )
        if not user_data.blacklisted:
            bot.log.debug("Can't un-blacklist user; user not blacklisted")
            return await inter.send("Can't un-blacklist user; user not blacklisted")
        else:
            user_data.blacklisted = False
            try:
                await self.cache.update_user_data(user_id=user.id, new=user_data)
            except problems_module.MathProblemsModuleException:
                await self.cache.add_user_data(user_id=user.id, new=user_data)
            self.bot.log.info(f"Successfully un-blacklisted the user with id {user.id}")
            await inter.send("Successfully un-blacklisted the user!")

            # TODO: what do I do after a user gets blacklisted? Do I delete their data?

    @checks.guild_owners_or_trusted_users_only()
    @checks.is_not_blacklisted()
    @checks.guild_not_blacklisted()
    @commands.slash_command(description="Request for your guild's data to be deleted")
    async def request_guild_data_delete(
        self, inter: disnake.ApplicationCommandInteraction
    ):
        """/request_guild_data_delete

        Requests the deletion of the data stored with this bot associated with the guild.
        Only guild owners can run this. There is also a confirmation view to confirm.
        You will have 2 minutes to click a button, or nothing will happen!"""
        try:
            assert inter.guild is not None
            assert (
                await self.bot.is_trusted(inter.author)
                or inter.author.id == inter.guild.owner_id
            )
        except AssertionError:
            await inter.send("You don't have permission!")
            raise
        assert isinstance(inter.channel, CAN_SEND_MESSAGES_TO)
        view = GuildDataDeletionView(
            inter=inter, timeout=GUILD_DATA_DELETION_TIMEOUT, bot=self.bot
        )
        await inter.send(view=view)
        msg = await inter.original_message()
        try:
            _ = await bot.wait_for(
                "button_click", check=lambda i: i.author.id == inter.author.id, timeout=120
            )
        except asyncio.TimeoutError:
            view.stop()
            for item in view.children:
                if not isinstance(item, disnake.ui.Item):
                    raise RuntimeError()
                if hasattr(item, "disabled"):
                    if not getattr(item, "disabled", False):
                        item.disabled = True

            await msg.edit(
                content="You didn't respond in time, so the view has now been closed"
                + msg.content,  # noqa: E501
                view=view,
            )
            return await inter.channel.send("You didn't submit in time!")
        return


def setup(bot):
    bot.add_cog(MiscCommandsCog(bot))


def teardown(bot):
    bot.remove_cog("MiscCommandsCog")
