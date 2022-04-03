import disnake
from .helper_cog import HelperCog
from disnake.ext import commands, tasks
from helpful_modules import checks, problems_module, the_documentation_file_loader
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from disnake import (
    User,
    Member,
    Guild,
    ApplicationCommandInteraction,
    Permissions
)
from helpful_modules.problems_module import (
    GuildData,
    MathProblemCache
)

class GuildConfigCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        self.bot=bot
        self.cache: problems_module.MathProblemCache =bot.cache
    async def user_passes_guild_mod_check(self, guild: Guild, author: User | Member) -> bool:
        data: problems_module.GuildData = await self.cache.get_guild_data(guild.id, default=problems_module.GuildData.default())
        return data.mod_check.check_for_user_passage(author)

    async def cog_slash_command_check(self, inter: disnake.ApplicationCommandInteraction) -> bool:
        """Make sure that only trusted users or guild owners or guild mods can run this command only in guilds!"""
        return (
            inter.guild_id is not None
            and inter.guild is not None # This is a guild!
            and (
                await self.bot.is_trusted(inter.author)
                or inter.guild.owner_id == inter.author.id
                or await self.user_passes_guild_mod_check(guild=inter.guild, author=inter.author)
            )
        )

    @commands.slash_command(
        description="Change your guild config!"
    )
    async def guild_config(self, inter: disnake.ApplicationCommandInteraction):
        """/guild_config
        Modify your guild's config -- there are subcommands"""
        pass

    @guild_config.sub_command_group(
        description="Modify your guild's mod check!"
    )
    async def modify_mod_check(self, inter: ApplicationCommandInteraction):
        """/guild_config modify_mod_check
        Usage:
            /guild_config_modify_mod_check add_permission [permission: str]
            -- Add a permission. This permission must be a valid permission and match up exactly with Disnake's permission names.
            /guild_config modify_mod-check remove_permission [permission: str]
            Remove a permission needed from the list of permissions needed. WARNING: If you remove all the permissions needed (for moderatorship), then ANYONE in your server can run commands as a mod in the bot!


            """
        pass
    @modify_mod_check.sub_command(
        description="Add a permission to the list of required permissions to be a mod!. This must match up exactly with Disnake's permission names!"
    )
    async def add_permission(self, inter: ApplicationCommandInteraction, permission: str):
        f"""/guild_config modify_mod_check add_permission [permission: str]
        Add a permission!
        The list of allowed permissions is added below.
        You must type each permission exactly, or the bot will not recongnize the permission. 
        omeday, I could add a dropdown menu, but there are too many permissions!
        Permission list: {'\t\n'.join([permission for permission in Permissions.VALID_FLAGS.keys()])}"""
        if permission not in Permissions.VALID_FLAGS:
            return await inter.send("Invalid permission!")

        data = await self.cache.get_guild_data(inter.guild.id,default=GuildData.default())
        data.mod_check.permissions_needed.append(permission)
        await self.cache.set_guild_data(data=data)
        await inter.send("This has been updated!")


    # TODO: Finish everything else!
