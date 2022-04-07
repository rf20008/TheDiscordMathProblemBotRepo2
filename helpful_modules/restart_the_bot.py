import asyncio
import disnake
import subprocess
from typing import NoReturn
from sys import executable
#from .custom_bot import TheDiscordMathProblemBot

RESTART_MESSAGE_WARNING = (
    "The bot will automatically restart to apply an update after 20 seconds. " 
    "It should be back in a few seconds!"
)
RESTART_MESSAGE_FINAL_WARNING = (
    "The bot is automatically restarting! It should be back in a few seconds!"
)
class RestartTheBot:
    def __init__(self, bot: "TheDiscordMathProblemBot"):
        self.bot=bot

    async def notify_before_restarting(self) -> None:
        channel = await self.bot.fetch_channel(self.bot.constants.BOT_RESTART_CHANNEL)
        await channel.send(RESTART_MESSAGE_WARNING)
        await asyncio.sleep(20)
        await channel.send(RESTART_MESSAGE_FINAL_WARNING)
    async def restart_the_bot(self) -> NoReturn:
        print("The bot is now restarting!")
        await self.notify_before_restarting()
        await self.actual_restart()
    async def actual_restart(self):
        await asyncio.sleep(3)
        await self.bot.close()
        await asyncio.sleep(5)
        subprocess.run(['cd', '../']) # Make sure that we're in the right directory
        command = executable + " main.py"
        subprocess.run(
            command.split(),
            capture_output=True,
            shell=True
        )
        os._exit(1)


