from nextcord import Embed, Color
from random import randint
class SimpleEmbed(Embed):
  def __init__(self, title="",description="",color=Color.random(seed=randint(1,200000))):
    super().__init__(title=title,description=description,color=color)
class ErrorEmbed(SimpleEmbed):
  def __init__(self,description="",color=Color.red(),custom_title="Error"):
    super().__init__(title=custom_title,description=description, color=color)
class SuccessEmbed(SimpleEmbed):
  def __init__(self,description="",color=Color.green(),successTitle="Success!"):
    super().__init__(title=successTitle,description=description,color=color)
