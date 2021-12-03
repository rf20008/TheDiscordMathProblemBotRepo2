import nextcord
from typing import Any
from .custom_embeds import SuccessEmbed, ErrorEmbed
class BasicButton(nextcord.ui.Button):
    def __init__(self,check,callback,**kwargs):
        super().__init__(**kwargs)
        self.check = check
        self._callback = callback
    async def callback(self,interaction: nextcord.Interaction) -> Any:
        if self.check(interaction):
            return await self._callback(interaction)

class ConfirmationButton(nextcord.ui.Button):
    "A confirmation button"
    def __init__(self, custom_id, **kwargs):
        super().__init__(**kwargs)
        self.custom_id = custom_id
        self.author_for = kwargs.pop("author_for")
        self.message_kwargs = kwargs.pop("message_kwargs")

    async def callback(self: "ConfirmationButton", interaction: nextcord.Interaction) -> Any:
        def check(inter: nextcord.Interaction):
            return inter.user.id == self.author_for
        responder = self.response
        if not check(interaction):
            embed = ErrorEmbed(description = "You are not allowed to use this menu!", custom_title= "Wrong menu :(")
            responder.send_message(embed = embed, ephemeral = True)
            return None
        #TBD!
        return await responder.send_message(**self.message_kwargs)
        