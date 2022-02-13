import asyncio
import contextlib
import copy
import io
import textwrap
from traceback import format_exception

import disnake
from disnake.ext import commands

from helpful_modules import checks, problems_module
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules.custom_embeds import ErrorEmbed, SimpleEmbed, SuccessEmbed
from helpful_modules.threads_or_useful_funcs import get_log
from helpful_modules.my_modals import MyModal

from .helper_cog import HelperCog
from os import urandom
log = get_log(__name__)


class DebugCog(HelperCog):
    """Commands for debugging :-)"""

    def __init__(self, bot: TheDiscordMathProblemBot):
        super().__init__(bot)

    async def eval_code(self, inter, code: str):
        thing_to_run = """async def func(): 
                """  # maybe: just exec() directly
        thing_to_run += textwrap.indent(code_, "    ", predicate=lambda l: True)
        compiled = False
        new_globals = {
            "bot": self.bot,
            "cache": self.cache,
            "self": self,
            "inter": inter,
            "author": inter.author,
        }
        new_globals.update(
            globals()
        )  # credit: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L234
        try:
            exec(thing_to_run, new_globals, locals())
            compiled = True
        except BaseException as e:
            compiled = False
            new_stderr.write("".join(format_exception(e)))
        if (
                "func" not in globals().keys()
                and "func" not in locals().keys()
                and compiled is True
        ):
            raise RuntimeError("func is not defined")
        err = None
        if compiled:
            try:
                with contextlib.redirect_stdout(new_stdout):
                    with contextlib.redirect_stderr(new_stderr):
                        if "func" in globals().keys():
                            print(
                                await globals()["func"](), file=new_stdout
                            )  # Get the 'func' from the global variables and call it
                            log.info("/eval ran (found in globals)")
                        elif "func" in locals().keys():

                            print(await (locals()["func"]()), file=new_stdout)  # Get func() from locals and call it
                            log.info("/eval ran (found in locals)")
                        else:
                            raise Exception(f"""fatal: func() not defined""")
            except BaseException as e:
                new_stderr.write("".join(format_exception(e)))
                err = None
        await inter.send(
            embed=SuccessEmbed(
                f"""The code was successfully executed!
        stdout: ```{new_stdout.getvalue()} ```
        stderr: ```{new_stderr.getvalue()} ```"""
            )
        )
        new_stdout.close()
        new_stderr.close()
        if err is not None:
            raise err
        else:
            return

    def cog_slash_command_check(self, inter: disnake.ApplicationCommandInteraction):
        """A check that makes sure only bot owners can use this cog!"""
        if self.bot.owner_id in [None, [], set()] and self.bot.owner_ids is None:
            raise commands.CheckFailure(
                "Warning: neither owner_id or owner_ids is defined..."
            )
        if self.bot.owner_id in [None, [], set()]:
            raise commands.CheckFailure(
                "You're not the owner of this bot! You must be the owner to execute debug commands!"
            )
        if self.bot.owner_id == inter.author.id:
            return True

        try:
            if (
                self.bot.owner_ids not in [None, [], set()]
                and inter.author.id in self.bot.owner_ids
            ):
                return True
            raise commands.CheckFailure("You don't own this bot!")
        except AttributeError:
            raise commands.CheckFailure("You don't own this bot!")

    @checks.has_privileges(trusted=True)
    @commands.is_owner()
    @checks.trusted_users_only()
    @commands.slash_command(
        name="sql",
        description="Run SQL",
        options=[
            disnake.Option(
                name="Query",
                description="The query to run",
                type=disnake.OptionType.string,
                required=True,
            )
        ],
    )
    async def sql(self, inter: disnake.ApplicationCommandInteraction, query: str):
        """/sql [query: str]
        A debug command to run SQL!
        You must own this bot to run this command!"""
        if (
            self.bot.owner_ids not in [None, [], set()]
            and inter.author.id not in self.bot.owner_ids
        ):
            await inter.send("You don't own this bot...")
            return
        if self.bot.owner_id is not None and inter.author.id != self.bot.owner_id:
            await inter.send("You don't own this bot!!!")
            return
        if self.bot.owner_id is None and self.bot.owner_ids is None:
            return await inter.send(
                "Neither owner_id or owner_ids is defined... exiting!"
            )
        try:
            result = await self.cache.run_sql(query)
        except BaseException as e:
            await inter.send("An exception occurred while running the SQL!")
            raise

        await inter.send(f"Result: {result}")
        return

    @checks.has_privileges(blacklisted=False)
    @commands.is_owner()
    @checks.trusted_users_only()
    @commands.slash_command(
        name="eval",
        description="Execute arbitrary python code (only owners can do this)",
        options=[
            disnake.Option(
                name="code",
                description="The code to execute",
                type=disnake.OptionType.string,
                required=True,
            )
        ],
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

        if (
            self.bot.owner_ids not in [None, [], set()]
            and inter.author.id not in self.bot.owner_ids
        ):
            await inter.send("You don't own this bot...")
            return
        if self.bot.owner_id is not None and inter.author.id != self.bot.owner_id:
            await inter.send("You don't own this bot!!!")
            return
        if self.bot.owner_id is None and self.bot.owner_ids is None:
            return await inter.send(
                "Neither owner_id or owner_ids is defined... exiting!"
            )

        if inter.guild is None:
            pass
        elif not (
            inter.author.guild_permissions().administrator
            and inter.guild.me.guild_permissions().administrator
        ):
            return await inter.send(
                "We must both have the administrator permission to /eval!"
            )
        code_ = "\n".join(code.split("\\n"))  # Split the code by `\n`
        await self.eval_code(inter, code)

    @commands.is_owner()
    @checks.has_privileges(trusted=True,)
    @commands.slash_command(
        name='eval2',
        description = "Evaluate Python code (for owners only)- this uses a modal"
    )
    async def eval2(self, inter):
        """/eval2

        R"""
        if not await self.bot.is_owner(inter.author):
            raise commands.NotOwner("You must be the owner to use /eval2")

        if not await self.bot.is_trusted(inter.author):
            raise RuntimeError("You must be trusted to use /eval2")

        the_custom_id = urandom(20).hex()
        text_inputs = [
            disnake.ui.TextInput(
                label = "What code do you want to run?",
                custom_id = the_custom_id,
                style=disnake.TextInputStyle.paragraph,
                required=True,
                max_length=5000

            )
        ]
        code_to_run = ""
        async def callback(s, modal_inter: disnake.ModalInteraction):
            if modal_inter.author.id != inter.author.id:
                raise RuntimeError
            nonlocal code_to_run
            code_to_run = modal_inter.text_inputs[the_custom_id]
            await modal_inter.send("Thanks for providing the code to run :-)")



        modal_custom_id = urandom(20).hex()
        modal: MyModal = MyModal(timeout=180,title="What code do you want to run?", custom_id=modal_custom_id, callback=callback, inter=inter)
        modal.append_component(text_inputs)
        await inter.response.send_modal(modal)
        modal_inter = await self.bot.wait_for('modal_submit', check=lambda modal_inter: modal_inter.custom_id == modal_custom_id)

        await self.eval_code(inter, code_to_run)

def setup(bot: TheDiscordMathProblemBot):
    bot.add_cog(DebugCog(bot))

def teardown(bot: TheDiscordMathProblemBot):
    bot.remove_cog("DebugCog")
