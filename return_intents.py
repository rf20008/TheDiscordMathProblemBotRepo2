from nextcord import Intents
def return_intents():
  i = Intents.default()
  i.bans = False
  i.dm_reactions=False
  i.dm_typing = False
  i.guild_reactions = False
  i.guild_typing = False
  i.guilds=True
  i.members=False
  i.integrations=False
  i.webhooks=False
  i.invites=False
  i.presences=False
  i.reactions=False
  i.typing=False
  i.voice_states=False
  return i
  