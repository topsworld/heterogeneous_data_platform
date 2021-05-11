import logging.config
import time

import paho.mqtt.client as mqtt

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('mqttclient')


def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.decode("utf-8"))
    logger.debug("MQTT receive message [\"%s\"] from %s %s" % (msg, client, userdata))


class service_mqttclient:
    def __init__(self, host, port, username, password, name="mqtt: no set"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.name = name
        self.sub_topic_list = []
        self.connect_timeout = 60
        # ClientId不能重复，所以使用当前时间
        self.client_id = time.strftime('mqttclient-%Y%m%d%H%M%S', time.localtime(time.time()))
        self.mqttclient = mqtt.Client(self.client_id, protocol=mqtt.MQTTv311, transport="tcp")
        # Set user info
        self.mqttclient.username_pw_set(self.username, self.password)
        self.mqttclient.on_connect = self.on_connect
        self.mqttclient.on_message = on_message

    def connect(self, sub_topic_list: list, timeout=60):
        self.sub_topic_list = sub_topic_list
        self.connect_timeout = timeout
        self.mqttclient.connect(self.host, self.port, self.connect_timeout)
        logger.info("Start mqttclient, [name]: %s, [mqtt host]: %s:%s, [client id]: %s"
                    % (self.name, self.host, self.port, self.client_id))
        self.mqttclient.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        logger.info("MQTT broker connected successfully, [name]: %s, [mqtt host]: %s:%s, [client id]: %s"
                    % (userdata, flags, rc, client))
        logger.info("MQTT broker connected successfully, [name]: %s, [mqtt host]: %s:%s, [client id]: %s"
                    % (self.name, self.host, self.port, self.client_id))
        for topic in self.sub_topic_list:
            self.mqttclient.subscribe(topic)
            logger.info("MQTT topic subscribed successfully, [topic]: %s" % topic)

        client.publish("test1", "你好 MQTT", qos=0, retain=False)  # 发布消息


obj_mqtt = service_mqttclient(host="www.sworld.top", port=1883
                              , username="sworld", password="0031", name="MQTT Client-1")
obj_mqtt.connect(["test1", "test2"])