#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from datetime import datetime
import logging

logger = logging.getLogger('database')

logger.debug("database")

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Table ,Float
from sqlalchemy.orm import relationship, sessionmaker,mapper
from sqlalchemy.ext.declarative import declarative_base


# Database connection string
con_db_str = "mysql+pymysql://{uid}:{pwd}@{host}/{dbname}?charset=utf8mb4"



class database_helper:
    def __init__(self, uid, pwd, host, dbname):
        # Create connection object
        self.engine = create_engine(con_db_str.format(
            uid=uid, pwd=pwd, host=host, dbname=dbname))
        self.metadata=MetaData(self.engine)
        # Create session
        self.DBsession=sessionmaker(bind=self.engine)
        # self.session=self.DBsession()
        self.tcp_table_dict = dict()
        self.udp_table_dict = dict()
        self.mqtt_table_dict = dict()
        # Create database
        # self.metadata.create_all(self.engine)

    def delete_all_raw_table():
        pass

    def tcp_create_table(self, port_list: list):
        for tcp_port in port_list:
            table_name = 'raw_tcp_data_'+str(tcp_port)
            Table(table_name, self.metadata,
                Column('id',Integer,autoincrement=True,primary_key=True),
                Column('recv_time',DateTime),
                Column('data',Text),
            )
            self.tcp_table_dict[str(tcp_port)] = {
                "table_name": table_name,
                "table_model": self.get_model(table_name)
            }
        
        self.metadata.create_all(self.engine)
        
        return self.tcp_table_dict
    
    def tcp_add_data(self, tcp_port, data):
        tcp_data = self.tcp_table_dict[str(tcp_port)]["table_model"](
            recv_time=datetime.now(), data=data)
        with dh.DBsession.begin() as session:
            session.add(tcp_data)
        

    def udp_create_table(self, port_list: list):
        for udp_port in port_list:
            table_name = 'raw_udp_data_'+str(udp_port)
            Table(table_name, self.metadata,
                Column('id',Integer,autoincrement=True,primary_key=True),
                Column('recv_time',DateTime),
                Column('data',Text),
            )
            self.udp_table_dict[str(udp_port)] = {
                "table_name": table_name,
                "table_model": self.get_model(table_name)
            }

        self.metadata.create_all(self.engine)

        return self.udp_table_dict

    def mqtt_create_table(self, sub_list: list):
        # TODO: Add sub topic verify
        # Verify code in here
        for mqtt_sub in sub_list:
            table_name = 'raw_mqtt_data_'+mqtt_sub
            model_table = Table(table_name, self.metadata,
                Column('id',Integer,autoincrement=True,primary_key=True),
                Column('recv_time',DateTime),
                Column('data',Text),
            )
            self.mqtt_table_dict[mqtt_sub] = {
                "table_name": table_name,
                "table_model": self.get_model(table_name)
            }

        self.metadata.create_all(self.engine)

        return self.mqtt_table_dict
    
    def get_model(self, table_name):
        DynamicBase = declarative_base(class_registry=dict())
        class custom_model(DynamicBase): 
            __tablename__ = table_name

            id = Column(Integer, primary_key=True, autoincrement=True) 
            recv_time = Column(DateTime) 
            data = Column(Text) 
        return custom_model 

        

# class tcp_data_helper:
#     def __init__():

dh = database_helper("test", "0031", "192.168.31.86:3306", "test")
dh.tcp_create_table([8001,8002])
dh.udp_create_table([8001,8002])
dh.mqtt_create_table(["test1", "test2"])
test = dh.udp_table_dict["8001"]["table_model"](recv_time=datetime.now(), data="tese")
with dh.DBsession.begin() as session:
    session.add(test)

print(dh.udp_table_dict)

# class MySQLHelper(object):
#     def __init__(self,uid,pwd,host):
#         #Create connection object
#         self.engine=create_engine(con_mysql_str.format(uid=uid,pwd=pwd,host=host,dbname=dbname))
#         self.metadata=MetaData(self.engine)
#         #Create session
#         self.DBsession=sessionmaker(bind=self.engine)
#         #self.session=self.DBsession()
#         #Generate a SqlORM base class
#         self.Base = declarative_base()

