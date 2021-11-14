from .helper_cog import HelperCog
from helpful_modules.problems_module import *
from helpful_modules.custom_embeds import *
import dislash, nextcord
from dislash import InteractionClient, Option, OptionType, NotOwner, OptionChoice
from helpful_modules import checks, cooldowns
class ProblemsCog(HelperCog):
    def __init__(self, bot):
        "Helpful __init__, the entire reason I decided to make this so I could transfer modules"        
        self.bot = bot
        super().__init__(bot)
    @checks.is_not_blacklisted
    @slash_command(
        name="edit_problem",
        description="edit a problem",
        options=[
            Option(
                name="problem_id",
                description="problem_id",
                type=OptionType.INTEGER,
                required=True,
            ),
            Option(name="guild_id", description="the guild id", type=OptionType.INTEGER),
            Option(
                name="new_question",
                description="the new question",
                type=OptionType.STRING,
                required=False,
            ),
            Option(
                name="new_answer",
                description="the new answer",
                type=OptionType.STRING,
                required=False,
            ),
        ],
    )
    async def edit_problem(
        self, inter, problem_id, new_question=None, new_answer=None, guild_id="null"
    ):
        "Allows you to edit a math problem."
        await cooldowns.check_for_cooldown(inter, "edit_problem", 0.5)
        try:
            problem = await self.cache.get_problem(int(guild_id), int(problem_id))
            if not problem.is_author(inter.author):
                await inter.reply(
                    embed=ErrorEmbed(
                        "You are not the author of this problem and therefore can't edit it!"
                    )
                )
                return
        except KeyError:
            await inter.reply(embed=ErrorEmbed("This problem does not exist."))
            return
        e = "Successfully"
        if new_question != None:
            if new_answer != None:
                await problem.edit(question=new_question, answer=new_answer)
                e += f"changed the answer to {new_answer} and question to {new_question}!"
            else:
                await problem.edit(question=new_question)
                e += f"changed the question to {new_question}!"
        else:
            if new_answer is not None:
                await problem.edit(answer=new_answer)
                e += f"changed the answer to {new_answer}"
            else:
                raise Exception(
                    "*** No new answer or new question provided. Aborting command...***"
                )

        await inter.reply(embed=SuccessEmbed(e), ephemeral=True)
    @slash_command(
        name="show_problem_info",
        description="Show problem info",
        options=[
            Option(
                name="problem_id",
                description="problem id of the problem you want to show",
                type=OptionType.INTEGER,
                required=True,
            ),
            Option(
                name="show_all_data",
                description="whether to show all data (only useable by problem authors and trusted users",
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name="raw",
                description="whether to show data as json?",
                type=OptionType.BOOLEAN,
                required=False,
            ),
            Option(
                name="is_guild_problem",
                description="whether the problem you are trying to view is a guild problem",
                type=OptionType.BOOLEAN,
                required=False,
            ),
        ],
    )
    async def show_problem_info(
        self, inter, problem_id, show_all_data=False, raw=False, is_guild_problem=False
    ):
        "Show the info of a problem."
        await cooldowns.check_for_cooldown(inter, "edit_problem", 0.5)
        problem_id = int(problem_id)
        try:
            guild_id = inter.guild.id
        except AttributeError as exc:
            raise Exception(
                "*** AttributeError: guild.id was not found! Please report this error or refrain from using it here***"
            ) from exc

        real_guild_id = str(inter.guild.id) if is_guild_problem else "null"
        problem = await self.cache.get_problem(real_guild_id, str(problem_id))

        if True:
            if is_guild_problem and guild_id is None:
                embed1 = ErrorEmbed(
                    description="Run this command in the discord server which has this problem, not a DM!"
                )
                inter.reply(embed=embed1)
                return
            problem = await self.cache.get_problem(
                str(inter.guild.id) if is_guild_problem else "null", str(problem_id)
            )
            Problem__ = f"Question: {problem.get_question()}\nAuthor: {str(problem.get_author())}\nNumVoters/Vote Threshold: {problem.get_num_voters()}/{self.bot.vote_threshold}\nNumSolvers: {len(problem.get_solvers())}"

            if show_all_data:
                if not (
                    (
                        problem.is_author(inter.author)
                        or inter.author.id not in self.bot.trusted_users
                        or (
                            is_guild_problem
                            and inter.author.guild_permissions.administrator == True
                        )
                    )
                ):  # Check for sufficient permissions
                    await inter.reply(
                        embed=ErrorEmbed("Insufficient permissions!"), ephemeral=True
                    )
                    return
                Problem__ += f"\nAnswer: {problem.get_answer}"

            if raw:
                await inter.reply(
                    embed=SuccessEmbed(str(problem.convert_to_dict())), ephemeral=True
                )
                return
            await inter.reply(embed=SuccessEmbed(Problem__), ephemeral=True)
    @slash_command(
        name="list_all_problem_ids",
        description="List all problem ids",
        options=[
            Option(
                name="show_only_guild_problems",
                description="Whether to show guild problem ids",
                required=False,
                type=OptionType.BOOLEAN,
            )
        ],
    )
    async def list_all_problem_ids(self,inter, show_only_guild_problems=False):
        "Lists all problem ids."
        await cooldowns.check_for_cooldown(inter, "list_all_problem_ids", 2.5)
        if show_only_guild_problems:
            guild_id = inter.guild.id
            if guild_id is None:
                await inter.reply(
                    "Run this command in a Discord server or set show_only_guild_problems to False!",
                    ephemeral=True,
                )
                return
            if show_only_guild_problems:
                guild_problems = await self.cache.get_guild_problems(inter.guild)
            else:
                guild_problems = await self.cache.get_global_problems()
            thing_to_write = [str(problem) for problem in guild_problems]
            await inter.reply(
                embed=SuccessEmbed(
                    "\n".join(thing_to_write)[:1950], successTitle="Problem IDs:"
                )
            )
            return

        global_problems = self.cache.get_global_problems()
        thing_to_write = "\n".join([str(problem.id) for problem in global_problems])
        await inter.send(embed=SuccessEmbed(thing_to_write))

def setup(bot):
    bot.add_cog(ProblemsCog(bot))


def teardown(bot):
    bot.remove_cog(ProblemsCog)
