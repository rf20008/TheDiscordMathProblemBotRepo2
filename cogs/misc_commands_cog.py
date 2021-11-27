from dislash import *
import nextcord
from .helper_cog import HelperCog
from sys import version_info, version
from helpful_modules import cooldowns
from helpful_modules.custom_embeds import SimpleEmbed, ErrorEmbed, SuccessEmbed
from helpful_modules.save_files import FileSaver
from helpful_modules.threads_or_useful_funcs import get_git_revision_hash
from asyncio import sleep as asyncio_sleep
import resource


class MiscCommandsCog(HelperCog):
    def __init__(self, bot: nextcord.ext.commands.Bot):
        super().__init__(bot)
        self.bot = bot

    @slash_command(
        name="info",
        description="Bot info!",
        options=[
            Option(
                name="include_extra_info",
                description="Whether to include extra, technical info",
                required=False,
                type=OptionType.BOOLEAN,
            )
        ],
    )
    async def info(self, inter, include_extra_info=False):
        embed = SimpleEmbed(title="Bot info", description="")
        embed = embed.add_field(
            name="Original Bot Developer", value="ay136416#2707", inline=False
        )  # Could be sufficient for attribution (except for stating changes).
        embed = embed.add_field(
            name="Latest Git Commit Hash",
            value=str(get_git_revision_hash()),
            inline=False,
        )
        embed = embed.add_field(
            name="Current Latency to Discord",
            value=f"{round(self.bot.latency*10000)/10}ms",
            inline=False,
        )
        current_version_info = version_info
        python_version_as_str = f"Python {current_version_info.major}.{current_version_info.minor}.{current_version_info.micro}{current_version_info.releaselevel}"

        embed = embed.add_field(
            name="Python version", value=python_version_as_str, inline=False
        )
        if include_extra_info:
            embed = embed.add_field(
                name="Python version given by sys.version", value=str(version)
            )

            embed = embed.add_field(
                name="Nextcord version", value=str(nextcord.__version__)
            )

            memory_limit = resource.getrlimit(resource.RUSAGE_SELF)[0]
            current_usage = resource.getrusage(resource.RUSAGE_SELF)

            embed = embed.add_field(
                name="Memory Usage",
                value=f"{round((current_usage[3]/memory_limit)*1000)/100}%",
            )

        await inter.reply(embed=embed)

    @slash_command(name="list_trusted_users", description="list all trusted users")
    @nextcord.ext.commands.cooldown(
        1, 5, nextcord.ext.commands.BucketType.user
      )  # 5 second user cooldown
    @nextcord.ext.commands.cooldown(
        20, 50, nextcord.ext.commands.BucketType.default
    ) #20 times before a global cooldown of 50 seconds is established
    @nextcord.ext.commands.guild_only # Due to bugs, it doesn't work in DM's
    async def list_trusted_users(self, inter):
        "List all trusted users in username#discriminator format (takes no arguments)"
        await inter.reply(type=5)  # Defer
        # We might not be able to respond in time because of the 100ms delay between user fetching
        # This is to respect the API rate limit.
        if len(self.bot.trusted_users) == 0:
            await inter.reply("There are no trusted users.")

            raise Exception("There are no trusted users!")

        __trusted_users = ""

        for user_id in self.bot.trusted_users:
            try:
                user = await self.bot.fetch_user(user_id=user_id)
                __trusted_users += f"""{user.name}#{user.discriminator}
            """
            except nextcord.NotFound:
                # A user with this ID does not exist
                self.bot.trusted_users.remove(user_id)  # delete the user!
                try:
                    f = FileSaver(name=4, enabled=True)
                    f.save_files(
                        self.bot.cache,
                        vote_threshold=self.bot.vote_threshold,
                        trusted_users_list=self.bot.trusted_users,
                    )
                    f.goodbye()  # This should delete it
                    try:
                        del f
                    except NameError:
                        pass
                except BaseException as e:
                    raise RuntimeError(
                        "Could not save the files after removing the trusted user with ID that does not exist!"
                    ) from e
            except nextcord.Forbidden as exc:  # Cannot fetch this user!
                raise RuntimeError("Cannot fetch users") from exc
            else:
                await asyncio_sleep(
                    0.1
                )  # 100 ms between fetching to respect the rate limit (and to prevent spam)

        await inter.reply(__trusted_users, ephemeral=True)

    @slash_command(name="ping", description="Prints latency and takes no arguments")
    
    async def ping(self, inter):
        "Ping the bot which returns its latency!"
        await cooldowns.check_for_cooldown(inter, "ping", 5)
        await inter.reply(
            embed=SuccessEmbed(
                f"Pong! My latency is {round(self.bot.latency*1000)}ms."
            ),
            ephemeral=True,
        )

    @slash_command(
        name="what_is_vote_threshold",
        description="Prints the vote threshold and takes no arguments",
    )
    async def what_is_vote_threshold(self, inter: SlashInteraction):
        "Returns the vote threshold"
        await cooldowns.check_for_cooldown(inter, "what_is_vote_threshold", 5)
        await inter.reply(
            embed=SuccessEmbed(f"The vote threshold is {self.bot.vote_threshold}."),
            ephemeral=True,
        )

    @slash_command(
        name="generate_invite_link",
        description="Generates a invite link for this bot! Takes no arguments",
    )
    async def generate_invite_link(self, inter):
        "Generate an invite link for the bot."
        await cooldowns.check_for_cooldown(inter, "generateInviteLink", 5)
        await inter.reply(
            embed=SuccessEmbed(
                "https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147552256&scope=bot%20applications.commands"
            ),
            ephemeral=True,
        )

    @slash_command(
        name="github_repo", description="Returns the link to the github repo"
    )
    @nextcord.ext.commands.cooldown(2, 120, nextcord.ext.commands.BucketType.user)
    async def github_repo(inter):
        await inter.reply(
            embed=SuccessEmbed(
                "[Repo Link:](https://github.com/rf20008/TheDiscordMathProblemBotRepo) ",
                successTitle="Here is the Github Repository Link.",
            )
        )
