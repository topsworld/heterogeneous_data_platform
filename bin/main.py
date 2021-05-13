import logging
import logging.config

logging.config.fileConfig('logging.conf')

from multiprocessing import Queue as msg_queue
from tcpserver_socketserver import process_tcpserver
from udpserver_socketserver import process_udpserver
from mqttclient_pahomqtt import process_mqttclient
from database import process_database
# import database
# import mqttclient
# import rpc
# import websocket

logger = logging.getLogger('main')


def tcp_custom_handle(custom_db_helper ,tcp_msg: dict()):
    logger.debug("tcp_custom_handle msg: %s" % tcp_msg)

def udp_custom_handle(custom_db_helper, udp_msg: dict()):
    logger.debug("udp_custom_handle msg: %s" % udp_msg)

def mqtt_custom_handle(custom_db_helper, mqtt_msg: dict()):
    logger.debug("mqtt_custom_handle msg: %s" % mqtt_msg)

if __name__ == '__main__':
    # Process global queue
    tcp_msg_queue = msg_queue()
    udp_msg_queue = msg_queue()
    mqtt_msg_queue = msg_queue()

    server_config_dict = {
        "database":{
            "status": 1,
            "raw_db_obj":None,
            "custom_db_obj": None
        },
        "tcp":{
            "queue":tcp_msg_queue,
            "port":{
                "8000":{
                    "name":"tcp_server: 8000",
                    "status":1,
                    "instance":None,
                    "is_save_raw_data": True,
                    "custom_handle":tcp_custom_handle,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    } 
                },
                "8001":{
                    "name":"tcp_server: 8001",
                    "status":1,
                    "instance":None,
                    "is_save_raw_data": True,
                    "custom_handle":tcp_custom_handle,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    } 
                }
            }
        },
        "udp":{
            "queue":udp_msg_queue,
            "port":{
                "8000":{
                    "name": "udp_server: 8000",
                    "status":1,
                    "instance": None,
                    "is_save_raw_data": True,
                    "custom_handle":udp_custom_handle,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    }
                }
            }
        },
        "mqtt":{
            "queue":mqtt_msg_queue,
            "sub":{
                "mqtt/sworld/test1":{
                    "status":1,
                    "is_save_raw_data": True,
                    "name": "name",
                    "custom_handle":mqtt_custom_handle,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    }
                }
            }
        }
    }

    obj_process_db = process_database(server_dict = server_config_dict)
    obj_process_db.start()

    obj_process_tcpserver = process_tcpserver(tcp_server_info_dict= server_config_dict["tcp"])
    obj_process_tcpserver.start()

    # obj_process_udpserver = process_udpserver(port=8000, recv_queue=udp_msg_queue, name="UDP Server-1")
    # obj_process_udpserver.start()
    # obj_process_udpserver2 = process_udpserver(port=8001, recv_queue=udp_msg_queue, name="UDP Server-2")
    # obj_process_udpserver2.start()
    # obj_process_udpserver3 = process_udpserver(port=8002, recv_queue=udp_msg_queue, name="UDP Server-3")
    # obj_process_udpserver3.start()

    # obj_mqtt = process_mqttclient(host="broker.hivemq.com", port=1883
    #                                 , sub_list=["mqtt/sworld/test1", "mqtt/sworld/test2"]
    #                                 , name="MQTT Client-1", recv_queue=mqtt_msg_queue)
    # obj_mqtt.start()

    # The main process receives and prints messages
    # while True:
    #     msg = global_queue.get()
    #     print(msg.to_dict())

