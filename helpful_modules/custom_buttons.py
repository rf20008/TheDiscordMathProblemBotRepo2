import nextcord
from typing import Any
from .custom_embeds import SuccessEmbed, ErrorEmbed
from .threads_or_useful_funcs import base_on_error
class MyView(nextcord.ui.View):
    async def on_error(self, error: Exception, item: nextcord.ui.Item, inter: nextcord.Interaction):
        return await inter.response.send_message(**base_on_error(inter, error))
class BasicButton(nextcord.ui.Button):
    def __init__(self,check,callback,**kwargs):
        super().__init__(**kwargs)
        self.check = check
        self._callback = callback
        self.user_for = kwargs.pop('user_for').id
    async def callback(self,interaction: nextcord.Interaction) -> Any:
        if self.check(self, interaction):
            return await self._callback(interaction)

class ConfirmationButton(BasicButton):
    "A confirmation button"
    def __init__(self, custom_id, *args, **kwargs):
        "Create a new ConfirmationButton."
        super().__init__(*args,**kwargs)
        self.custom_id = custom_id
        self.author_for = kwargs.pop("author_for")
        self.message_kwargs = kwargs.pop("message_kwargs")
        self._func = kwargs.pop("callback")
        self._extra_data = kwargs.get("_extra_data", {})
    async def callback(self: "ConfirmationButton", interaction: nextcord.Interaction) -> Any:
        def check(inter: nextcord.Interaction):
            return inter.user.id == self.author_for
        responder = self.response
        if not check(interaction):
            embed = ErrorEmbed(description = "You are not allowed to use this menu!", custom_title= "Wrong menu :(")
            responder.send_message(embed = embed, ephemeral = True)
            return None
        #TBD!
        return await self._func(self, interaction, self._extra_data)
        #return await responder.send_message(**self.message_kwargs)
        