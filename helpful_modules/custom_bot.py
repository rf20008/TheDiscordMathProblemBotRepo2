import logging
import time

import disnake

import helpful_modules
from helpful_modules import problems_module
from helpful_modules.constants_loader import BotConstants
from helpful_modules.problems_module.cache import MathProblemCache
from helpful_modules.FileDictionaryReader import AsyncFileDict

class TheDiscordMathProblemBot(disnake.ext.commands.Bot):

    def __init__(self, *args, **kwargs):
        self.is_closing = False

        self.tasks = kwargs.pop("tasks")
        self.config_json =AsyncFileDict("config.json")
        self.trusted_users = kwargs.pop("trusted_users")
        self._on_ready_func = kwargs.pop(
            "on_ready_func"
        )  # Will be called when the bot is ready (with an argument of itself
        cache = kwargs.pop("cache")
        self.cache = (
            cache
            if isinstance(
                cache,
helpful_modules.problems_module.MathProblemCache
            )
            else False
        )
        if self.cache is False:
            raise TypeError("Not of type MathProblemCache")
        #print(self.cache)
        self.constants = (
            kwargs.pop("constants")
            if isinstance(kwargs.get("constants"), BotConstants)
            else False
        )
        if self.constants is False:
            raise TypeError("Constants is not a BotConstants object")
        super().__init__(*args, **kwargs)
        
        assert isinstance(self.tasks, dict)
        self.restart = RestartTheBot(self)
        for task in self.tasks.values():
            assert isinstance(task, disnake.ext.tasks.Loop)
            task.start()  # TODO: add being able to change it
        self.timeStarted = float("inf")
        
        
        #self.trusted_users = kwargs.get("trusted_users", None)
        # if not self.trusted_users and self.trusted_users != []:
        #    raise TypeError("trusted_users was not found")
        # self.blacklisted_users = kwargs.get("blacklisted_users", [])
        self.closing_things = []
        self.support_server=None
    def get_task(self, task_name):
        return self.tasks[task_name]

    def start_tasks(self):
        for task in self.tasks.values():
            task.start()

    @property
    def log(self):
        return logging.getLogger(__name__)

    @property
    def uptime(self):
        return time.time() - self.timeStarted  # TODO: more accurate time + timestamp

    async def on_ready(self):
        self.timeStarted = time.time()
        await self._on_ready_func(self)

    def owns_and_is_trusted(self, user: disnake.User):
        if not hasattr(self, "owner_id") or not self.owner_id or self.owner_id == None:
            return False
        return user.id in self.trusted_users and user.id == self.owner_id
