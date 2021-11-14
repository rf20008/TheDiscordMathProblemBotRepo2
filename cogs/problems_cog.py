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


def setup(bot):
    bot.add_cog(ProblemsCog(bot))


def teardown(bot):
    bot.remove_cog(ProblemsCog)
