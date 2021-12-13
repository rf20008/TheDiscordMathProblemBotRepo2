<<<<<<< HEAD
from nextcord import Intents
=======
from disnake import Intents
>>>>>>> disnake


def return_intents():
    i = Intents.default()
    i.typing = False
    i.presences = False
    i.members = False
<<<<<<< HEAD

=======
    i.reactions = False
    i.bans = False
>>>>>>> disnake
    return i
