import asyncio
import copy

import aiosqlite

from ...dict_factory import dict_factory
from ..appeal import Appeal
from ..mysql_connector_with_stmt import *
from ..mysql_connector_with_stmt import mysql_connection

from .guild_data_related_cache import GuildDataRelatedCache


class AppealsRelatedCache(GuildDataRelatedCache):
    async def set_appeal_data(self, data: Appeal):
        assert isinstance(data, Appeal)  # Basic type-checking

        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """INSERT INTO appeals (special_id, appeal_str, appeal_num, user_id, timestamp,type) 
                    VALUES (?,?,?,?,?,?) 
                    ON CONFLICT REPLACE 
                    special_id=?, appeal_str=?, appeal_num=?, user_id=?, timestamp=?, type=?""",
                    (
                        data.special_id,
                        data.appeal_str,
                        data.appeal_num,
                        data.user_id,
                        data.timestamp,
                        data.type,
                        data.special_id,
                        data.appeal_str,
                        data.appeal_num,
                        data.user_id,
                        data.timestamp,
                        data.type,
                    ),
                )  # TODO: test
                await conn.commit()
        else:
            with self.get_a_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(
                    """INSERT INTO appeals (special_id, appeal_str, appeal_num, user_id, timestamp,type) 
                    VALUES (%s,%s,%s,%s,%s,%s) 
                    ON DUPLICATE KEY UPDATE 
                    special_id=%s, appeal_str=%s, appeal_num=%s, user_id=%s, timestamp=%s, type=%s""",
                    (
                        data.special_id,
                        data.appeal_str,
                        data.appeal_num,
                        data.user_id,
                        data.timestamp,
                        data.type,
                        data.special_id,
                        data.appeal_str,
                        data.appeal_num,
                        data.user_id,
                        data.timestamp,
                        data.type,
                    ),
                )  # TODO: test

    async def get_appeal(self, special_id: int, default: Appeal) -> Appeal:
        assert isinstance(guild_id, int)
        assert isinstance(default, GuildData)

        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                conn.row_factory = dict_factory
                cursor = await conn.cursor()
                await cursor.execute(
                    "SELECT * FROM appeals WHERE special_id = ?", (special_id,)
                )
                results = list(await cursor.fetchall())
                if len(results) == 0:
                    return default
                elif len(results) == 1:
                    return GuildData.from_dict(results[0])
                else:
                    raise SQLException(
                        "There were too many rows with the same special id in the appeals table!"
                    )
        else:
            with self.get_a_connection() as connection:
                cursor = connection.cursor(dictionaries=True)

                cursor.execute(
                    "SELECT * FROM appeals WHERE special_id = %s", (special_id,)
                )
                results = list(cursor.fetchall())
                if len(results) == 0:
                    return default
                elif len(results) == 1:
                    return GuildData.from_dict(results[0])
                else:
                    raise SQLException(
                        "There were too many rows with the same special id in the appeals table!"
                    )
