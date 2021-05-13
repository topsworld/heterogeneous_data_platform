from datetime import datetime
import logging.config
import time

import paho.mqtt.client as mqtt
from multiprocessing import Queue as msg_queue
from multiprocessing import Process

from sqlalchemy.sql.functions import user

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('mqttclient')

# https://docs.emqx.cn/broker/v4.3/development/resource.html

class mqtt_packet_item:
    """
    mqtt packet item
    """
    def __init__(self, sub_topic: str, recv_time: datetime, recv_address, recv_msg: str):
        """
        Structure initialization
        """
        self.sub_topic = sub_topic
        self.recv_time = recv_time
        self.recv_address = recv_address
        self.recv_msg = recv_msg

    def to_dict(self):
        """
        Convert structure to dictionary
        :return: mqtt packet item dict
        """
        return {
            "sub_topic": self.sub_topic,
            "recv_time": self.recv_time,
            "recv_address": self.recv_address,
            "recv_msg": self.recv_msg
        }



class service_mqttclient:
    def __init__(self, host:str, port:int, recv_queue: msg_queue, name:str, username="", password=""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.name = name
        self.recv_queue = recv_queue
        self.sub_topic_list = []
        self.connect_timeout = 60
        # ClientId不能重复，所以使用当前时间
        self.client_id = time.strftime('mqttclient-%Y%m%d%H%M%S', time.localtime(time.time()))
        self.mqttclient = mqtt.Client(self.client_id, protocol=mqtt.MQTTv311, transport="tcp")
        # Set user info
        if self.username != "" and self.password != "":
            self.mqttclient.username_pw_set(self.username, self.password)
        self.mqttclient.on_connect = self.on_connect
        self.mqttclient.on_message = self.on_message

    def connect(self, sub_topic_list: list, timeout=60):
        self.sub_topic_list = sub_topic_list
        self.connect_timeout = timeout
        self.mqttclient.connect(self.host, self.port, self.connect_timeout)
        logger.info("Start mqttclient, [name]: %s, [mqtt host]: %s:%s, [client id]: %s"
                    % (self.name, self.host, self.port, self.client_id))
        self.mqttclient.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT broker connected successfully, [name]: %s, [mqtt host]: %s:%s, [client id]: %s"
                    % (self.name, self.host, self.port, self.client_id))
        for topic in self.sub_topic_list:
            self.mqttclient.subscribe(topic)
            logger.info("MQTT topic subscribed successfully, [topic]: %s" % topic)
    
    def on_message(self, client, userdata, msg):
        logger.debug("MQTT receive message [\"%s\"] from topic [%s]" %
        (msg.payload.decode("utf-8"), msg.topic))
        # TODO: set MQTT recv_address
        recv_pkt = mqtt_packet_item(sub_topic=msg.topic, recv_time=datetime.now()
                ,recv_address="",recv_msg=msg.payload.decode("utf-8"))

        # Add msg to the queue
        if self.recv_queue is not None:
            self.recv_queue.put(recv_pkt.to_dict())


class process_mqttclient(Process):
    def __init__(self, host: str, port: int, sub_list: list
    , recv_queue: msg_queue, username="", password="", name="mqtt: no set"):
        super(process_mqttclient, self).__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.sub_list = sub_list
        self.recv_queue = recv_queue
        self.name = name
        self.obj_service_mqttclient = service_mqttclient(host=self.host, port=self.port
        , username=self.username, password=self.password, name=self.name
        , recv_queue=self.recv_queue)

    def run(self):
        self.obj_service_mqttclient.connect(self.sub_list)

    def stop(self):
        """
        Terminate the process, stop the MQTT service
        :return:
        """
        self.terminate()
        logger.info("Terminate mqttclient, [name]:%s, [sub_list]:%s" % (self.name, self.sub_list))


# obj_mqtt = process_mqttclient(host="broker.hivemq.com", port=1883
# , sub_list=["mqtt/sworld/test1", "mqtt/sworld/test2"]
# , name="MQTT Client-1", recv_queue=msg_queue())
# obj_mqtt.start()