import mysql.connector
import contextlib


@contextlib.contextmanager
def mysql_connection(*args, **kwargs):
    connection = mysql.connector.connect(*args, **kwargs)
    yield connection
    connection.commit()
    connection.close()
