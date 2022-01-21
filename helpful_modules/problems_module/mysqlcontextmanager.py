import contextlib
from mysql import connector as mysql_connector
import mysql


@contextlib.contextmanager
def mysql_connection(*args, **kwargs):
    connection = mysql_connector.connect(*args, **kwargs)
    yield connection
    connection.commit()
    connection.close()
