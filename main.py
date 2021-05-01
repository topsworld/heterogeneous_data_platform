import logging
import logging.config
logging.config.fileConfig('logging.conf')

from multiprocessing import Queue

from tcpserver import process_tcpserver
import database
import udpserver
import mqttclient
import rpc
import websocket

logger = logging.getLogger('main')

if __name__ == '__main__':
    pass