#         #Environment Data
#         self.tb_envi_data=Table('tb_envi_data',self.metadata,autoload=True)
#         #mapper
#         mapper(Envi_Data,self.tb_envi_data)

#         #RFID Data
#         self.tb_rfid_data=Table("tb_rfid_data",self.metadata,autoload=True)
#         #mapper
#         mapper(RFID_Data,self.tb_rfid_data)

#         #Scale Data
#         self.tb_scale_data=Table("tb_scale_data",self.metadata,autoload=True)
#         #mapper
#         mapper(Scale_Data,self.tb_scale_data)

#         #Infrare Data
#         self.tb_infrare_data=Table("tb_infrare_data",self.metadata,autoload=True)
#         #mapper
#         mapper(Infrare_Data,self.tb_infrare_data)


#     def add_envi_data_obj(self,obj):
#         session=self.DBsession()
#         session.add(obj)
#         session.commit()
#         session.close()
    
#     def add_envi_data(self,col_node_id,col_datetime,col_envi_temp,col_envi_humi,col_envi_light):
#         session=self.DBsession()
#         obj=Envi_Data()
#         obj.col_node_id=col_node_id
#         obj.col_datetime=col_datetime
#         obj.col_envi_temp=col_envi_temp
#         obj.col_envi_humi=col_envi_humi
#         obj.col_envi_light=col_envi_light
#         session.add(obj)
#         session.commit()
#         session.close()

#     def add_rfid_data_obj(self,obj):
#         session=self.DBsession()
#         session.add(obj)
#         session.commit()
#         session.close()
    
#     def add_rfid_data(self,col_node_id,col_rfid_id,col_datetime,col_rfid_val):
#         session=self.DBsession()
#         obj=RFID_Data()
#         obj.col_node_id=col_node_id
#         obj.col_rfid_id=col_rfid_id
#         obj.col_datetime=col_datetime
#         obj.col_rfid_val=col_rfid_val
#         session.add(obj)
#         session.commit()
#         session.close()
    
#     def add_scale_data_obj(self,obj):
#         session=self.DBsession()
#         session.add(obj)
#         session.commit()
#         session.close()

#     def add_scale_data(self,col_node_id,col_scale_id,col_datetime,col_scale_val):
#         session=self.DBsession()
#         obj=Scale_Data()
#         obj.col_node_id=col_node_id
#         obj.col_scale_id=col_scale_id
#         obj.col_datetime=col_datetime
#         obj.col_scale_val=col_scale_val
#         session.add(obj)
#         session.commit()
#         session.close()

#     def add_infrare_data_obj(self,obj):
#         session=self.DBsession()
#         session.add(obj)
#         session.commit()
#         session.close()

#     def add_infrare_data(self,col_node_id,col_infrare_id,col_datetime,col_temp_max,col_temp_min,col_temp_avrg,col_img_base64):
#         session=self.DBsession()
#         obj=Infrare_Data()
#         obj.col_node_id=col_node_id
#         obj.col_infrare_id=col_infrare_id
#         obj.col_datetime=col_datetime
#         obj.col_temp_max=col_temp_max
#         obj.col_temp_min=col_temp_min
#         obj.col_temp_avrg=col_temp_avrg
#         obj.col_img_base64=col_img_base64
#         session.add(obj)
#         session.commit()
#         session.close()


#     def show_envi_data(self):
#         result=self.engine.execute("select * from tb_envi_data")
#         print(result.fetchall())

#     # def session_close(self):
#     #     self.session.close()

#     # def test(self):
#     #     #od=tb_envi_data(col_datetime=datetime.now().strftime("%Y-%m-%d-%H:%M:%S"),col_envi_temp=10.12,col_envi_humi=20.23)

#     #     session.add(od)
#     #     session.commit()
#     #     session.close()
#     #     result=engine.execute("select * from tb_envi_data")
#     #     print(result.fetchall()) 





# class tcp_table_base:
#     id = Column(Integer, primary_key=True)
#     port = Column(Integer)
#     recv_time = Column(DateTime)
#     data = Column(String(64))
