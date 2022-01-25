import contextlib

import mysql.connector
import mysql.connector.pooling

# Licensed under GPLv3 (or later)


@contextlib.contextmanager
def mysql_connection(*args, **kwargs) -> None:
    """A custom with statement to connect to a MySQL database.
    This makes connecting to MYSQL possible within a context wrapper. This is a wrapper around MySQL
    You must take care to provide the correct arguments and keyword arguments, which will be directly passed to the mysql.connector.connect() method.
    If an exception happens in the with statement, the connection will commit and close and then the exception will be raised.
    Otherwise, the connection will commit and close. It will not return anything. :-)
    This function is licensed under GPLv3."""
    connection = mysql.connector.connect(*args, **kwargs)  # Connect
    try:
        yield connection
    except:
        print(
            "An exception occured!. After closing resources, the exception will be raised"
        )
        connection.commit()
        connection.close()
        raise
    finally:
        connection.commit()
        connection.close()

pool = pooling.MySQLConnectionPool()
@contextlib.contextmanager
def mysql_connection_with_a_pool(*args, **kwargs):

