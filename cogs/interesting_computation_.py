from math import gcd

import disnake
import more_itertools
from disnake.ext import commands, tasks
from mpmath import *

from helpful_modules import (checks, custom_bot, problems_module,
                             threads_or_useful_funcs)
from helpful_modules.custom_embeds import ErrorEmbed, SimpleEmbed, SuccessEmbed
from helpful_modules.problems_module import *

from .helper_cog import HelperCog

MAX_NUM = 1_000_000_000_000_000_000_000_000_000_000


class InterestingComputationCog(HelperCog):
    def __init__(self, bot):
        self.bot=bot
        self.cache = bot.cache
        super().__init__(bot)

    class ChineseRemainderTheoremComputer:
        def __init__(self, remainders, moduli):
            if len(remainders) != len(moduli):
                raise ValueError(
                    "The length of the remainders does not equal the length of the moduli!"
                )
            for a, b in more_itertools.distinct_combinations(moduli, 2):
                if gcd(a, b) != 1:
                    raise ValueError(
                        "Not all the moduli are relatively pairwise coprime!!!!!!"
                    )
            for i in range(len(moduli)):
                if not (
                    isinstance(remainders[i], int)
                    and isinstance(moduli[i], int)
                    and modli[i] > remainders[i] > 0
                ):
                    raise ValueError("The CRT prerequsites are not satisifed!")
            self.remainders = remainders
            self.moduli = moduli

        def compute(self):
            """Compute the CRT
            Algorithm credits to my brother"""
            product = 1
            for i in range(len(moduli)):
                product *= moduli[i]
            sum = 0
            for i in range(len(moduli)):
                num = product // moduli[i]
                # compute the multiplicative number of product/b_i mod b_i
                return_val = threads_or_useful_funcs.extended_gcd(product, moduli[i])
                mult_inv = return_val[0][1]
                sum += num * mult_inv * remainders[i]
            return sum

    @checks.no_insanely_huge_numbers_check()
    @commands.slash_command(name = "crt_problem", description="crt_problem")
    async def crt_problem(self, inter: disnake.ApplicationCommandInteraction,  moduli: str, nums: str):
        """/crt_problem (moduli: str (should be a space-seperated list of numbers)) (nums: str (should be a space-seperated list of numbers)
        Solve the CRT problem for when the moduli are `moduli` and the nums are `nums`

        """
        moduliA = moduli
        numsA = nums

        if len(moduliA) >= 300 or len(numsA) >= 300:
            return inter.send(embed=ErrorEmbed("Too many moduli or nums!"))
        try:
            moduli = [int(item) for item in moduliA.split()]
        except ValueError:
            inter.send(
                embed=ErrorEmbed("Could not convert moduli to a list of numbers!")
            )
            raise
        if len(moduli_) >= 100:
            return inter.send(embed=ErrorEmbed("Too many moduli!"))
        for i in moduli:
            if i <= 0 or i > 10**30:
                return inter.send("All the remainders must be positive")
        for i in range(len(moduli) - 1):
            for j in range(i, len(moduli)):
                if math.gcd(moduli[i], moduli[j]) != 1:
                    return inter.send(
                        embed=ErrorEmbed(
                            "The chinese remainder theorem doesn't hold unless the numbers are relatively prime"
                        )
                    )
            if moduli[i] >= MAX_NUM:
                raise MathProblemsModuleException("Remainder too big")
            for j in range(i, len(moduli)):
                if math.gcd(moduli[i], moduli[j]) != 1:
                    return inter.send(
                        embed=ErrorEmbed(
                            "The chinese remainder theorem doesn't hold unless the numbers are relatively prime"
                        )
                    )

        try:
            nums = [int(item) for item in numsA.split()]
        except ValueError:
            inter.send(embed=ErrorEmbed("Could not convert nums to a list of numbers!"))
            raise
        if len(nums) >= 100:
            return inter.send(embed=ErrorEmbed("Too many nums!"))
        if len(moduli) != len(nums):
            return inter.send(
                embed=ErrorEmbed("#moduli != # nums : therefore we can't use CRT.")
            )

        for i in range(len(nums)):
            if nums[i] <= 0:
                return inter.send("All the remainders must be positive!")
            if nums[i] >= MAX_NUM:
                raise MathProblemsModuleException("Number too big")
            if nums[i] >= moduli[i]:
                raise MathProblemsModuleException("nums[i] > moduli[i]")
        CRTC = InterestingComputationCog.ChineseRemainderTheoremComputer(
            remainders=nums, nums=nums
        )
        inter.send(embed=SuccessEmbed(f"The result is f{CRTC.compute()}."))
        return



def setup(bot):
    bot.add_cog(InterestingComputationCog(bot))


def teardown(bot):
    bot.remove_cog("InterestingComputationCog")
