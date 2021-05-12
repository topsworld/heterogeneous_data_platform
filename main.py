import logging
import logging.config
logging.config.fileConfig('logging.conf')

from multiprocessing import Queue as msg_queue
from tcpserver_socketserver import process_tcpserver
from udpserver_socketserver import process_udpserver
from database import process_database
# import database
# import mqttclient
# import rpc
# import websocket

logger = logging.getLogger('main')


def tcp_custom_handle(custom_db_helper ,tcp_msg):
    logger.debug("custom_db_helper url: %s" % custom_db_helper.con_raw_db_str)
    logger.debug("tcp_custom_handle msg: %s" % tcp_msg)

if __name__ == '__main__':
    # Process global queue
    tcp_msg_queue = msg_queue()


    process_db_obj = process_database(server_dict = {
        "database":{
            "raw_db_obj":None,
            "custom_db_obj": None
        },
        "tcp":{
            "queue":tcp_msg_queue,
            "port":{
                "8000":{
                    "status":1,
                    "is_save_raw_data": True,
                    "name": "name",
                    "custom_handle":tcp_custom_handle,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    }
                }
            }
        },
        "udp":{
            "queue":msg_queue(),
            "port":{
                "8000":{
                    "status":1,
                    "is_save_raw_data": True,
                    "name": "name",
                    "custom_handle":None,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    }
                }
            }
        },
        "mqtt":{
            "queue":msg_queue(),
            "sub":{
                "test1":{
                    "status":1,
                    "is_save_raw_data": True,
                    "name": "name",
                    "custom_handle":None,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    }
                }
            }
        }
    })

    process_db_obj.start()

    # Create three TCP services with port numbers 8000, 8001, and 8002.
    obj_process_tcpserver = process_tcpserver(port=8000, recv_queue=tcp_msg_queue, name="TCP Server-1")
    obj_process_tcpserver.start()
    obj_process_tcpserver2 = process_tcpserver(port=8001, recv_queue=tcp_msg_queue, name="TCP Server-2")
    obj_process_tcpserver2.start()
    obj_process_tcpserver3 = process_tcpserver(port=8002, recv_queue=tcp_msg_queue, name="TCP Server-3")
    obj_process_tcpserver3.start()

    # # Process global queue
    # global_queue = msg_queue()

    # Create three TCP services with port numbers 8000, 8001, and 8002.
    # obj_process_udpserver = process_udpserver(port=8000, recv_queue=global_queue, name="UDP Server-1")
    # obj_process_udpserver.start()
    # obj_process_udpserver2 = process_udpserver(port=8001, recv_queue=global_queue, name="UDP Server-2")
    # obj_process_udpserver2.start()
    # obj_process_udpserver3 = process_udpserver(port=8002, recv_queue=global_queue, name="UDP Server-3")
    # obj_process_udpserver3.start()

    # The main process receives and prints messages
    # while True:
    #     msg = global_queue.get()
    #     print(msg.to_dict())

