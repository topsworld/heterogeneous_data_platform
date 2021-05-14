from datetime import datetime
import logging
import logging.config
import time

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('main')

from sqlalchemy import Column, String, Integer, DateTime, Float

from multiprocessing import Queue as msg_queue
from tcpserver_socketserver import process_tcpserver
from udpserver_socketserver import process_udpserver
from mqttclient_pahomqtt import process_mqttclient
from database import process_database, CustomBase



##################################################################
# 用户数据自定义解析: start
# [注意]: 接受到的TCP和UDP每条数据需要以"\n"结尾!!! mqtt不需要
# 每一个开启端口或者订阅主题，都可以使用不同的处理句柄
# TODO: (1)解决不能存储中文bug
# TODO: (2)各服务状态实时更新，初始化失败循环
# TODO: (3)添加RPC调用，添加websocket支持
##################################################################
"""
下述代码为用户自定义数据模型，对应自定义数据库中的单独一张表。
在数据库初始化过程中，如果对应表不存在，会创建对应表。
如果修改了表结构，且数据库中存在旧表的映射，则需要删除旧表。

注意：可以创建多张表，结合自定义句柄，实现解析存储不同端口的数据至指定表。
"""
class sample_custom_data_table(CustomBase):
    """
    Sample: 用户自定义表模型，需要继承自database的CustomBase
    接受数据格式要求json字符串，示范如下：
    "{
        "acquisition_time":20210101120000,
        "node_unique_id": "FFFFFFFFFFFFFFFF",
        "para1": 10.00,
        "para2": 20.00,
        "para3": 30.00
    }
    "
    """
    # 存储表名，建议与类名一致
    __tablename__ = "sample_custom_data_table"
    
    # 下述为各个字段定义，详细定义规则见sqlalchemy官方手册：
    # https://www.sqlalchemy.org/
    id = Column(Integer, primary_key=True, autoincrement=True)
    recv_time = Column(DateTime, nullable=False)
    recv_address = Column(String(100), nullable=False)
    acquisition_time = Column(DateTime, nullable=False)
    node_unique_id = Column(String(16), nullable=False)
    para1 = Column(Float)
    para2 = Column(Float)
    para3 = Column(Float)

    def __init__(self, recv_time, recv_address, acquisition_time
    , node_unique_id, para1, para2, para3):
        """
        模型初始化，默认需要输入每个参数
        id: 自增标识
        recv_time: 服务器接受时间
        recv_address: 服务器接收端口号或者订阅主题
        node_unique_id: 节点唯一ID
        acquisition_time: 节点数据采集时间
        para1: 采集参数1
        para2: 采集参数2
        para3: 采集参数3
        """
        self.recv_time = recv_time
        self.recv_address = recv_address
        self.acquisition_time = acquisition_time
        self.node_unique_id = node_unique_id
        self.para1 = para1
        self.para2 = para2
        self.para3 = para3


"""
下述代码为用户自定义消息处理句柄，配置文件中添加一个端口或者一个订阅，可以提供用户
自定义消息处理句柄，从而对接受的消息进行解析及存储，如果不提供，表示不处理消息。
自定义消息处理句柄函数需要两个参数：
custom_db_helper: 封装的数据库接口，用于数据库操作，目前主要有两个函数可供使用
    add_data(obj_data): 以事务的形式向数据库添加一条数据
    execute_sql(sql_str): 执行原生sql语句
    more: 如果对sqlalchemy比较熟悉，可自行修改database.py
        从而实现更多的功能，如修改、删除等。
<obj|tcp, udp, mqtt>_msg: 消息字典，分tcp、udp、mqtt三种类型消息：
    tcp_msg: tcp数据字典，字典结构如下：
        {
            "server_port": "8000",  # 接受端口号，类型：str
            "recv_time": 20210101120000,    # 服务器接受时间，类型：datetime
            "recv_address": "127.0.0.1:12345",  # 节点发送ip地址，类型：str
            "recv_msg": "{...}\n"   # 消息内容，类型：str
        }
    udp_msg:tcp数据字典，字典结构如下：
        {
            "server_port": "8000",  # 接受端口号，类型：str
            "recv_time": 20210101120000,   # 服务器接受时间，类型：datetime
            "recv_address": "127.0.0.1:12345",  # 节点发送ip地址，类型：str
            "recv_msg": "{...}\n"      # 消息内容，类型：str
        }
    mqtt_msg:tcp数据字典，字典结构如下：
        {
            "sub_topic": "/nodedata/test",    # 订阅主题，类型：str
            "recv_time": 20210101120000,   # 服务器接受时间，类型：datetime
            "recv_address": "", # 预留
            "recv_msg": "{...}\n"      # 消息内容，类型：str
        }

"""

