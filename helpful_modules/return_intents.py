from disnake import Intents


def return_intents():
    i = Intents.default()
    i.typing = False
    i.presences = False
    i.members = False
    i.reactions = False
    i.bans = False
    return i
