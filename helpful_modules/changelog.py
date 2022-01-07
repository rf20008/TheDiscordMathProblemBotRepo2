import json
import typing as t
import datetime
import io


class ChangeLogEntry:
    def __init__(self, *, patchNotes: t.List[str], old: str, new: str, date_released: str):
        self.patchNotes = '\n'.join[patchNotes]
        self.patch_notes = patchNotes
        self.old_version = old
        self.new_version = new
        try:
            self.date_released = datetime.datetime.fromtimestamp(date_released, tzinfo=datetime.timezone.utc)
        except TypeError:
            raise TypeError("Could not convert date_released to a datetime object")

    def to_dict(self) -> dict:
        return {
            'patch_notes': '\n'.split(self.patchNotes),
            'old': self.old_verison,
            'new': self.new_version,
            'date_released': self.date_released.totimestamp(tzinfo=datetime.timezone.utc)
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChangelogEntry":
        return cls(
            patchNotes=data['patch_notes'],
            old=data['old'],
            new=data['new'],
            date_released=data['date_released']
        )


class ChangeLogManager:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self._lock = asyncio.Lock()
        try:
            asyncio.run(self._open_file())
        except FileNotFoundError:
            raise ValueError("File not found.")
        self._changelogs: t.List[ChangelogEntry] = []

    async def _open_file(self, func: t.Callable[[io.TextIOWrapper, t.Any], t.Any] = lambda f: None, mode='r',
                         args: list = None, kwargs: dict = None) -> t.Any:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        async with self._lock:
            with open(self.file_name, mode) as file:
                return func(file, *args, *kwargs)  # type: ignore

    async def load_files(self):
        def func(file):
            entries = json.load(file)
            changelogs = []
            for entry in entries.values():
                changelogs.append(ChangelogEntry.from_dict(entry))
            return changelogs

        self._changelogs = await self._open_file(func=func, mode='r')
        return self._changelogs

    async def save_files(self, new: dict):
        def func(file: io.TextIOWrapper, data: dict):
            file.write(data)

        return await self._open_file(func=func, mode='w', args=[new])

    async def add_changelog(self, item: ChangelogEntry):
        data = await self.load_files()
        data.append(item.to_dict())

        def func(file, _data):
            file.write(_data)

        await self._open_file(func=func, mode='w', args=[data])

    @staticmethod
    async def create_changelog(self, data: dict):
        # TODO: finish
        try:
            return ChangelogEntry(*data)
        except BaseException as exc:
            raise RuntimeError("Could not convert it to a dictionary") from exc
