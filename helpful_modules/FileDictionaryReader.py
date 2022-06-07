import asyncio
import json

import aiofiles

"""
This is used to read config.json, but it could also be used to read any JSON files and treat it like a dictionary, but not like a dictionary
because
1) __getitem__ has to be sync
2) This uses file I/O, instead of dictionaries
3) The file already needs to exist"""

__all__ = ("AsyncFileDict",)


class AsyncFileDict:
    """This is a class that uses a file and stores JSON. It also uses an internal dictionary"""

    def __init__(self, filename):
        self.filename = filename
        self.dict = {}
        asyncio.run(self.update_my_file())

    async def update_my_file(self):
        async with aiofiles.open(self.filename, "wb") as file:
            await file.write(bytes(json.dumps(self.dict), "utf-8"))
            return

    async def read_from_file(self) -> dict:
        async with aiofiles.open(self.filename, "r") as file:
            self._dict = json.loads(await file.read())
            return self.dict

    async def get_key(self, key):
        return (await self.read_from_file())[key]

    async def set_key(self, key, val):
        self.dict[key] = val
        await self.update_my_file()  # This could raise a JSONEncodeError

    async def del_key(self, key):
        del self.dict[key]
        await self.update_my_file()

    def __iter__(self):
        return self.dict.__iter__()

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.items()

    def items(self):
        return self.dict.items()
