import asyncio
import logging
import time
from types import FunctionType

import disnake

import helpful_modules
from helpful_modules import problems_module
from helpful_modules.constants_loader import BotConstants
from helpful_modules.problems_module.cache import MathProblemCache


class TheDiscordMathProblemBot(disnake.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_closing = False
        try:
            self.tasks = kwargs.pop("tasks")
        except:
            raise KeyError("Uh oh")
        self._on_ready_func = kwargs.pop(
            "on_ready_func"
        )  # Will be called when the bot is ready (with an argument of itself)
        assert isinstance(self.tasks, dict)
        for task in self.tasks.values():
            assert isinstance(task, disnake.ext.tasks.Loop)
            task.start()  # TODO: add being able to change it
        self.timeStarted = float("inf")
        self.cache = (
            kwargs.get("cache")
            if isinstance(
                kwargs.get("cache"), helpful_modules.problems_module.MathProblemCache
            )
            else False
        )
        if self.cache is False:
            raise TypeError("Not of type MathProblemCache")
        self.constants = (
            kwargs.get("constants")
            if isinstance(kwargs.get("constants"), BotConstants)
            else False
        )
        if self.constants is False:
            raise TypeError("Constants is not a BotConstants object")
        self.trusted_users = kwargs.get("trusted_users", None)
        if not self.trusted_users and self.trusted_users != []:
            raise TypeError("trusted_users was not found")
        self.blacklisted_users = kwargs.get("blacklisted_users", [])
        self.closing_things = []

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

    def add_task(self, task):
        self.tasks.append(task)
        task.start()

    async def close(self):
        self.is_closing = True
        for task in self._tasks:
            task.stop()
        await asyncio.sleep(5)
        self.is_closing = False
        await asyncio.gather(*self.closing_things)
        await super.close()

    def add_closing_thing(self, thing: types.FunctionType) -> None:

        assert asyncio.iscoroutinefunction(thing)
        self.closing_things.append(thing)
