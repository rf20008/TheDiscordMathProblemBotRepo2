from disnake import Embed, Color
from random import randint


class SimpleEmbed(Embed):
    def __init__(
        self,
        title="",
        description="",
        color=Color.from_rgb(r=randint(0, 255), g=randint(0, 255), b=randint(0, 255)),
        footer=Embed.Empty,
    ):
        super().__init__(title=title, description=description, color=color)
        self.set_footer(text=footer)


class ErrorEmbed(SimpleEmbed):
    def __init__(
        self,
        description="",
        color=Color.from_rgb(r=240, g=0, b=0),
        custom_title="Error",
        footer=Embed.Empty,
    ):
        super().__init__(title=custom_title, description=description, color=color)
        self.set_footer(text=footer)


class SuccessEmbed(SimpleEmbed):
    def __init__(
        self,
        description="",
        color=Color.from_rgb(r=0, g=256, b=0),
        successTitle="Success!",
        footer=Embed.Empty,
    ):
        super().__init__(title=successTitle, description=description, color=color)
        self.set_footer(text=footer)
