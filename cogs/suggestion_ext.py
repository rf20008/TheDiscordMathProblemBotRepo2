"""
The Discord Math Problem Bot
Copyright (C) August 2022 <No organization yet>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses>"""

import disnake
from typing import *
from disnake.ext import commands, tasks
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from helpful_modules import checks, custom_embeds
from .helper_cog import HelperCog
import random
SUGGESTIONS_AND_FEEDBACK_CHANNEL_ID = 883908866541256805

class ConfirmView(disnake.ui.View):
    def __init__(self, *, user_id: int, timeout: float, bot: TheDiscordMathProblemBot, suggestion: str):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.bot=bot
        self.suggestion=suggestion

    async def interaction_check(self, inter: disnake.Interaction):
        return self.user_id == inter.author.id and not await self.bot.is_blacklisted(inter.author.id)

    @disnake.ui.button(label="CONFIRM", disabled=False, style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):

        # assume the interaction check has passed, Disnake calls the interaction check before the function is called
        channel =await self.bot.get_or_fetch_channel(SUGGESTIONS_AND_FEEDBACK_CHANNEL_ID)
        await channel.send(
            disnake.Embed(
                title = (inter.author.name + "#" + inter.author.discriminator),
                description=suggestion,
                color = random.randint(0x000000, 0xffffff),
                timestamp=disnake.utils.utcnow()
            )
        )
        await inter.edit_original_message(content="Successful. This view is now closed.", embeds=[], view=None)

    @disnake.ui.button(label="DENY", disabled=False, style=disnake.ButtonStyle.red)
    async def deny(self, _: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.edit_original_message(content="Okay. I guess you don't want to make the suggestion.", embeds=[], view=None)



class SuggestionCog(HelperCog):
    """This category is for suggestions"""
    def __init__(self, bot: TheDiscordMathProblemBot):
        self.bot=bot
        self.cache=bot.cache
        self.suggestions_and_feedback_channel=None
        self.is_ready=False

    async def cog_load(self):
        await self.bot.wait_until_ready() # Make sure we have a connection before we continue
        self.suggestions_and_feedback_channel = await self.bot.fetch_channel(SUGGESTIONS_AND_FEEDBACK_CHANNEL_ID)
        self.is_ready=True

    @checks.is_not_blacklisted()
    @commands.slash_command(description="Make a suggestion")
    async def suggest(self, inter: disnake.ApplicationCommandInteraction, suggestion: str) -> Optional[disnake.Message]:
        """/suggest [suggestion: str]
        Make a suggestion. The suggestion must be shorter than 5451 characters (due to character limitations)."""
        if len(suggestion) > 5450:
            return await inter.send("Your suggestion is too long.")
        if not self.is_ready:
            return await inter.send("I am not ready to recieve suggestions!")

        await inter.send(
            embed=SimpleEmbed(
                title="Are you sure you want to make this?",
                description = (
                    "This suggestion will be sent to the official support server. "+
                    "You may be BLACKLISTED for making rule-breaking suggestions. "+
                    "Do you want do this anyway?"+
                    "You have 3 minutes to respond."
                )
            ),
            view=ConfirmView(
                user_id=inter.author.id,
                timeout=180.0,
                bot=self.bot,
                suggestion=suggestion

            )
        )






