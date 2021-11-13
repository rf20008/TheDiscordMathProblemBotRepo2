# Attribution to https://web.archive.org/web/20201112013549/https://stackoverflow.com/questions/3300464/how-can-i-get-dict-from-sqlite-query
# I did not have any part in writing the code
import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
