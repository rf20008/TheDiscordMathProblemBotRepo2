# This module is the 'core' of my bot!
# It's quite important.

# Licensed under GPLv3

#     This file is part of The Discord Math Problem Bot.
# 
#     The Discord Math Problem Bot is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     The Discord Math Problem Bot is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with the Discord Math Problem Bot.  If not, see <https://www.gnu.org/licenses/>.

from .errors import *
from .base_problem import BaseProblem
from .quizzes import *
from .cache import MathProblemCache
from . import *

__version__ = "0.1.0"
