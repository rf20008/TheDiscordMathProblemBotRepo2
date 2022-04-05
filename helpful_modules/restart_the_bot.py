import asyncio
import disnake
import subprocess
from typing import NoReturn

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
        await asyncio.sleep(3)
        await self.bot.close()
        await asyncio.sleep(5)
        subprocess.run('cd ../') # Make sure that we're in the right directory
        subprocess.run(
            [
                'python3.10'
                'main.py'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        await asyncio.sleep(0.5)
        os._exit(0)


