import asyncio
import copy

import aiosqlite

from ..GuildData.guild_data import GuildData
from ..mysql_connector_with_stmt import *
from ..mysql_connector_with_stmt import mysql_connection
from .user_data_related_cache import UserDataRelatedCache


class GuildDataRelatedCache:
    def set_guild_data(self, data: GuildData):
        assert isinstance(data, GuildData)  # Basic type-checking

        if self.use_sqlite:
            async with aiosqlite.connect(self.db) as conn:
                cursor = await conn.cursor()
                await cursor.execute(
                    """INSERT INTO guild_data (guild_id, blacklisted, can_create_problems_check, can_create_quizzes_check, mod_check) 
                    VALUES (?,?,?,?,?) 
                    ON CONFLICT REPLACE 
                    guild_id = ?, blacklisted=?, can_create_problems_check = ?, can_create_quizzes_check = ?, mod_check = ?""",
                    (
                        data.guild_id,
                        int(data.blacklisted),
                        str(data.can_create_problems_check.to_dict()),
                        str(data.can_create_quizzes_check.to_dict()),
                        str(data.mods_check.to_dict()),
                        data.guild_id,
                        int(data.blacklisted),
                        str(data.can_create_problems_check.to_dict()),
                        str(data.can_create_quizzes_check.to_dict()),
                        str(data.mods_check.to_dict())
                    )
                ) # TODO: test
                await conn.commit()
        else:
