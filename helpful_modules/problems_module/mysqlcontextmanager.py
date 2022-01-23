import contextlib

import mysql
from mysql import connector as mysql_connector


@contextlib.contextmanager
def mysql_connection(*args, **kwargs):
    connection = mysql_connector.connect(*args, **kwargs)
    yield connection
    connection.commit()
    connection.close()
