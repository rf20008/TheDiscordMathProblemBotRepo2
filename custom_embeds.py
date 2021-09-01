from nextcord import Embed, Color
from random import randint
class Embedv2(Embed):
  def __init__(self, title,description,color=Color.random(seed=randint(1,200000)):
    super().__init__(title=title,description=description,color=color)
class ErrorEmbed(Embedv2):
  def __init__(self,description,color=Color.red()):
    super().__init__(title="Error",description=description, color=color)
class SuccessEmbed(Embedv2):
  def __init__(self,description,color=Color.green(),successTitle="Success!"):
    super().__init___(title=successTitle,description=description,color=color)
