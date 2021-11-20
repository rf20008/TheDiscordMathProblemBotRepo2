from dislash.interactions.interaction import BaseInteraction
import nextcord, dislash
from copy import deepcopy
from warnings import warn
from helpful_modules import checks

class HelperCog(nextcord.ext.commands.Cog):
    "A helper cog :-) However, by itself, it does not implement any commands."

    def __init__(self, bot):
        "Helpful __init__, the entire reason I decided to make this so I could transfer modules"
        self.b = bot._transport_modules
        checks.setup(bot)
        (
            self.problems_module,
            self.SuccessEmbed,
            self.ErrorEmbed,
            self.the_documentation_file_loader,
        ) = (
            self.b["problems_module"],
            self.b["custom_embeds"].SuccessEmbed,
            self.b["custom_embeds"].ErrorEmbed,
            self.b["the_documentation_file_loader"],
        )
        self.cache = bot.cache
        self.slash = bot.slash
        self.bot = bot
        self.check_for_cooldown = self.bot._transport_modules["check_for_cooldown"]
        self.custom_embeds = self.bot._transport_modules["custom_embeds"]
        self.checks = self.bot._transport_modules["checks"]

    @property
    def trusted_users(self):
        "Syntactic sugar? A shorthand for self.bot.trusted_users"
        return self.bot.trusted_users

    @property
    def vote_threshold(self):
        "A shorthand for self.bot.vote_threshold"
        return self.bot.vote_threshold

    def _change_vote_threshold(
        self,
        new_vote_threshold,
        ctx=None,
        *,
        bypass_ctx_check=False,
        bypass_argument_checks=False,
    ):
        "A helper method that will change the vote_threshold"
        if not bypass_ctx_check:
            assert isinstance(
                ctx, (nextcord.ext.commands.Context, dislash.BaseInteraction)
            )
            if ctx.author.id not in self.trusted_users:
                raise RuntimeError(
                    f"Sadly, you're not allowed to do this, {ctx.author.mention} ☹️"
                )
        if not bypass_argument_checks:
            if not isinstance(new_vote_threshold, int):
                raise TypeError(
                    f"new_vote_threshold is of type {type(new_vote_threshold)}, not int"
                )
            if new_vote_threshold <= 0:
                raise ValueError("new_vote_threshold must be bigger than 0")
        self.bot.vote_threshold = new_vote_threshold

    def _change_trusted_users(
        self,
        new_trusted_users,
        ctx=None,
        *,
        bypass_ctx_check=False,
        bypass_argument_checks=False,
    ):
        "A helper method that will change the trusted_users"
        if not bypass_ctx_check:
            assert isinstance(
                ctx, (nextcord.ext.commands.Context, dislash.BaseInteraction)
            )
            if ctx.author.id not in self.trusted_users:
                raise RuntimeError(
                    f"Sadly, you're not allowed to do this, {ctx.author.mention} ☹️"
                )
        if not bypass_argument_checks:
            if not isinstance(new_trusted_users, (list, tuple)):
                raise TypeError(
                    f"new_trusted_users is of type {type(new_trusted_users)}, not list"
                )
            if len(new_trusted_users) == 0:
                warn("You are removing all trusted users", Warning)
        self.bot.trusted_users = new_trusted_users
