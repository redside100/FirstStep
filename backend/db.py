import logging
import time

import psycopg2

connection = None


logger = logging.Logger("db")
def init_db(host, port, user, password, database):
    global connection
    for _ in range(10):
        try:
            connection = psycopg2.connect(user=user, password=password, host=host, port=port, database=database)
            break
        except psycopg2.OperationalError:
            logger.warning("Could not connect to postgres, retrying in 1 second")
            time.sleep(1)

    if not connection:
        logger.error("Couldn't connect to postgres (within 10 seconds)")
    else:
        logger.info("Connected to postgres.")

