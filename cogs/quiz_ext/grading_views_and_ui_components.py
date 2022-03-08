from disnake import commands, ui
import disnake
from helpful_modules import problems_module as pm
from helpful_modules.threads_or_useful_funcs import base_on_error
from helpful_modules.my_modals import MyModal
from helpful_modules.custom_bot import TheDiscordMathProblemBot
from typing import Union, List, Optional


class GradingQuizView(ui.View):
    def __init__(
        self,
        *,
        quiz_id: int,
        user_id: int,
        bot: TheDiscordMathProblemBot,
        attempt_num: int,
        problem_num: int,
        grader_user_id: int,
        timeout: int = 600
    ):
        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )
        self._buttons = (self.exit_and_stop, self.continue_grading)
        self.quiz_id = quiz_id
        self.user_id = user_id
        self._bot = bot
        self._attempt_num = attempt_num
        self.target = grader_user_id
        self.problem_num = problem_num

    def stop(self):
        super().__stop__()
        for button in self._buttons:
            button.disabled = True

    @ui.button(
        label="Exit and stop grading (Your changes will be saved)",
        style=disnake.ButtonStyle.danger,
    )
    async def exit_and_stop(
        self,
        button: disnake.Button,
        inter: disnake.MessageInteraction,
    ):
        button.disabled = True
        content = inter.message.content
        content = "Thank you for grading Your changes have been saved!" + content
        self.stop()
        await inter.response.edit_message(content=content, view=self)
        return

    @ui.button(label="Continue Grading", style=disnake.ButtonStyle.green)
    async def continue_grading(
        self, button: disnake.ui.Button, inter: disnake.MessageInteraction
    ):
        assert isinstance(inter.bot, TheDiscordMathProblemBot)
        await inter.response.send_modal(MyModal())

    async def on_error(self, item: ui.Item, exc: Exception):
        await base_on_error(exc)
        raise NotImplementedError

    async def interaction_check(self, inter: disnake.MessageInteraction):
        return (
            inter.author.id == self.grader_user_id
            and inter.component.custom_id in [self.continue_grading.custom_id, self.exit_and_stop.custom_id]
        )


async def on_grade_modal_callback(
    modal_inter: disnake.ModalInteraction,
    quiz_id: int,
    reasoning_input_custom_id: str,
    grade_input_custom_id: str,
    cache: pm.MathProblemCache,
    problem_num: int,
    user_id: int,
    attempt_num: int,
):
    quiz: Quiz = await cache.get_quiz(quiz_id)
    try:
        grade = float(modal_inter.text_values[grade_input_custom_id])
    except ValueError:
        await modal_inter.send("Invalid input....")
        return

    submissions = list(
        filter(
            lambda session: session.user_id == user_id
            and session.attempt_num == attempt_num,
            quiz.existing_sessions,
        )
    )
    session: pm.QuizSolvingSession = copy.copy(submissions[0])
    submission=session.answers[problem_num]
    submission.set_grade(grade)
    submission.reasoning = modal_inter.text_values[reasoning_input_custom_id]
    await quiz.update_self()
    await modal_inter.send(
        view=GradingQuizView(
            timeout=200,
            user_id=user_id,
            quiz_id=quiz_id,
            grader_user_id=inter.author.id,
            bot=inter.bot,
            attempt_num=attempt_num,
            channel = modal_inter.channel
        )
    )


class GradingModal(ui.Modal):
    def __init__(
        self,
        *,
        target_user_id: int,
        bot: TheDiscordMathProblemBot,
        quiz_id: int,
        grader_user_id: int,
        attempt_num: int,
        problem_num: int,
        channel: Union[disnake.TextChannel, disnake.PartialMessageable],
        reasoning_input_custom_id: str,
        grade_input_custom_id: str,
        title: str,
        components: Union[
            disnake.ui.ActionRow,
            disnake.ui.WrappedComponent,
            List[
                Union[
                    disnake.ui.ActionRow,
                    disnake.ui.WrappedComponent,
                    List[disnake.ui.WrappedComponent],
                ]
            ],
        ],
        custom_id=...,
        timeout=60*60
    ):
        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )
        self._bot = bot
        self.quiz_id = quiz_id
        self.grader_quiz_id = grader_user_id,
        self.target_user_id = target_user_id
        self._attempt_num = attempt_num
        self._channel = channel
        self.reasoning_input_custom_id = reasoning_input_custom_id
        self.grade_input_custom_id = grade_input_custom_id
        self.problem_num = problem_num

    async def on_timeout(self):
        try:
            await self._channel.send("You didn't submit the modal in time!")
        except disnake.Forbidden:
            raise RuntimeError("I don't have permission to send to the channel and tell them that they ran out of time")

    async def callback(self, inter: disnake.ModalInteraction):
        if inter.author.id is not self.grader_quiz_id:
            raise RuntimeError("Uh oh!")
        assert isinstance(inter.bot, TheDiscordMathProblemBot)

        #raise NotImplementedError("I haven't fully implemented this yet!")
        return await on_grade_modal_callback(
            modal_inter=inter,
            quiz_id=self.quiz_id,
            grade_input_custom_id=self.grade_input_custom_id,
            reasoning_input_custom_id=self.reasoning_input_custom_id,
            problem_num=self.problem_num,
            attempt_num=self._attempt_num,
            cache=inter.bot.cache
        )

    async def on_error(self, error: Exception, inter: disnake.ModalInteraction):
        return await inter.send(**base_on_error(inter, error))

