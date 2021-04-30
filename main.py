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
    q = Queue()
    obj_process_tcpserver = process_tcpserver(port= 8001, recv_queue=q, name="P1")
    obj_process_tcpserver.start()