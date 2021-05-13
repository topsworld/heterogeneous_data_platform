#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from datetime import datetime
from logging import log
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('database')

from multiprocessing.context import Process
from multiprocessing import Queue as msg_queue

from sqlalchemy.sql.expression import true
from sqlalchemy.sql.functions import func
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Table ,Float
from sqlalchemy.orm import relationship, sessionmaker,mapper, with_expression
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from sqlalchemy.ext.declarative import declarative_base

from threading import Thread
import time


Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)
    email = Column(String(64))

    def __init__(self, name, email):
        self.name = name
        self.email = email


class custom_database_helper:
    def __init__(self, uid, pwd, host
    , db_name: str, db_class="mysql"):
        self.con_db_str = ""
        if db_class == "mysql":
            self.con_db_str = "mysql+pymysql://{uid}:{pwd}@{host}"
        elif db_class == "sqlserver":
            pass
        elif db_class == "sqlite":
            pass
        self.db_name = db_name

        self.Base = Base

        if not database_exists(self.con_db_str.format(
            uid=uid, pwd=pwd, host=host)+"/"+self.db_name):
            # Create raw db
            self.engine = create_engine(self.con_db_str.format(
            uid=uid, pwd=pwd, host=host), pool_pre_ping=True)
            self.engine.execute("CREATE DATABASE "+self.db_name
                +" CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info("Custom database not exist, created database: %s" % self.db_name)

        self.engine = create_engine(self.con_db_str.format(
            uid=uid, pwd=pwd, host=host)+"/"+self.db_name+"?charset=utf8mb4"
            , pool_pre_ping=True)

        self.Base.metadata.create_all(self.engine)
        logger.info("Custom database initialize successfully.")

    def custom_handle_sample(self, msg):
        pass
        
    def delete_all_table(self):
        self.Base.metadata.drop_all(self.engine)





class raw_database_helper:
    def __init__(self, uid, pwd, host
    , tcp_port_list: list, udp_port_list: list, mqtt_sub_list: list
    , raw_db_name="heterogeneous_raw_data_db"
    , is_save=True, db_class="mysql"):
        # https://docs.sqlalchemy.org/en/14/dialects/index.html
        self.con_raw_db_str = ""
        if db_class == "mysql":
            self.con_raw_db_str = "mysql+pymysql://{uid}:{pwd}@{host}"
        elif db_class == "sqlserver":
            pass
        elif db_class == "sqlite":
            pass
        
        self.db_name = raw_db_name
        
        if not database_exists(self.con_raw_db_str.format(
            uid=uid, pwd=pwd, host=host)+"/"+self.db_name):
            # Create raw db
            self.engine = create_engine(self.con_raw_db_str.format(
            uid=uid, pwd=pwd, host=host), pool_pre_ping=True)
            self.engine.execute("CREATE DATABASE "+self.db_name
                +" CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info("Raw database not exist, created database: %s" % self.db_name)

        self.engine = create_engine(self.con_raw_db_str.format(
            uid=uid, pwd=pwd, host=host)+"/"+self.db_name+"?charset=utf8mb4"
            , pool_pre_ping=True)
        
        self.metadata=MetaData(self.engine)
        # Create session
        self.DBsession=sessionmaker(bind=self.engine)

        self.tcp_port_list = tcp_port_list
        self.udp_port_list = udp_port_list
        self.mqtt_sub_list = mqtt_sub_list

        self.tcp_table_dict = dict()
        self.udp_table_dict = dict()
        self.mqtt_table_dict = dict()

        # Create raw table
        self.tcp_create_table(self.tcp_port_list)
        self.udp_create_table(self.udp_port_list)
        self.mqtt_create_table(self.mqtt_sub_list)
        
        # Create database
        self.metadata.create_all(self.engine)
        logger.info("Raw database initialize successfully.")

    def tcp_create_table(self, port_list: list):
        for tcp_port in port_list:
            table_name = 'raw_tcp_data_'+str(tcp_port)
            Table(table_name, self.metadata,
                Column('id',Integer,autoincrement=True,primary_key=True),
                Column('recv_time',DateTime),
                Column("recv_address", String(30)),
                Column('recv_msg',Text),
            )
            self.tcp_table_dict[str(tcp_port)] = {
                "table_name": table_name,
                "table_model": self.get_model(table_name)
            }
        
        # self.metadata.create_all(self.engine)
        
        return self.tcp_table_dict
    
    def udp_create_table(self, port_list: list):
        for udp_port in port_list:
            table_name = 'raw_udp_data_'+str(udp_port)
            Table(table_name, self.metadata,
                Column('id',Integer,autoincrement=True,primary_key=True),
                Column('recv_time',DateTime),
                Column("recv_address", String(30)),
                Column('recv_msg',Text),
            )
            self.udp_table_dict[str(udp_port)] = {
                "table_name": table_name,
                "table_model": self.get_model(table_name)
            }

        # self.metadata.create_all(self.engine)

        return self.udp_table_dict

    def mqtt_create_table(self, sub_list: list):
        # TODO: Add sub topic verify
        # Verify code in here
        for mqtt_sub_raw in sub_list:
            mqtt_sub = mqtt_sub_raw# mqtt_sub_raw.replace('/','_').replace('#','').replace('*','')
            table_name = 'raw_mqtt_data_'+mqtt_sub
            model_table = Table(table_name, self.metadata,
                Column('id',Integer,autoincrement=True,primary_key=True),
                Column('recv_time',DateTime),
                Column("recv_address", String(30)),
                Column('recv_msg',Text),
            )
            self.mqtt_table_dict[mqtt_sub] = {
                "table_name": table_name,
                "table_model": self.get_model(table_name)
            }

        # self.metadata.create_all(self.engine)
        return self.mqtt_table_dict


    def get_model(self, table_name):
        DynamicBase = declarative_base(class_registry=dict())
        class custom_model(DynamicBase): 
            __tablename__ = table_name

            id = Column(Integer, primary_key=True, autoincrement=True) 
            recv_time = Column(DateTime) 
            recv_address = Column(String)
            recv_msg = Column(Text) 
        return custom_model 
    

    def execute_sql(self, sql_str):
        results = []
        with self.DBsession.begin() as session:
            results = session.execute(sql_str).fetchall()
        return results

    def add_data(self, obj_dict: dict(), recv_time: datetime, recv_address: str, recv_msg: str):
        obj_data = obj_dict["table_model"](
            recv_time=recv_time, recv_address=recv_address, recv_msg=recv_msg
        )
        with self.DBsession.begin() as session:
            session.add(obj_data)
        return True
    
    def tcp_add_data(self, tcp_port, recv_time: datetime, recv_address: str, recv_msg: str):
        return self.add_data(self.tcp_table_dict[str(tcp_port)]
        , recv_time=recv_time, recv_address=recv_address, recv_msg=recv_msg)

    def udp_add_data(self, udp_port, recv_time: datetime, recv_address: str, recv_msg: str):
        return self.add_data(self.udp_table_dict[str(udp_port)]
        , recv_time=recv_time, recv_address=recv_address, recv_msg=recv_msg)

    def mqtt_add_data(self, sub_topic, recv_time: datetime, recv_address: str, recv_msg: str):
        return self.add_data(self.mqtt_table_dict[sub_topic]
        , recv_time=recv_time, recv_address=recv_address, recv_msg=recv_msg)
    
    def delete_all_raw_table(self):
        self.metadata.drop_all(self.engine)
    

class thread_custom_handle(Thread):
    def __init__(self, custom_func):
        super(thread_custom_handle, self).__init__()
        self.custom_func = custom_func

    def run(self):
        try:
            self.custom_func()
        except Exception as err:
            logger.error(err.args)
        

class thread_tcp_handle(Thread):
    def __init__(self, server_tcp_dict: dict(), save_raw_data, db_helper):
        super(thread_tcp_handle, self).__init__()
        self.server_tcp_dict = server_tcp_dict
        self.save_tcp_raw_data = save_raw_data
        self.db_helper = db_helper

    def run(self):
        if self.server_tcp_dict["queue"] is None:
            logger.waring("TCP msg queue is None, [thread_tcp_handle] exited!")
            return
        while true:
            #try:
            tcp_msg = self.server_tcp_dict["queue"].get()
            if self.server_tcp_dict["port"][tcp_msg["server_port"]]["is_save_raw_data"] \
                and self.save_tcp_raw_data is not None:
                self.save_tcp_raw_data(tcp_port=tcp_msg["server_port"], recv_time=tcp_msg["recv_time"]
                , recv_address=tcp_msg["recv_address"], recv_msg= tcp_msg["recv_msg"])
            
            if self.server_tcp_dict["port"][tcp_msg["server_port"]]["custom_handle"] is not None:
                self.server_tcp_dict["port"][tcp_msg["server_port"]]["custom_handle"](self.db_helper, tcp_msg)
            # except Exception as err:
            #     logger.error(err.args)

        logger.info("TCP data handle thread exit!")

    def save_tcp_raw_data(self, tcp_port, recv_time: datetime, recv_address: str, recv_msg: str):
        pass


class thread_udp_handle(Thread):
    def __init__(self, server_udp_dict: dict(), save_raw_data, db_helper):
        super(thread_udp_handle, self).__init__()
        self.server_udp_dict = server_udp_dict
        self.save_udp_raw_data = save_raw_data
        self.db_helper = db_helper

    def run(self):
        if self.server_udp_dict["queue"] is None:
            logger.waring("UDP msg queue is None, [thread_udp_handle] exited!")
            return
        while True:
            try:
                udp_msg = self.server_udp_dict["queue"].get()
                if self.server_udp_dict["port"][udp_msg["server_port"]]["is_save_raw_data"]\
                    and self.save_udp_raw_data is not None:
                    self.save_udp_raw_data(udp_port=udp_msg["server_port"], recv_time=udp_msg["recv_time"]
                    , recv_address=udp_msg["recv_address"], recv_msg= udp_msg["recv_msg"])

                if self.server_udp_dict["port"][udp_msg["server_port"]]["custom_handle"] is not None:
                    self.server_udp_dict["port"][udp_msg["server_port"]]["custom_handle"](self.db_helper, udp_msg)

            except Exception as err:
                logger.error(err.args)

        logger.info("UDP data handle thread exit!")

        
    def save_udp_raw_data(self, udp_port, recv_time: datetime, recv_address: str, recv_msg: str):
        pass


class thread_mqtt_handle(Thread):
    def __init__(self, server_mqtt_dict: dict(), save_raw_data, db_helper):
        super(thread_mqtt_handle, self).__init__()
        self.server_mqtt_dict = server_mqtt_dict
        self.save_mqtt_raw_data = save_raw_data
        self.db_helper = db_helper
    
    def run(self):
        if self.server_mqtt_dict["queue"] is None:
            logger.waring("MQTT msg queue is None, [thread_mqtt_handle] exited!")
            return
        while True:
            try:
                mqtt_msg = self.server_mqtt_dict["queue"].get()
                if self.server_mqtt_dict["sub"][mqtt_msg["sub_topic"]]["is_save_raw_data"]\
                    and self.save_mqtt_raw_data is not None:
                    self.save_mqtt_raw_data(sub_topic=mqtt_msg["sub_topic"], recv_time=mqtt_msg["recv_time"]
                    , recv_address=mqtt_msg["recv_address"], recv_msg= mqtt_msg["recv_msg"])
                
                if self.server_mqtt_dict["sub"][mqtt_msg["sub_topic"]]["custom_handle"] is not None:
                    self.server_mqtt_dict["sub"][mqtt_msg["sub_topic"]]["custom_handle"](self.db_helper, mqtt_msg)

            except Exception as err:
                logger.error(err.args)
        
        logger.info("MQTT data handle thread exit!")
    
    def save_mqtt_raw_data(self, sub_topic, recv_time: datetime, recv_address: str, recv_msg: str):
        pass

class process_database(Process):
    def __init__(self, server_dict: dict()):
        super(process_database, self).__init__()
        self.server_dict = server_dict
        self.host = server_dict["database"]["host"]
        self.port = server_dict["database"]["port"]
        self.username = server_dict["database"]["username"]
        self.password = server_dict["database"]["password"]
        self.raw_db_name = server_dict["database"]["raw_db_name"]
        self.custom_db_name = server_dict["database"]["custom_db_name"]

        self.tcp_port_list = list(self.server_dict["tcp"]["port"].keys())
        self.udp_port_list = list(self.server_dict["udp"]["port"].keys())
        self.mqtt_sub_list = list(self.server_dict["mqtt"]["sub"].keys())

        self.raw_db_helper = raw_database_helper(uid=self.username,pwd=self.password
        , host=f"{self.host}:{self.port}", tcp_port_list= self.tcp_port_list
        , udp_port_list= self.udp_port_list, mqtt_sub_list= self.mqtt_sub_list,
        raw_db_name=self.raw_db_name)
        self.server_dict["database"]["raw_db_obj"] = self.raw_db_helper

        # 获取原始数据表
        for tcp_port in self.raw_db_helper.tcp_table_dict.keys():
            self.server_dict["tcp"]["port"][tcp_port]["table_info"] = self.raw_db_helper.tcp_table_dict[tcp_port]

        for udp_port in self.raw_db_helper.udp_table_dict.keys():
            self.server_dict["udp"]["port"][udp_port]["table_info"] = self.raw_db_helper.udp_table_dict[udp_port]

        for mqtt_sub in self.raw_db_helper.mqtt_table_dict.keys():
            self.server_dict["mqtt"]["sub"][mqtt_sub]["table_info"] = self.raw_db_helper.mqtt_table_dict[mqtt_sub]


        self.custom_db_helper = custom_database_helper(uid= self.username, pwd= self.password
        , host=f"{self.host}:{self.port}", db_name=self.custom_db_name)
        self.server_dict["database"]["custom_db_obj"] = self.custom_db_helper

        # TCP handle thread
        self.thread_tcp = thread_tcp_handle(server_tcp_dict=self.server_dict["tcp"]
        , save_raw_data= self.server_dict["database"]["raw_db_obj"].tcp_add_data
        , db_helper=self.custom_db_helper)

        # UDP handle thread
        self.thread_udp = thread_udp_handle(server_udp_dict=self.server_dict["udp"]
        , save_raw_data=self.server_dict["database"]["raw_db_obj"].udp_add_data
        , db_helper=self.custom_db_helper)

        # MQTT handle thread
        self.thread_mqtt = thread_mqtt_handle(server_mqtt_dict=self.server_dict["mqtt"]
        , save_raw_data=self.server_dict["database"]["raw_db_obj"].mqtt_add_data
        , db_helper=self.custom_db_helper)

    def run(self):    
        # Start TCP, UDP, MQTT message processing thread.
        self.thread_tcp.start()
        self.thread_udp.start()
        self.thread_mqtt.start()
        
        # Waiting for all threads to exit
        self.thread_tcp.join() 
        self.thread_udp.join()
        self.thread_mqtt.join()



# tcp_msg_queue = msg_queue()


# process_db_obj = process_database(server_dict = {
#     "database":{
#         "raw_db_obj":None,
#         "custom_db_obj": None
#     },
#     "tcp":{
#         "queue":tcp_msg_queue,
#         "port":{
#             "8000":{
#                 "status":1,
#                 "is_save_raw_data": True,
#                 "name": "name",
#                 "custom_handle":None,
#                 "table_info":{
#                     "table_name":"",
#                     "table_model":None,
#                 }
#             }
#         }
#     },
#     "udp":{
#         "queue":msg_queue(),
#         "port":{
#             "8000":{
#                 "status":1,
#                 "is_save_raw_data": True,
#                 "name": "name",
#                 "custom_handle":None,
#                 "table_info":{
#                     "table_name":"",
#                     "table_model":None,
#                 }
#             }
#         }
#     },
#     "mqtt":{
#         "queue":msg_queue(),
#         "sub":{
#             "test1":{
#                 "status":1,
#                 "is_save_raw_data": True,
#                 "name": "name",
#                 "custom_handle":None,
#                 "table_info":{
#                     "table_name":"",
#                     "table_model":None,
#                 }
#             }
#         }
#     }
# })

# process_db_obj.start()



# cdh = custom_database_helper("test", "0031", "192.168.31.86:3306")


# rdh = raw_database_helper("test", "0031", "192.168.31.86:3306",
#     [8000, 8001], [8000, 8001], ["test1", "test2"])

# rdh.tcp_add_data(8000, datetime.now(), "test: tcp data insert")
# rdh.tcp_add_data(8001, datetime.now(), "test: tcp data insert")
# rdh.udp_add_data(8000, datetime.now(), "test: udp data insert")
# rdh.udp_add_data(8001, datetime.now(), "test: udp data insert")
# rdh.mqtt_add_data("test1", datetime.now(), "test: mqtt data insert")
# rdh.mqtt_add_data("test2", datetime.now(), "test: mqtt data insert")
