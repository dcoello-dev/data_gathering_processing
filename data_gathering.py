import time
import logging
import json
import mysql.connector
from random import randrange

from app.notification_service import NotifyClient


def setup(cnx):
    logging.info("Database setup")
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(new_weight, (0, 0.2))
        cursor.execute(new_weight, (1, 0.6))
        cursor.execute(new_weight, (2, 0.1))
        cursor.execute(new_weight, (3, 0.1))
        cnx.commit()
        cursor.close()
    except mysql.connector.errors.IntegrityError:
        pass

def connect_to_database(conf):
    try:
        cnx = mysql.connector.connect(user=conf["user"],
                                      password=conf["password"],
                                      host=conf["host"],
                                      database=conf["database"],
                                      port=3306)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.info(
                "Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.info("Database does not exist")
        else:
            logging.info(err)
        raise err

def main():
    """Randomly add/update dates with securities"""
    try:
        id_date = 0
        # TODO: split this functionality in functions, study if makes sense to
        # add this use cases to DataHandler
        while True:
            cursor = cnx.cursor(dictionary=True)
            price = 100.0 if not id_date else 0.0
            cursor.execute(new_date, (id_date, price, 0, 1))

            logging.info("Date id: " + str(id_date) + " status: True")

            for i in range(0, 4):
                value = randrange(100) + 1  # dont allow to be 0.0
                # TODO: solve the insert/update with SQL instead exception handling in python
                try:
                    cursor.execute(
                        new_security, (float(value), 0.0, i, id_date))
                except mysql.connector.errors.IntegrityError:
                    cursor.execute(update_security, (float(value), i, id_date))

                logging.info("Weight id: " + str(i) + " price: " + str(value))

            cnx.commit()
            cursor.close()

            try:
                noty.notify("not")
            except Exception:
                # TODO: reduce the scope of the error handling
                pass

            id_date = randrange(10) + 1
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("shutdown")
        noty.disconnect()
        cnx.close()
        exit(0)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.DEBUG)

    with open("./conf/conf.json", "r") as f:
        DB_CONF = json.loads(f.read())

    new_date = ("INSERT INTO Date "
                "(timestamp, price, date_return, date_update) "
                "VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE "
                "date_update=VALUES(date_update)")

    new_weight = ("INSERT INTO Weight "
                  "(id, value) "
                  "VALUES (%s, %s)")

    # TODO: look how to ON DUPLICATE KEY UPDATE with composite primary key
    new_security = ("INSERT INTO Security "
                    "(price, security_return, fk_weight, fk_date) "
                    "VALUES (%s, %s, %s, %s)")

    update_security = "UPDATE Security SET price = %s "\
        "WHERE fk_weight = %s AND fk_date = %s"
    
    cnx = connect_to_database(DB_CONF)
    noty = NotifyClient("localhost", 25000)
    setup(cnx)
    main()

    
