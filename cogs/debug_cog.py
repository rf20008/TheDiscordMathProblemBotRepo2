import contextlib
import disnake
import io
import textwrap
from traceback import format_exception
from disnake.ext import commands
from helpful_modules import checks, problems_module
from helpful_modules.custom_bot import TheDiscordMathProblemBot

from .helper_cog import HelperCog


class DebugCog(HelperCog):
    """Commands for debugging :-)"""

    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)

    def cog_slash_command_check(self, inter: disnake.ApplicationCommandInteration):
        """A check that makes sure only bot owners can use this cog!"""
        if self.bot.owner_id in [None, []]:
            raise commands.CheckFailure(
                "You're not the owner of this bot! You must be the owner to execute debug commands!")
        if self.bot.owner_id == inter.author.id:
            return True

        try:
            if self.bot.owner_ids not in [None, []] and inter.author.id in self.bot.owner_ids:
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
    async def sql(self, inter: disnake.ApplicationCommandInteration, query: str):
        """/sql [query: str]
        A debug command to run SQL!
        You must own this bot to run this command!"""
        pass

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
    async def eval(self, inter, code: str, stdin: str = ''):
        """/eval [code: str]
        Evaluate arbitrary python code.
        Any instances of `\n` in code and stdin will be replaced with a newline character!
        This will happen even in strings. Therefore, be very careful!
        Only the owner can run this command!
        """
        new_stdout = io.StringIO()
        new_stderr = io.StringIO()
        if inter.author.id not in self.bot.owner_ids or inter.author.id != self.bot.owner_id:
            await inter.send("You don't own this bot.")
            return
        code_ = '\n'.join(code.split('\\n')) #Split the code by `\n`
        thing_to_run = '''async def func():
        '''
        thing_to_run += textwrap.indent(code_, '\t', predicate = lambda l: True)
        try:
            exec(thing_to_run, globals = globals(), locals = locals())
        except SyntaxError as e:
            new_stderr.write(format_exception(e))

        try:
            with contextlib.redirect_stdout(new_stdout):
                with contextlib.redirect_stderr(new_stderr)
                    exec('func()')
        except BaseException as e:
            new_stderr.write(format_exception(e))
        await inter.reply(embed = SuccessEmbed(
            f"""The code was successfully executed!
stdin: ```{stdin}```
stdout: ```{new_stdout.getvalue()}```
stderr: ```{new_stderr.getvalue()}```}"""
        ))
        new_stdout.close()
        new_stderr.close()
        return


