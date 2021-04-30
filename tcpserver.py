# coding=utf-8
from configparser import Error
import datetime
import logging.config
from multiprocessing import Process, Queue
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen, ioloop


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('tcpserver')


"""
采用进程启动tcpserver，同时设置连接超时时间
目前只支持单个端口开启

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
    def __init__(self, recv_queue, port=8000, name = "no set"
        , timeout=recv_timeout, *args, **kwargs):
        super(service_tcpserver, self).__init__(*args, **kwargs)
        self.timeout = timeout
        self.devices = dict()
        self.name = name
        self.port = port
        self.recv_queue = recv_queue
        self.io_loop = ioloop.IOLoop.current()

    @gen.coroutine
    def report_devices(self):
        while True:
            logger.debug("[%s]: %s"%(self.name, self.devices))
            yield gen.sleep(5)
    
    def add_callback(self, func):
        self.io_loop.add_callback(func)

    def close_device(self, ipport):
        self.devices[ipport]["stream"].close()
        del self.devices[ipport]
        logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                    % (self.name, ipport, "User close", len(self.devices)))
    @gen.coroutine
    def handle_stream(self, stream, address):
        # Add connect to the dict
        ipport = address[0]+":"+str(address[1])
        self.devices[ipport] = {
            "stream": stream,
        }
        logger.info("[%s][%s]device connected, devices count: %s"
            % (self.name, ipport, len(self.devices)))

        # Listen to the message
        while True:
            try:
                data = yield gen.with_timeout(datetime.timedelta(seconds=self.timeout), 
                    stream.read_until(recv_end_str))
                yield stream.write(data)
                logger.debug("Receive data [%s] from %s" % (data, ipport))

                recv_pkt = tcp_packet_item()
                recv_pkt.server_port = self.port
                recv_pkt.recv_address = ipport
                recv_pkt.recv_msg = data

                # Add msg to tht queue
                self.recv_queue.put(recv_pkt)

            except Exception as err:
                # Close socket
                stream.close()
                # Del device from dict
                del self.devices[ipport]
                logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                    % (self.name, ipport,err.args[0] , len(self.devices)))
                break
                

    def get_devices(self):
        return self.devices

    @gen.coroutine
    def start_listen(self):
        # self.bind(self.port)
        # self.start(1) 

        self.listen(self.port)
        # Add callback func
        # self.add_callback(self.report_devices)
        logger.info("Start tcpserver, [name]:%s, [port]: %s" % (self.name, self.port))
        self.io_loop.start()


class process_tcpserver(Process):
    def __init__(self, port, recv_queue, name="no set"):
        super(process_tcpserver, self).__init__()
        self.port = port
        self.name = name
        self.recv_queue = recv_queue
        self.server = service_tcpserver(port=self.port,recv_queue=self.recv_queue, name=self.name)

    def run(self):
        try:
            self.server.start_listen()
        except Exception as e:
            logger.error(e.args)

    def stop(self):
        self.terminate()
        logger.info("Terminate tcpserver, [name]:%s, [port]:%s" % (self.name, self.port))



# if __name__ == '__main__':
#     q = Queue()
#     obj_process_tcpserver = process_tcpserver(port= 8001, recv_queue=q, name="P1")
#     obj_process_tcpserver.start()
    
    # time.sleep(5)

    # obj_process_tcpserver2.stop()



