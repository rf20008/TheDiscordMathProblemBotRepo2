import nextcord, dislash
class TheDiscordMathProblemBot(nextcord.ext.commands.Bot):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = kwargs.pop('tasks')
        assert isinstance(self.tasks, dict)
        for task in self.tasks.values():
            assert isinstance(task, nextcord.ext.tasks.Loop)
            task.start()
    def get_task(self,task_name):
        return self.tasks[task_name]
        