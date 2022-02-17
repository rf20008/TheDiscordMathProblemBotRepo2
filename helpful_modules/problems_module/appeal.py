from typing import *


class Appeal:
    __slots__ = (
        "user_id",
        "appeal_msg",
        "timestamp",
        "appeal_num",
        "cache",
        "special_id",
    )

    def __init__(
        self,
        *,
        user_id: int,
        appeal_msg: str,
        timestamp: int,
        appeal_num: int,
        special_id: int,
        cache: "MathProblemCache",
    ):
        self.user_id = user_id
        self.appeal_msg = appeal_msg
        self.timestamp = timestamp
        self.appeal_num = appeal_num
        self.special_id = special_id
        self.cache = cache

    @classmethod
    def from_dict(cls, data: dict, cache: "MathProblemCache"):
        return cls(
            user_id=data["user_id"],
            appeal_msg=data["appeal_msg"],
            timestamp=data["timestamp"],
            appeal_num=data["appeal_num"],
            special_id=data["special_id"],
            cache=cache,
        )

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "appeal_msg": self.appeal_num,
            "timestamp": self.timestamp,
            "appeal_num": self.appeal_num,
            "special_id": self.special_id,
        }

    def __str__(self):
        return f"""
        Appeal from <@{self.user_id}>:
        timestamp: {disnake.utils.format_dt(self.timestamp)}
        
        Appeal message: {self.appeal_msg}
        
        This is appeal #{self.appeal_num}
        and its special id is {self.special_id}
        
"""
