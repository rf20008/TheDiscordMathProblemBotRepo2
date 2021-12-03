import nextcord
from .custom_embeds import SuccessEmbed, ErrorEmbed
class ConfirmationButton(nextcord.ui.Button):
    "A confirmation button"
    def __init__(self, custom_id, **kwargs):
        super().__init__(**kwargs)
        self.custom_id = custom_id
        self.author_for = kwargs.pop("author_for")
    

    async def callback(self: "ConfirmationButton", interaction: nextcord.Interaction) -> None:
        def check(inter: nextcord.Interaction):
            return inter.user.id == self.author_for
        responder = self.response
        if not check(interaction):
            embed = ErrorEmbed(description = "You are not allowed to use this menu!", custom_title= "Wrong menu :(")
            responder.send_message(embed = embed, ephemeral = True)
            return None
        #TBD!
        responder.reply()
        