# 导入json库    
import json
def tcp_custom_handle(custom_db_helper ,tcp_msg: dict()):
    
    logger.debug("tcp_custom_handle msg: %s" % tcp_msg)
    try:
        """
        解析json数据，获取6个参数
        接受数据格式要求json字符串，示范如下：
        "{"acquisition_time":"20210101120000", "node_unique_id": "FFFFFFFFFFFFFFFF", "para1": 10.10, "para2": 20.20, "para3": 30.30}
        "
        """
        json_dict = json.loads(tcp_msg["recv_msg"])
        acquisition_time = datetime.strptime(json_dict["acquisition_time"], "%Y%m%d%H%M%S")
        node_unique_id = json_dict["node_unique_id"]
        para1 = json_dict["para1"]
        para2 = json_dict["para2"]
        para3 = json_dict["para3"]
        scdt_tcp = sample_custom_data_table(recv_time=tcp_msg["recv_time"]
        , recv_address=tcp_msg["recv_address"], acquisition_time=acquisition_time
        ,node_unique_id=node_unique_id, para1=para1, para2=para2, para3=para3)
        if custom_db_helper.add_data(scdt_tcp):
            logger.debug("TCP数据添加成功！")
    except Exception as err:
        logger.error(err.args)

    

def udp_custom_handle(custom_db_helper, udp_msg: dict()):
    logger.debug("udp_custom_handle msg: %s" % udp_msg)
    try:
        """
        解析json数据，获取6个参数
        接受数据格式要求json字符串，示范如下：
        "{"acquisition_time":"20210101120000", "node_unique_id": "FFFFFFFFFFFFFFFF", "para1": 10.10, "para2": 20.20, "para3": 30.30}
        "
        """
        json_dict = json.loads(udp_msg["recv_msg"])
        acquisition_time = datetime.strptime(json_dict["acquisition_time"], "%Y%m%d%H%M%S")
        node_unique_id = json_dict["node_unique_id"]
        para1 = json_dict["para1"]
        para2 = json_dict["para2"]
        para3 = json_dict["para3"]
        scdt_tcp = sample_custom_data_table(recv_time=udp_msg["recv_time"]
        , recv_address=udp_msg["recv_address"], acquisition_time=acquisition_time
        ,node_unique_id=node_unique_id, para1=para1, para2=para2, para3=para3)
        if custom_db_helper.add_data(scdt_tcp):
            logger.debug("UDP数据添加成功！")
    except Exception as err:
        logger.error(err.args)

