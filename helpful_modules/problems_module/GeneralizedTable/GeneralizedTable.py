"""
The Discord Math Problem Bot
Copyright (C) August 2022 <No organization yet>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses>"""
import typing
from collections import namedtuple as NamedTuple
from types import FunctionType
from typing import *

import orjson
from mpmath import *

from ..cache.final_cache import MathProblemCache
from ..errors import *

T = typing.TypeVar("T")
class ConverterData(NamedTuple):
    """ConverterData class

    This class is used to denote using custom classes in MySQL using the GeneralizedTable function.

    Attributes
    ---------

    type: The type that this is wrapping
    converter: A converter than converts the type given to a string
    deconverter: A converter that converts a well-formed string to the type expected.

    Let the type being wrapped T. Let X be any object of type T.
    It is expected that deconverter(converter(X)) == X for all X of type T.
    Additionally we expect converter(deconverter(X)) == X for all X of type T.
    """
    type: T
    converter: typing.Callable[[T], str]
    deconverter: typing.Callable[[str], T]
TYPE_TO_SQLITE_TYPE = {
    int: "BIGINT",
    str: "MEDIUMTEXT(10000000)",
    float: "DOUBLE(53)"
    bytes: "BIGBLOB",
    dict: ConverterData(
        dict,
        converter=orjson.dump,
        deconverter=orjson.load,
    ),
    mpf: ConverterData(
        mpf,
        converter=mpf,
        deconverter = lambda a: str(a)
    )

}

Converter = typing.Callable[[T], str]
DeConverter= typing.Callable[[str], T]
def addextratype(type_used: T, converter: Converter, deconverter: DeConverter) -> None:
    TYPE_TO_SQLITE_TYPE[T] = ConverterData(type_used, converter, deconverter)


UNUSABLE_NAMES = {
    "problems",
    "quiz_problems",
    "quiz_submissions",
    "quizzes",
    "user_data",
    "quiz_submission_sessions",
    "guild_data",
    "quiz_description"
}
class GeneralizedTable:
    """A table that can be used for general purposes and can be used"""
    cache: MathProblemCache
    table_name: str
    column_names: Sequence[str]
    name_to_type_mapping: Mapping[str, type]

    def __init__(self, cache: MathProblemCache, table_name: str, column_names: Sequence[str], name_to_type_mapping: Mapping[str, type]):
        self.cache=cache
        if table_name in UNUSABLE_NAMES:
            raise MathProblemsModuleException("You cannot use this table name")
        self.table_name=table_name
        self.column_names=column_names
        self.name_to_type_mapping=name_to_type_mapping

    async def create_my_table(self):
        if self.cache.use_sqlite:
            sql_query = "CREATE TABLE IF NOT EXISTS "
            sql_query+=self.table_name
            sql_query += "("
            for column_type, column_name in self.name_to_type_mapping:
                # Verify the column type
                if not isinstance(column_type, (str, dict)):
                    raise MathProblemsModuleException("The column type is invalid!")
                if isinstance(column_type, str):
                    sql_query+= column_name + " " + column_type
                else:
                    sql_query += column_name + " MEDIUMTEXT(1000000)"
                raise NotImplementedError
            await self.cache.run_sql(sql_query)