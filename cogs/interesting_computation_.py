from .helper_cog import HelperCog
from mpmath import *
from disnake.ext import commands, tasks
import disnake
from helpful_modules import checks, problems_module, custom_bot, threads_or_useful_funcs
from math import gcd
import more_itertools
class InterestingComputationCog(HelperCog):
    class ChineseRemainderTheoremComputer:
        def __init__(self, remainders, moduli):
            if len(remainders) != len(moduli):
                raise ValueError("The length of the remainders does not equal the length of the moduli!")
            for a,b in more_itertools.distinct_combinations(moduli, 2):
                if gcd(a,b) != 1:
                    raise ValueError("Not all the moduli are relatively pairwise coprime!!!!!!")
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
            product=1
            for i in range(len(moduli)):
                product *= moduli[i]
            sum = 0
            for i in range(len(moduli)):
                num = product//moduli[i]
                # compute the multiplicative number of product/b_i mod b_i
                return_val = threads_or_useful_funcs.extended_gcd(product, moduli[i])
                mult_inv = return_val[0][1]
                sum += num*mult_inv * remainders[i]
            return sum

def setup(bot):
    bot.add_cog(InterestingComputationCog(bot))

def teardown(bot):
    bot.remove_cog("InterestingComputationCog")