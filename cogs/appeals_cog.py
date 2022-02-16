from helpful_modules import checks
from helpful_modules.custom_bot import TheDiscordMathProblemBot
import disnake
from disnake.ext import commands
from .helper_cog import HelperCog
from helpful_modules.custom_embeds import SuccessEmbed, ErrorEmbed

class AppealsCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)
        self.bot=bot
        self.cache = bot.cache

    @commands.cooldown(1,30, commands.BucketType.user)
    @commands.slash_command(
        name="appeal",
        description= "Appeal your punishments"
    )
    async def appeal(self, inter: disnake.ApplicationCommandInteraction):
        """/appeal

        Appeal your punishments! It uses a modal.
        There are subcommands!"""
        pass


    @appeal.sub_command(
        name='blacklist',
        description = "Appeal your blacklists"
    )
    async def blacklist(self, inter: disnake.ApplicationCommandInteraction):
        """Appeal your blacklists!"""
        raise NotImplementedError



def setup(bot):
    bot.add_cog()