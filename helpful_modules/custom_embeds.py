from random import randint

from disnake import Color, Embed

# This is mostly just easier ways for me to use commonly used embeds :)


class SimpleEmbed(Embed):
    def __init__(
        self,
        title="",
        description="",
        color=Color.from_rgb(r=randint(0, 255), g=randint(0, 255), b=randint(0, 255)),
        footer=None,
        file=None,
        url=None,
        timestamp=None
    ):
        super().__init__(title=title, description=description, color=color)
        self.set_footer(text=footer)
        if url is not None and file is not None:
            self.set_image(url)
        if timestamp is not None:
            self.timestamp=timestamp


class ErrorEmbed(SimpleEmbed):
    def __init__(
        self,
        description="",
        color=Color.red(),
        custom_title="Error",
        footer=None,
    ):
        super().__init__(title=custom_title, description=description, color=color)
        self.set_footer(text=footer)


class SuccessEmbed(SimpleEmbed):
    def __init__(
        self,
        description="",
        color=Color.green(),
        successTitle="Success!",
        footer=None,
    ):
        super().__init__(title=successTitle, description=description, color=color)
        self.set_footer(text=footer)
