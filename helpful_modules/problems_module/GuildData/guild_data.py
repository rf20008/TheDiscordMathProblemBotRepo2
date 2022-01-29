import json

from ..errors import InvalidDictionaryInDatabaseException
from .the_basic_check import CheckForUserPassage


class GuildData:
    blacklisted: bool
    guild_id: int
    can_create_problems_check: CheckForUserPassage
    can_create_quizzes_check: CheckForUserPassage
    mods_check: CheckForUserPassage
    cache: "MathProblemCache"

    def __init__(
        self,
        guild_id: int,
        blacklisted: bool,
        can_create_problems_check: str,
        can_create_quizzes_check: str,
        mods_check: str,
        cache,
    ):
        self.cache = cache
        self.guild_id = guild_id
        self.blacklisted = blacklisted
        try:
            self.can_create_problems_check = CheckForUserPassage.from_dict(
                json.loads(can_create_problems_check)
            )
        except json.JSONDecodeError as exc:
            raise InvalidDictionaryInDatabaseException.from_invalid_data(
                can_create_problems_check
            ) from exc
        except KeyError as exc:
            raise InvalidDictionaryInDatabaseException(
                f"I was able to parse {can_create_problems_check} into a dictionary, but I couldn't find the key called {str(exc)}!"
            ) from exc
        try:
            self.can_create_quizzes_check = CheckForUserPassage.from_dict(
                json.loads(can_create_quizzes_check)
            )
        except json.JSONDecodeError as exc:
            raise InvalidDictionaryInDatabaseException.from_invalid_data(
                can_create_quizzes_check
            ) from exc
        except KeyError as exc:
            raise InvalidDictionaryInDatabaseException(
                f"I was able to parse {can_create_quizzes_check} into a dictionary, but I couldn't find the key called {str(exc)}!"
            ) from exc

        try:
            self.mods_check = CheckForUserPassage.from_dict(json.loads(mods_check))
        except json.JSONDecodeError as exc:
            raise InvalidDictionaryInDatabaseException.from_invalid_data(
                mods_check
            ) from exc
        except KeyError as exc:
            raise InvalidDictionaryInDatabaseException(
                f"I was able to parse {mods_check} into a dictionary, but I couldn't find the key called {str(exc)}!"
            ) from exc

    @classmethod
    def from_dict(cls, data: dict, cache) -> "GuildData":
        return cls(
            blacklisted=bool(data["blacklisted"]),
            guild_id=data["guild_id"],
            can_create_problems_check=data["can_create_problems_check"],
            mods_check=data["mods_check"],
            can_create_quizzes_check=data["can_create_quizzes_check"],
            cache=cache,
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
            dict_to_return["cache"] = self.cache

        return dict_to_return

    @classmethod
    def default(cls, guild_id: int) -> "GuildData":
        return cls(
            guild_id=guild_id,
            blacklisted=False,
            can_create_quizzes_check=CheckForUserPassage.default(),
            can_create_problems_check=CheckForUserPassage.default(),
            mods_check=CheckForUserPassage.default_mod_check(),
        )
