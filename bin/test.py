from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Table ,Float
from sqlalchemy.orm import sessionmaker

con_mysql_str="mysql+pymysql://{uid}:{pwd}@{host}/{dbname}?charset=utf8mb4"
engine=create_engine(con_mysql_str.format(uid="test",pwd="0031",host="192.168.31.86:3306",dbname="test"))
metadata=MetaData(engine)
#Create session
DBsession=sessionmaker(bind=engine)
#self.session=self.DBsession()
#Generate a SqlORM base class
Base = declarative_base()
metaData = MetaData(engine) # 创建表
for i in [8000,8001]:
    Table('raw_tcp_data_'+str(i),metaData,
        Column('id',Integer,autoincrement=True,primary_key=True),
        Column('name',String(50)),
        Column('age',Integer),
        Column('sex',String(10)),
    )
    
metaData.create_all(engine)


def get_model(suffix):
    DynamicBase = declarative_base(class_registry=dict())

    class MyModel(DynamicBase): 
        __tablename__ = 'table_{suffix}'.format(suffix=suffix) 

        id = Column(Integer, primary_key=True) 
        name = Column(String) 
        age = Column(String) 
        sex = Column(String) 
    return MyModel 


# from socketserver import BaseRequestHandler, UDPServer
# import time

# class TimeHandler(BaseRequestHandler):
#     def handle(self):
#         print('Got connection from', self.client_address)
#         # Get message and client socket
#         msg, sock = self.request
#         resp = time.ctime()
#         sock.sendto(resp.encode('ascii'), self.client_address)

# if __name__ == '__main__':
#     serv = UDPServer(('localhost', 8000), TimeHandler)
#     serv.serve_forever()