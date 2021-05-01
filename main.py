import logging
import logging.config
logging.config.fileConfig('logging.conf')

from multiprocessing import Queue as msg_queue
from tcpserver_socketserver import process_tcpserver
from udpserver_socketserver import process_udpserver
# import database
# import mqttclient
# import rpc
# import websocket

logger = logging.getLogger('main')


if __name__ == '__main__':
    # Process global queue
    global_queue = msg_queue()

    # Create three TCP services with port numbers 8000, 8001, and 8002.
    obj_process_tcpserver = process_tcpserver(port=8000, recv_queue=global_queue, name="TCP Server-1")
    obj_process_tcpserver.start()
    obj_process_tcpserver2 = process_tcpserver(port=8001, recv_queue=global_queue, name="TCP Server-2")
    obj_process_tcpserver2.start()
    obj_process_tcpserver3 = process_tcpserver(port=8002, recv_queue=global_queue, name="TCP Server-3")
    obj_process_tcpserver3.start()

    # # Process global queue
    # global_queue = msg_queue()

    # Create three TCP services with port numbers 8000, 8001, and 8002.
    obj_process_udpserver = process_udpserver(port=8000, recv_queue=global_queue, name="UDP Server-1")
    obj_process_udpserver.start()
    obj_process_udpserver2 = process_udpserver(port=8001, recv_queue=global_queue, name="UDP Server-2")
    obj_process_udpserver2.start()
    obj_process_udpserver3 = process_udpserver(port=8002, recv_queue=global_queue, name="UDP Server-3")
    obj_process_udpserver3.start()

    # The main process receives and prints messages
    while True:
        msg = global_queue.get()
        print(msg.to_dict())

