import disnake, logging
import helpful_modules
import time

from helpful_modules import problems_module
from helpful_modules.problems_module.cache import MathProblemCache

class TheDiscordMathProblemBot(disnake.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = kwargs.pop("tasks")
        self._on_ready_func = kwargs.pop('on_ready_func') # Will be called when the bot is ready (with an argument of itself)
        assert isinstance(self.tasks, dict)
        for task in self.tasks.values():
            assert isinstance(task, disnake.ext.tasks.Loop)
            task.start() #TODO: add being able to change it
        self.timeStarted = float('inf')
        self.cache = (kwargs.get('cache') if isinstance(kwargs.get('cache'), helpful_modules.problems_module.MathProblemCache) else None)
        if not self.cache:
            raise TypeError("Not of type MathProblemCache")

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
        return time.time() - self.timeStarted
    async def on_ready(self):
        self.timeStarted = time.time()
        await self._on_ready_func(self)