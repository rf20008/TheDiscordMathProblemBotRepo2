import asyncio
import contextlib
import copy
import disnake
import io
import textwrap
from traceback import format_exception
from disnake.ext import commands
from helpful_modules import checks, problems_module
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules.custom_embeds import SuccessEmbed, ErrorEmbed, SimpleEmbed
from .helper_cog import HelperCog


class DebugCog(HelperCog):
    """Commands for debugging :-)"""

    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)

    def cog_slash_command_check(self, inter: disnake.ApplicationCommandInteraction):
        """A check that makes sure only bot owners can use this cog!"""
        if self.bot.owner_id in [None, [], set()] and self.bot.owner_ids is None:
            raise commands.CheckFailure("Failing to protect myself (neither owner_id nor owner_ids are defined)")
        if self.bot.owner_id in [None, [], set()]:
            raise commands.CheckFailure(
                "You're not the owner of this bot! You must be the owner to execute debug commands!")
        if self.bot.owner_id == inter.author.id:
            return True

        try:
            if self.bot.owner_ids not in [None, [],set()] and inter.author.id in self.bot.owner_ids:
                return True
            raise commands.CheckFailure("You don't own this bot!")
        except AttributeError:
            raise commands.CheckFailure("You don't own this bot!")

    @commands.is_owner()
    @checks.trusted_users_only()
    @commands.slash_command(
        name='sql',
        description="Run SQL",
        options=[
            disnake.Option(
                name='Query',
                description="The query to run",
                type=disnake.OptionType.string,
                required=True,
            )
        ]
    )
    async def sql(self, inter: disnake.ApplicationCommandInteraction, query: str):
        """/sql [query: str]
        A debug command to run SQL!
        You must own this bot to run this command!"""
        if (self.bot.owner_ids not in [None, [], set()] and inter.author.id not in self.bot.owner_ids):
            await inter.send("You don't own this bot...")
            return
        if self.bot.owner_id is not None and inter.author.id != self.bot.owner_id:
            await inter.send("You don't own this bot!!!")
            return
        if self.bot.owner_id is None and self.bot.owner_ids is None:
            return await inter.send("Neither owner_id or owner_ids is defined... exiting!")
        try:
            result = await self.cache.run_sql(query)
        except BaseException as e:
            await inter.send("An exception occurred while running the SQL!")
            raise

        await inter.send(f"Result: {result}")
        return


    @commands.is_owner()
    @checks.trusted_users_only()
    @commands.slash_command(
        name='eval',
        description="Execute arbitrary python code (only owners can do this)",
        options=[
            disnake.Option(
                name='code',
                description='The code to execute',
                type=disnake.OptionType.string,
                required=True
            )
        ]
    )
    async def eval(self, inter: disnake.ApplicationCommandInteraction, code: str):
        """/eval [code: str]
        Evaluate arbitrary python code.
        Any instances of `\n` in code and stdin will be replaced with a newline character!
        This will happen even in strings. Therefore, be very careful!
        Only the owner can run this command!
        This requires both the owner and the bot to have the Administrator permission.
        """
        new_stdout = io.StringIO()
        new_stderr = io.StringIO()
        
        if (self.bot.owner_ids not in [None, [], set()] and inter.author.id not in self.bot.owner_ids):
            await inter.send("You don't own this bot...")
            return
        if self.bot.owner_id is not None and inter.author.id != self.bot.owner_id:
            await inter.send("You don't own this bot!!!")
            return
        if self.bot.owner_id is None and self.bot.owner_ids is None:
            return await inter.send("Neither owner_id or owner_ids is defined... exiting!")

        if inter.guild is None:
            pass
        elif not (inter.author.guild_permissions().administrator and inter.guild.me.guild_permissions().administrator):
            return await inter.send("We must both have the administrator permission to /eval!")
        code_ = '\n'.join(code.split('\\n')) #Split the code by `\n`
        thing_to_run = '''async def _func():
        '''
        thing_to_run += textwrap.indent(code_, '    ', predicate = lambda l: True)
        compiled = False
        new_globals = {
            'bot': self.bot,
            'cache': self.cache,
            'self': self,
            'inter': inter,
            'author': inter.author
        }
        new_globals.update(globals()) # credit: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L234
        try:
            exec(thing_to_run, new_globals, locals())
            compiled = True
        except BaseException as e:
            compiled = False
            new_stderr.write(''.join(format_exception(e)))
        if compiled:
            try:
                _func
            except NameError:
                raise RuntimeError("Uh oh")
        if compiled:
            try:
                with contextlib.redirect_stdout(new_stdout):
                    with contextlib.redirect_stderr(new_stderr):
                        await _func()
            except BaseException as e:
                new_stderr.write(''.join(format_exception(e)))
        await inter.send(embed = SuccessEmbed(
            f"""The code was successfully executed!
stdout: ```{new_stdout.getvalue()} ```
stderr: ```{new_stderr.getvalue()} ```"""
        ))
        new_stdout.close()
        new_stderr.close()
        return


