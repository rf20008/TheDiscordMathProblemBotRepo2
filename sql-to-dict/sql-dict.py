import sqlite3
class CannotConnectException(Exception):
    "Raised when the SQLDICT can't connect"
    pass
class SQLChooser:
    def __init__(self, choosernameStr, chooserWanted):
        self.choosernamestr = choosernameStr
        self.chooserWanted = chooserWanted
class SQLColumn:
    "Used in SQLDict.__init__ for chooserNames and selects"
    def __init__(self, name, datatype="VARCHAR", can_be_null=True):
        self.name = name
        self.datatype = datatype
        self.can_be_null = can_be_null
    def __str__(self):
        e = self.name +"\t" + self.datatype
        if self.can_be_null:
            e += "\t" + "NOT NULL"
        return e



class SQLDict:
    "A custom class that represents a dictionary, but instead of being stored in RAM, it's stored in SQL"
    def __init__(self,database_name, name,tablename, chooserNames = [SQLColumn("_key")], selects = [SQLColumn("_value")]):
        self.database_name = database_name
        assert isinstance(chooserNames, list)
        assert isinstance(selects, list)
        self.chooserNames = chooserNames
        self.selects = selects
        self.name = name #each SqlDict
        #test connection to database, and initialize my table
        connection = self.connection
        query = f"CREATE TABLE {self.name} (" 
        for item in chooserNames:

        connection.execute(query) #initialize the table


    @property
    def connection(self):
        "Connect to my database"
        try:
            return sqlite3.connect(self.database_name)
        except Exception as e:
            raise CannotConnectException(f"Can't connect to database {self.database_name}, maybe you made a typo?") from e
    def get_item(self,choosers: list, wanted: list ):
        """Get the item with the exact choosers provided. Like dict[key]
        choosers is a list of SQLChoosers"""
        if len(choosers) != len(self.chooserNames):
            raise ValueError(f"{len(choosers)} choosers provided, expected {len(self.chooserNames)} choosers")
        for item in choosers.keys():
            if item not in self.chooserNames:
                raise ValueError(f"Did not expect chooser argument {item}, valid values are {', '.join(self.chooserNames)}")
        

        connection = self.connection #Establish connection
        query = "SELECT "
        for item in wanted:
            query += item
            query += ","


        