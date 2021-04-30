# coding=utf-8
from configparser import Error
import datetime
import logging.config
from multiprocessing import Process
from os import name
from socket import IPPROTO_PIM
import time
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen, ioloop
import functools

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('tcpserver')


"""
采用进程启动tcpserver，同时设置连接超时时间，

"""

# 消息接收截止字符
recv_end_str = b"\n"
recv_timeout = 5

"""
TCP数据结构体
"""
class tcp_packet_item:
    def __init__(self) -> None:
        self.server_port = 8000
        self.recv_address = ""
        self.recv_msg = b""
    
    def to_dict(self):
        return {
            "server_port":self.server_port,
            "recv_address":self.recv_address,
            "recv_msg": self.recv_msg
        }

        
class service_tcpserver(TCPServer):
    def __init__(self, port=8000, name = "no set", timeout=recv_timeout, *args, **kwargs):
        super(service_tcpserver, self).__init__(*args, **kwargs)
        self.timeout = timeout
        self.devices = dict()
        self.name = name
        self.port = port
        self.io_loop = ioloop.IOLoop.current()

    @gen.coroutine
    def report_devices(self):
        while True:
            logger.debug(self.devices)
            yield gen.sleep(5)
    
    def add_callback(self, func):
        self.io_loop.add_callback(func)

    def close_device(self, ipport):
        self.devices[ipport]["stream"].close()
        del self.devices[ipport]
        logger.info("[%s] device disconnected ( %s ), devices count: %s"
                    % (ipport, "User close", len(self.devices)))
    @gen.coroutine
    def handle_stream(self, stream, address):
        # Add connect to the dict
        ipport = address[0]+":"+str(address[1])
        self.devices[ipport] = {
            "stream": stream,
        }
        logger.info("[%s] device connected, devices count: %s"
            % (ipport, len(self.devices)))

        # Listen to the message
        while True:
            try:
                data = yield gen.with_timeout(datetime.timedelta(seconds=self.timeout), 
                    stream.read_until(recv_end_str))
                logger.debug("Receive data [%s] from %s" % (data, ipport))

            except Exception as err:
                # Close socket
                stream.close()
                # Del device from dict
                del self.devices[ipport]
                logger.info("[%s] device disconnected ( %s ), devices count: %s"
                    % (ipport,err.args[0] , len(self.devices)))
                break
                

    def get_devices(self):
        return self.devices

    @gen.coroutine
    def start_listen(self):
        self.listen(self.port)
        # Add callback func
        # self.add_callback(self.report_devices)
        logger.info("Start tcpserver, [name]:%s, [port]: %s" % (self.name, self.port))
        self.io_loop.start()


class process_tcpserver(Process):
    def __init__(self, port, name="no set"):
        super(process_tcpserver, self).__init__()
        self.port = port
        self.name = name
        self.server = service_tcpserver(port=self.port, name=self.name)

    def run(self):
        try:
            self.server.start_listen()
        except Exception as e:
            logger.error(e.args)

    def stop(self):
        self.terminate()
        logger.info("Terminate tcpserver, [name]:%s, [port]:%s" % (self.name, self.port))

if __name__ == '__main__':
    obj_process_tcpserver = process_tcpserver(8000)
    obj_process_tcpserver.start()
    obj_process_tcpserver1 = process_tcpserver(8001)
    obj_process_tcpserver1.start()
    obj_process_tcpserver2 = process_tcpserver(8002)
    obj_process_tcpserver2.start()
    
    time.sleep(5)

    obj_process_tcpserver2.stop()



