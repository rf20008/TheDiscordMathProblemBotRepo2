import sqlite3
class CannotConnectException(Exception):
    "Raised when the SQLDICT can't connect"
    pass
class SQLChooser:
    def __init__(self, name, value_wanted):
        self.name = name
        self.value_wanted = value_wanted
class SQLColumn:
    "Used in SQLDict.__init__ for chooserNames and selects"
    def __init__(self, name, datatype="VARCHAR", can_be_null=True):
        self.name = name
        self.datatype = datatype
        self.can_be_null = can_be_null
    def __str__(self):
        e = self.name +"\t" + self.datatype
        if not self.can_be_null:
            e += "\t" + "NOT NULL"
        return e



class SQLDict:
    "A custom class that represents a dictionary, but instead of being stored in RAM, it's stored in SQL"
    def __init__(self,database_name, name,tablename, choosers = [SQLColumn("_key")], selects = [SQLColumn("_value")]):
        self.database_name = database_name
        assert isinstance(choosers, list)
        assert isinstance(selects, list)
        self.choosers = choosers
        self.selects = selects
        self.name = name #each SqlDict
        #test connection to database, and initialize my table
        connection = self.connection
        query = f"CREATE TABLE {self.name} (" 
        for item in range(len(choosers)):
            query += str(choosers[item])
            if item != len(choosers) - 1:
                query += ","
            query += "\n"
        query += ");"

        connection.execute(query) #initialize the table

    def __generate_query_str__(self,middle,wanted):

        query = "SELECT "
        for item in range(len(wanted)):
            query += wanted[item]
            if item != len(wanted) - 1:
                query += ", "
        query += f" {middle} FROM {self.name}"
        return query
        

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
            if item not in self.choosers:
                raise ValueError(f"Did not expect chooser argument {item.name}, valid values are {', '.join([item.name for item in self.chooserNames])}")
        
        for item in wanted:
            if item not in self.selects:
                raise ValueError(f"Did not expect wanted argument {item}, valid values are {', '.join(self.selects)}")
        
        connection = self.connection #Establish connection
        q = ""
        for item in range(len(choosers)):
            q += f"{choosers[item].name} = {choosers[item].value_wanted}"
            if item != len(choosers) - 1:
                q += "AND"
        q += f" FROM {self.name}"
        self.connection.execute(self.__generate_query_str__(middle = q, wanted = wanted))
    def set_item(self,choosers,selects):
        for item

            

        