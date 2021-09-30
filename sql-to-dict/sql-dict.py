import sqlite3
class CannotConnectException(Exception):
    "Raised when the SQLDICT can't connect"
class SqlDict:
    def __init__(self,database_name, name, chooserNames = ["_key"], selects = ["_value"]):
        self.database_name = database_name
        assert isinstance(chooserNames, list)
        assert isinstance(selects, list)
        self.chooserNames = chooserNames
        self.selects = selects
        self.name = name

    @property
    def connection(self):
        "Connect to my database"
        try:
            return sqlite3.connect(self.database_name)
        except Exception as e:
            raise CannotConnectException(f"Can't connect to database {self.database_name}, maybe you made a typo?") from e
    def get_item(self,**choosers):
        "Get the item with the exact choosers provided. Like dict[key]"
        if len(choosers) != len(self.chooserNames):
            raise ValueError(f"{len(choosers)} choosers provided, expected {len(self.chooserNames)} choosers")
        for item in choosers.keys():
            if item not in self.chooserNames:
                raise ValueError(f"Did not expect chooser argument {item}, valid values are {', '.join(self.chooserNames)}")
        

        connection = self.connection #Establish connection

        