from disnake import commands, ui
import disnake
from helpful_modules import problems_module as pm
from helpful_modules.threads_or_useful_funcs import base_on_error
class GradingQuizView(ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buttons = (self.exit_and_stop, self.continue_grading)

    @ui.button(
        label="Exit and stop grading (Your changes will be saved)",
        style=disnake.ButtonStyle.danger
    )
    async def exit_and_stop(self, inter: disnake.MessageInteraction,):
        for button in self._buttons:
            button.disabled=True
        content = inter.message.content
        await inter.response.edit_message
        await inter.send(
            "Thank you for grading! Your changes have been saved!"
        )
        return

    @ui.button(
        label='Continue Grading',
        style=disnake.ButtonStyle.green
    )
    async def continue_grading(self, inter: disnake.MessageInteraction):
        raise NotImplementedError

    async def on_error(self, item: ui.Item, exc: Exception):
        await base_on_error(exc)
        raise NotImplementedError


async def on_grade_modal_callback(modal_inter: disnake.ModalInteraction, quiz_id: int, reasoning_input_custom_id: str,
                                  grade_input_custom_id: str, cache: pm.MathProblemCache)
    quiz = await cache.get_quiz(quiz_id)
    if not modal_inter.text_values[reasoning_input_custom_id].isnumeric():
        await modal_inter.send("Invalid input....")
