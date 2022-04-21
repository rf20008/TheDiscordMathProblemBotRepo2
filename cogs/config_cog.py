import disnake
from .helper_cog import HelperCog
from disnake.ext import commands, tasks
from helpful_modules import checks, problems_module, the_documentation_file_loader
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from disnake import User, Member, Guild, ApplicationCommandInteraction, Permissions
from helpful_modules.problems_module import GuildData, MathProblemCache

TAB_NEWLINE = "\t\n"  # This is because f-strings cannot contain backslashes...


class GuildConfigCog(HelperCog):
    def __init__(self, bot: TheDiscordMathProblemBot):
        self.bot = bot
        self.cache: problems_module.MathProblemCache = bot.cache

    async def user_passes_guild_mod_check(
        self, guild: Guild, author: User | Member
    ) -> bool:
        data: problems_module.GuildData = await self.cache.get_guild_data(
            guild.id, default=problems_module.GuildData.default()
        )
        return data.mod_check.check_for_user_passage(author)

    async def cog_slash_command_check(
        self, inter: disnake.ApplicationCommandInteraction
    ) -> bool:
        """Make sure that only trusted users or guild owners or guild mods can run this command only in guilds!"""
        return (
            inter.guild_id is not None
            and inter.guild is not None  # This is a guild!
            and (
                await self.bot.is_trusted(inter.author)
                or inter.guild.owner_id == inter.author.id
                or await self.user_passes_guild_mod_check(
                    guild=inter.guild, author=inter.author
                )
            )
        )

    @commands.slash_command(description="Change your guild config!")
    async def guild_config(self, inter: disnake.ApplicationCommandInteraction):
        """/guild_config
        Modify your guild's config -- there are subcommands"""
        pass

    @guild_config.sub_command_group(description="Modify your guild's mod check!")
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
    async def add_permission(
        self, inter: ApplicationCommandInteraction, permission: str
    ):
        f"""/guild_config modify_mod_check add_permission [permission: str]
        Add a permission!
        The list of allowed permissions is added below.
        You must type each permission exactly, or the bot will not recongnize the permission.
        Someday, I could add a dropdown menu, but there are too many permissions!
        Permission list: {TAB_NEWLINE.join([permission for permission in Permissions.VALID_FLAGS.keys()])}"""
        if permission not in Permissions.VALID_FLAGS:
            return await inter.send("Invalid permission!")

        data = await self.cache.get_guild_data(
            inter.guild.id, default=GuildData.default()
        )
        data.mod_check.permissions_needed.append(permission)
        await self.cache.set_guild_data(data=data)
        await inter.send("This has been updated!")

    # TODO: Finish everything else!
    @modify_mod_check.sub_command(
        description="Remove a required permission from the mod check"
    )
    async def remove_a_required_permission(
        self, inter: ApplicationCommandInteraction, permission: str
    ):
        """/guild_config remove_a_required_permission [permission: str]
        Remove a required permission from the list of required permissions to meet the mod check!
        Warning: If you remove all required permissions, then ANYBODY can act as a moderator in your server in regards to this bot!"""
        data = await self.cache.get_guild_data(
            inter.guild_id, default=problems_module.GuildData.default(inter.guild_id)
        )
        try:
            data.mod_check.permissions_needed.remove(permission)
        except (ValueError, TypeError) as t:
            await self.cache.set_guild_data(inter.guild_id, data)
            raise
        await inter.send("Successfully completed!")
        return

    @modify_mod_check.sub_command(description="Add a whitelisted user to the mod check")
    async def add_whitelisted_user(
        self, inter: ApplicationCommandInteraction, user: Member
    ):
        """/guild_config modify_mod_check add_whitelisted_user [user: User]
        Add a user to the whitelisted users part of the mod check - this will fail if the user is already whitelisted
        """
        data = await self.cache.get_guild_data(
            inter.guild_id,
            default=problems_module.GuildData.default(guild_id=inter.guild_id),
        )
        if user.id in data.mod_check.whitelisted_users:
            return await inter.send("This user is already whitelisted!")
        data.mod_check.whitelisted_users.append(user.id)
        await self.cache.set_guild_data(inter.guild_id, data)
        await inter.send("You have successfully added a whitelisted user!")
        return

    @modify_mod_check.sub_command(
        description="Remove a whitelisted user from the mod check"
    )
    async def remove_whitelisted_user(
        self, inter: ApplicationCommandInteraction, user: User
    ):
        """/guild_config modify_mod_check remove_whitelisted_user [user: User]
        Remove a whitelisted user from the list of whitelisted users for the mod check. This will work even if the user is not whitelisted"""
        # I have no way of telling whether the user is in the server - because I don't have the members intent
        # This doesn't seem like a valid reason that Discord would give me this intent
        # so I have to work around it
        data = await self.cache.get_guild_data(
            inter.guild_id,
            default=problems_module.GuildData.default(guild_id=inter.guild_id),
        )
        try:
            data.mod_check.whitelisted_users.remove(user.id)
            await self.cache.set_guild_data(inter.guild_id, data=data)
            await inter.send("Data sent!")
            return
        except ValueError:
            await inter.send("This user is not whitelisted")
            raise  # for debugging purposes only

    @modify_mod_check.sub_command(description="add_blacklisted_user")
    async def add_blacklisted_user(
        self, inter: ApplicationCommandInteraction, user: User
    ):
        """/guild_config modify_mod_check add_blacklisted_user [user: User]
        Add a blacklisted user to the mod check, which prevents this user from interacting as a mod with this bot, even if they meet all other requirements"""  # noqa: E401

        data = await self.cache.get_guild_data(
            inter.guild_id,
            default=problems_module.GuildData.default(guild_id=inter.guild_id),
        )
        data.blacklisted_users.append(user.id)
        await self.cache.set_guild_data(inter.guild_id, data=data)
        await inter.send(
            "Successfully added a blacklisted user to the list of blacklisted users..."
        )
    @commands.slash_command(
        description = "Remove a blacklisted user from the list of blacklisted users in the mod check"
    )
    async def remove_blacklisted_user(
        self, inter: ApplicationCommandInteraction, user: User
    ):
        """/guild_config modify_mod_check remove_blacklisted_user [user: User]
        Attempt to remove a blacklisted user from the list of blacklisted users, and don't do anything if the user is not blacklisted"""
        data = await self.cache.get_guild_data(
            inter.guild_id, default=problems_module.GuildData.default()
        )
        try:
            data.mod_check.blacklisted_users.remove(user.id)
            await self.cache.set_guild_data(inter.guild_id, data=data)
            await inter.send("Successfully removed the user's blacklistness")
            return
        except ValueError:
            await inter.send("The user is not blacklisted, so I cannot unblacklist the user from the mod check.")
            raise # for debugging purposes

def setup(bot: TheDiscordMathProblemBot):
    bot.add_cog(GuildConfigCog(bot))

