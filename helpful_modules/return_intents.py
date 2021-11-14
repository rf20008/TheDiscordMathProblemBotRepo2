from nextcord import Intents


def return_intents():
    i = Intents.default()
    i.typing = False
    i.presences = False
    i.members = False

    return i
