import json
import asyncio
import threading
import logging

from app.http_connection import thread_flask
from app.notification_service import notification_server

with open("./conf/conf.json", "r") as f:
    DB_CONF = json.loads(f.read())

loop = asyncio.get_event_loop()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        level=logging.DEBUG)
    try:
        loop.create_task(notification_server(loop, ('', 25000), DB_CONF))
        fl_th = threading.Thread(name='Web App', target=thread_flask, args=(DB_CONF,))
        fl_th.setDaemon(True)
        fl_th.start()
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Shutdown')
        exit(0)