def mqtt_custom_handle(custom_db_helper, mqtt_msg: dict()):
    logger.debug("mqtt_custom_handle msg: %s" % mqtt_msg)
    try:
        """
        解析json数据，获取6个参数
        接受数据格式要求json字符串，示范如下：
        "{"acquisition_time":"20210101120000", "node_unique_id": "FFFFFFFFFFFFFFFF", "para1": 10.10, "para2": 20.20, "para3": 30.30}
        "
        """
        json_dict = json.loads(mqtt_msg["recv_msg"])
        acquisition_time = datetime.strptime(json_dict["acquisition_time"], "%Y%m%d%H%M%S")
        node_unique_id = json_dict["node_unique_id"]
        para1 = json_dict["para1"]
        para2 = json_dict["para2"]
        para3 = json_dict["para3"]
        scdt_tcp = sample_custom_data_table(recv_time=mqtt_msg["recv_time"]
        , recv_address=mqtt_msg["recv_address"], acquisition_time=acquisition_time
        ,node_unique_id=node_unique_id, para1=para1, para2=para2, para3=para3)
        if custom_db_helper.add_data(scdt_tcp):
            logger.debug("MQTT数据添加成功！")
    except Exception as err:
        logger.error(err.args)

##################################################################
# 用户数据自定义解析: end
##################################################################

if __name__ == '__main__':
    # Process global queue
    tcp_msg_queue = msg_queue()
    udp_msg_queue = msg_queue()
    mqtt_msg_queue = msg_queue()

    server_config_dict = {
        # 数据库配置参数
        "database":{
            "status": 1,
            "host":"192.168.31.86", # 数据库host
            "port":3306,    # 数据库端口
            "username":"test",  # 数据库用户
            "password":"0031",  # 数据库密码
            "custom_db_name":"heterogeneous_data_db",   # 用户自定义数据存储数据库名称
            "raw_db_name":"heterogeneous_rawdata_db",   # 原始数据存储数据库名称
            "raw_db_obj":None,  # 不用管，原始数据库操作实体
            "custom_db_obj": None   # 不用管， 用户自定义数据库实体
        },
        # tcp配置参数
        "tcp":{
            "queue":tcp_msg_queue,
            "port":{
                # 开启端口列表，开启一个端口需要添加一个配置参数
                "8000":{
                    "name":"tcp_server: 8000",  # 服务名称
                    "status":1,
                    "instance":None,
                    "is_save_raw_data": True,   # 是否存储原始数据，True：存储，False：不存储
                    "custom_handle":tcp_custom_handle,  # 自定义操作句柄函数名
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
        # udp配置参数
        "udp":{
            "queue":udp_msg_queue,
            "port":{
                # 开启端口列表，结构同tcp
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
        # mqtt配置参数
        "mqtt":{
            "queue":mqtt_msg_queue,
            "host": "broker.hivemq.com",    # mqtt代理地址
            "port": 1883,   # mqtt代理端口
            "username": "", # mqtt代理用户名，不需要认证为空即可
            "password": "", # mqtt代理用户密码，不需要认证为空即可
            "name": "mqtt_client",  # 服务名称
            "sub":{
                # 订阅主题列表，需要订阅多个主题，按照规则添加即可
                "mqtt/sworld/test1":{
                    "status":1,
                    "is_save_raw_data": True,
                    "custom_handle":mqtt_custom_handle,
                    "table_info":{
                        "table_name":"",
                        "table_model":None,
                    }
                }
            }
        }
    }

    # Database processing processes, there are multiple data processing threads in the process.
    obj_process_db = process_database(server_dict = server_config_dict)
    obj_process_db.start()

    # TCP service process, each port service will open a process
    obj_process_tcpserver = process_tcpserver(tcp_server_info_dict= server_config_dict["tcp"])
    obj_process_tcpserver.start()

    # UDP service process, each port service will open a process
    obj_process_udpserver = process_udpserver(udp_server_info_dict= server_config_dict["udp"])
    obj_process_udpserver.start()
    
    # MQTT service process, only open a process
    obj_process_mqttclient = process_mqttclient(mqtt_server_info_dict=server_config_dict["mqtt"])
    obj_process_mqttclient.start()
    
    while True:
        # print(server_config_dict["tcp"]["port"]["8000"]["table_info"]["table_name"])
        # server_config_dict["tcp"]["port"]["8000"]["table_info"]["table_name"] = "1212"
        # print(server_config_dict["tcp"]["port"]["8000"]["table_info"]["table_name"])
        time.sleep(1)

