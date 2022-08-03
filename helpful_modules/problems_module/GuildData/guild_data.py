import json
import typing
from warnings import warn

from ...threads_or_useful_funcs import attempt_to_import_orjson
from ..errors import InvalidDictionaryInDatabaseException
from .the_basic_check import CheckForUserPassage

JSON = json
orjson, could_import = attempt_to_import_orjson()
if could_import:
    JSON = orjson
else:
    del orjson, could_import
    

class GuildData:
    global_cache: "MathProblemCache"
    blacklisted: bool
    guild_id: int
    can_create_problems_check: CheckForUserPassage
    can_create_quizzes_check: CheckForUserPassage
    mods_check: CheckForUserPassage

    def __init__(
        self,
        guild_id: int,
        blacklisted: bool,
        can_create_problems_check: str | CheckForUserPassage,
        can_create_quizzes_check: str | CheckForUserPassage,
        mods_check: str | CheckForUserPassage,
    ):
        self.guild_id = guild_id
        self.blacklisted = blacklisted
        for property, val in (
            ("can_create_problems_check", can_create_problems_check),
            ("can_create_quizzes_check", can_create_quizzes_check),
            ("mods_check", mods_check)
        ):
            if isinstance(val, (str, dict)):
                res=val
                if isinstance(val, str):
                    try:
                        res = JSON.loads(val)
                    except json.JSONDecodeError as exc:
                        # Oh no
                        raise
                    except TypeError as exc:
                        raise InvalidDictionaryInDatabaseException.from_invalid_data(val) from exc
                try:
                    setattr(self, property, CheckForUserPassage.from_dict(JSON.loads(val)))

                except KeyError as exc:
                    raise InvalidDictionaryInDatabaseException(
                        f"I was able to parse {mods_check} into a dictionary, but I couldn't find the key called {str(exc)}!"
                    ) from exc
            else:
                if isinstance(val, CheckForUserPassage):
                    setattr(self, property, val)
                

    @classmethod
    def from_dict(cls, data: dict, cache) -> "GuildData":
        return cls(
            blacklisted=bool(data["blacklisted"]),
            guild_id=data["guild_id"],
            can_create_problems_check=data["can_create_problems_check"],
            mods_check=data["mods_check"],
            can_create_quizzes_check=data["can_create_quizzes_check"],
        )

    def to_dict(self, include_cache: bool) -> dict:
        dict_to_return = {
            "blacklisted": int(self.blacklisted),
            "guild_id": self.guild_id,
            "can_create_problems_check": self.can_create_problems_check,
            "can_create_quizzes_check": self.can_create_quizzes_check,
            "mods_check": self.mods_check,
        }
        if include_cache:
            dict_to_return["cache"] = self.global_cache

        return dict_to_return

    def get_mod_check(self):
        return self.mods_check

    def set_mod_check(self, value: CheckForUserPassage):
        if not isinstance(value, CheckForUserPassage):
            warnings.warn(
                "The mod check is being set to an object that is not of type CheckForUserPassage, instead it is of type "
                + value.__class__.__name__
                + "...",
                stacklevel=2,
            )  # noqa: E401
        self.mods_check = value

    def del_mod_check(self):
        del self.mods_check

    mod_check = property(get_mod_check, set_mod_check, del_mod_check)

    @classmethod
    def default(cls, guild_id: int) -> "GuildData":
        return cls(
            guild_id=guild_id,
            blacklisted=False,
            can_create_quizzes_check=CheckForUserPassage.default(),
            can_create_problems_check=CheckForUserPassage.default(),
            mods_check=CheckForUserPassage.default_mod_check(),
        )

    def __eq__(self, other: typing.Any):
        if not isinstance(other, GuildData):
            return False  # There is no way that these objects are equal if they are of different types
        return (
            self.guild_id == other.guild_id
            and self.blacklisted == other.blacklisted
            and self.mod_check == other.mod_check
            and self.can_create_quizzes_check == other.can_create_quizzes_check
            and self.can_create_problems_check == other.can_create_problems_check
        )

    def is_default(self):
        return self == GuildData.default(self.guild_id)
