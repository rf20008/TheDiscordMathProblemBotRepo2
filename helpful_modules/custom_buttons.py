import nextcord
from typing import Any, List
from .custom_embeds import SuccessEmbed, ErrorEmbed
from .threads_or_useful_funcs import base_on_error
from copy import deepcopy


class MyView(nextcord.ui.View):
    "A better? view for my bot (which is easier for my bot to work with)"

    async def __init__(
        self,
        message: nextcord.Message = None,
        *,
        timeout: int = 180.0,
        items: List[nextcord.ui.Item]
    ):
        super().__init__(timeout)
        self.message = message
        assert len(items) <= 25  # Discord limitation
        for item in items:
            assert isinstance(item, nextcord.ui.Item)
            self.add_item(item)

    async def on_error(
        self, error: Exception, item: nextcord.ui.Item, inter: nextcord.Interaction
    ):
        return await inter.response.send_message(**base_on_error(inter, error))

    async def reply(Interaction: nextcord.Interaction, *args, **kwargs):
        "Reply to an interaction"
        return await Interaction.response.send_message(*args, **kwargs)

    async def stop_all_items(self):
        "Stop all items. However, this does not work, because the bot will not know the message before it's sent"
        newView = self.__class__(
            self.message
        )  # Create a new view that has the same message
        for item in self.children:
            if item.__class__ == nextcord.ui.Item:
                # It's a base item
                raise RuntimeError("Cannot stop base item")
            new_item_dict = item.__dict__
            new_item_dict["disabled"] = True  # Disable the button by editing __dict__
            newItem = item.__class__(**new_item_dict)  # Create a new item
            newView.add_item(newItem)  # Add it to the new view

        await self.message.edit(
            content=self.message.content,
            embeds=self.message.embeds,
            attachments=self.message.attachments,
            view=newView,
        )


class BasicButton(nextcord.ui.Button):
    def __init__(self, check, callback, **kwargs):
        super().__init__(**kwargs)
        self.check = check
        self._callback = callback
        self.user_for = kwargs.pop("user_for").id

    async def callback(self, interaction: nextcord.Interaction) -> Any:
        if self.check(self, interaction):
            return await self._callback(interaction)

    def disable(self):
        "Disable myself. If this does not work, this is probably a Discord limitation. However, I don't know."
        self.disabled = True

    def enable(self):
        "Enable myself. If this does not work, this is probably a Discord limitation. However, I don't know."
        self.disabled = False


class ConfirmationButton(BasicButton):
    "A confirmation button"

    def __init__(self, custom_id="1", *args, **kwargs):
        "Create a new ConfirmationButton."
        super().__init__(*args, **kwargs)
        self.custom_id = custom_id
        self.author_for = kwargs.pop("author_for")
        self.message_kwargs = kwargs.pop("message_kwargs")
        self._func = kwargs.pop("callback")
        self._extra_data = kwargs.get("_extra_data", {})

    async def callback(
        self: "ConfirmationButton", interaction: nextcord.Interaction
    ) -> Any:
        def check(inter: nextcord.Interaction):
            return inter.user.id == self.author_for

        responder = self.response
        if not check(interaction):
            embed = ErrorEmbed(
                description="You are not allowed to use this menu!",
                custom_title="Wrong menu :(",
            )
            responder.send_message(embed=embed, ephemeral=True)
            return None
        # TBD!
        return await self._func(self, interaction, self._extra_data)
        # return await responder.send_message(**self.message_kwargs)