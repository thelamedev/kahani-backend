import sqlite3

dbConn: sqlite3.Connection


def connect_database(dbPath: str = "karela.sqlite"):
    global dbConn
    dbConn = sqlite3.connect(dbPath, check_same_thread=False, autocommit=True)


def close_database():
    global dbConn
    dbConn.commit()
    dbConn.close()
