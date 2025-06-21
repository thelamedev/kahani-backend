import logging

from shared.database import dbConn
from shared.queries import CREATE_USER_TABLE_QUERY

logger = logging.getLogger("database")


def seed_database():
    try:
        cur = dbConn.execute(CREATE_USER_TABLE_QUERY)
        cur.close()
        return None
    except Exception as e:
        logger.exception(e)
        return "Seeding Execution failed"
