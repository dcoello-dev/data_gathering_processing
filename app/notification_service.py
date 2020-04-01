import asyncio
import logging
from socket import *

from app.data_handler import DataHandler
from app.data_processing import DataProcessing
from app.database_connection import DatabaseConnection

class NotifyClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connected = self.connect(host, port)

    def connect(self, host, port):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect((host, port))
            return True
        except ConnectionRefusedError:
            return False

    def notify(self, msg):
        if self.connected:
            self.sock.send(msg.encode())
        else:
            if self.connect(self.host, self.port):
                self.sock.send(msg.encode())
                self.connected=True
        
    def disconnect(self):
        if self.connected:
            self.sock.close()
        self.connected = False

async def notification_server(loop, address, db_conf):
    """
    Start notification server to receive notifications from 
    data gathering processes.

    args:
        address: tuple with host and port
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    sock.setblocking(False)
    datahandler = DataHandler(DatabaseConnection(db_conf))
    dataproc = DataProcessing()
    while True:
        client, addr = await loop.sock_accept(sock)
        logging.info('Connection from' + str(addr))
        loop.create_task(dicovery_handler(loop, client, datahandler, dataproc))


async def dicovery_handler(loop, client, datahandler, dataproc):
    """
    Handler triggered when notfication server receive 
    a notification.

    args:
        client: addres of the notification client
        datahandler: class to gather information from database
        dataproc: class to process the data
    """
    with client:
        while True:
            data = await loop.sock_recv(client, 10000)
            if not data:
                break
            # check which element/s are updated in the database
            data = datahandler.discovery()
            if data is not None:
                logging.info('Processing: ' + str(len(data["dates"])))
                # calculate and update data
                datahandler.update_elements(dataproc.process(data))
    logging.info('Connection closed')