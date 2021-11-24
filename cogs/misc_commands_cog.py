from dislash import *
import nextcord
from .helper_cog import HelperCog
from sys import version_info, version
from helpful_modules import checks, cooldowns
from helpful_modules.custom_embeds import *
from helpful_modules.threads_or_useful_funcs import get_git_revision_hash
from asyncio import sleep as asyncio_sleep
import resource


class MiscCommandsCog(HelperCog):
    def __init__(self, bot):
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
        embed = custom_embeds.SimpleEmbed(title="Bot info", description="")
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
            max_cpu = resource.RLIMIT_CPU
            current_usage = resource.getrusage(resource.RUSAGE_SELF)

            embed = embed.add_field(
                name="Memory Usage",
                value=f"{round((current_usage[3]/memory_limit)*1000)/100}%",
            )

        await inter.reply(embed=embed)

    @slash_command(name="list_trusted_users", description="list all trusted users")
    async def list_trusted_users(self, inter):
        "List all trusted users with username/discriminator"
        await inter.reply(type=5)  # Defer
        # We might not be able to respond in time because of the 100ms delay between user fetching
        # This is to respect the API rate limit.
        if len(self.bot.trusted_users) == 0:
            await inter.reply("There are no trusted users.")
            
            raise Exception("There are no trusted users!")
            
        __trusted_users = ""

        for user_id in self.bot.trusted_users:
            user = await self.bot.fetch_user(user_id=user_id)
            __trusted_users += f"""{user.name}#{user.discriminator}
            """
            await asyncio_sleep(
                0.1
            )  # 100 ms between fetching to respect the rate limit (and to prevent spam)

        await inter.reply(__trusted_users, ephemeral=True)
    @slash_command(name="ping", description="Prints latency and takes no arguments")
    async def ping(inter):
        "Ping the bot which returns its latency!"
        await check_for_cooldown(inter, "ping", 5)
        await inter.reply(
            embed=SuccessEmbed(f"Pong! My latency is {round(bot.latency*1000)}ms."),
            ephemeral=True,
        )


    @slash_command(
        name="what_is_vote_threshold",
        description="Prints the vote threshold and takes no arguments",
    )
    async def what_is_vote_threshold(inter):
        "Returns the vote threshold"
        await check_for_cooldown(inter, "what_is_vote_threshold", 5)
        await inter.reply(
            embed=SuccessEmbed(f"The vote threshold is {vote_threshold}."), ephemeral=True
        )


    @slash_command(
        name="generate_invite_link",
        description="Generates a invite link for this bot! Takes no arguments",
    )
    async def generate_invite_link(inter):
        "Generate an invite link for the bot."
        await check_for_cooldown(inter, "generateInviteLink", 5)
        await inter.reply(
            embed=SuccessEmbed(
                "https://discord.com/api/oauth2/authorize?client_id=845751152901750824&permissions=2147552256&scope=bot%20applications.commands"
            ),
            ephemeral=True,
        )


    @slash_command(
        name="github_repo", description="Returns the link to the github repo"
    )
    async def github_repo(inter):
        await check_for_cooldown(inter, "github_repo", 5)
        await inter.reply(
            embed=SuccessEmbed(
                "[Repo Link:](https://github.com/rf20008/TheDiscordMathProblemBotRepo) ",
                successTitle="Here is the Github Repository Link.",
            )
        )
