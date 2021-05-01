# coding=utf-8
import datetime
import logging.config
from multiprocessing import Process, Queue
from threading import Thread
from typing import Tuple

from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory, connectionDone
from twisted.internet import reactor
from twisted.python import failure

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('tcpserver')

"""
采用进程启动tcpserver，同时设置连接超时时间
支持多端口开启调用
"""

"""
Message reception cutoff character
"""
recv_end_str = b"\n"
"""
The maximum interval of no data transmission,
the connection will be disconnected when timeout
"""
recv_timeout = 5


class tcp_packet_item:
    """
    Tcp packet item
    """

    def __init__(self) -> None:
        """
        Structure initialization
        """
        self.server_port = 8000
        self.recv_address = ""
        self.recv_msg = b""

    def to_dict(self):
        """
        Convert structure to dictionary
        :return: tcp packet item dict
        """
        return {
            "server_port": self.server_port,
            "recv_address": self.recv_address,
            "recv_msg": self.recv_msg
        }


class tcpserver_protocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.devices = factory.devices
        self.recv_queue = factory.recv_queue
        self.name = factory.name

    def connectionMade(self):
        # Add connect to the dict
        ip_port = self.transport.getPeer().host+":"+str(self.transport.getPeer().port)
        self.devices[ip_port] = {
            "stream": self.transport,
        }
        logger.info("[%s][%s]device connected, devices count: %s"
                    % (self.name, ip_port, len(self.devices)))

    def connectionLost(self, reason: failure.Failure = connectionDone):
        ip_port = self.transport.getPeer().host+":"+str(self.transport.getPeer().port)
        # Del device from dict
        del self.devices[ip_port]
        logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                    % (self.name, ip_port, reason, len(self.devices)))
        self.transport.loseConnection()

    def dataReceived(self, data):
        ip_port = self.transport.getPeer().host+":"+str(self.transport.getPeer().port)
        logger.debug("Receive data [%s] from %s" % (data, ip_port))

        recv_pkt = tcp_packet_item()
        recv_pkt.server_port = self.port
        recv_pkt.recv_address = ip_port
        recv_pkt.recv_msg = data

        # Add msg to tht queue
        if self.recv_queue is not None:
            self.recv_queue.put(recv_pkt)


class service_tcpserver(Factory):
    def __init__(self, recv_queue=None, port=8000, name="no set"
                 , timeout=recv_timeout):
        """
        Tcp server init
        :param recv_queue: Receive queue
        :param port: TCP service open port
        :param name: TCP service name, default: no set
        :param timeout: The maximum interval of no data transmission,
                        the connection will be disconnected when timeout
        :param args: Inherited parameters
        :param kwargs: Inherited parameters
        """
        self.timeout = timeout
        self.devices = dict()
        self.name = name
        self.port = port
        self.recv_queue = recv_queue
        # Define listen port
        self.endpoint = TCP4ServerEndpoint(reactor, self.port)

    def buildProtocol(self, addr: Tuple[str, int]):
        return tcpserver_protocol(self)

    def close_device(self, ip_port):
        """
        Disconnect the specified device
        :param ip_port: Connection IP address and port number,
                        such as 192.168.1.1:12345
        :return: None
        """
        self.devices[ip_port]["stream"].close()
        del self.devices[ip_port]
        logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                    % (self.name, ip_port, "User close", len(self.devices)))

    def get_devices(self):
        """
        Get device list
        :return: Devices list
        """
        return self.devices

    def start_listen(self):
        """
        Start tcp server
        :return: None
        """
        # 指定端口绑定子类
        self.endpoint.listen(self)
        logger.info("Start tcpserver, [name]:%s, [port]: %s" % (self.name, self.port))
        # 启动服务
        reactor.run()

# f = Factory()
# f.protocol = service_tcpserver
# reactor.listenTCP(8000, f)
# reactor.run()


# obj_process_tcpserver = service_tcpserver(port=8000)
# Thread(target=obj_process_tcpserver.start_listen(), args=(False,)).start()
# obj_process_tcpserver1 = service_tcpserver(port=8001)
# Thread(target=obj_process_tcpserver1.start_listen(), args=(False,)).start()
# obj_process_tcpserver2 = service_tcpserver(port=8002)
# Thread(target=obj_process_tcpserver2.start_listen(), args=(False,)).start()

class process_tcpserver(Process):
    """
    TCP service process, Inherited from multiprocessing Process
    """

    def __init__(self, port, recv_queue, name="no set"):
        """
        TCP service process
        :param port: TCP service open port, such as 12345
        :param recv_queue: TCP service receive queue
                (Used for process data interaction)
                from multiprocessing import Queue
        :param name: TCP Service name, default: no set
        """
        super(process_tcpserver, self).__init__()
        self.port = port
        self.name = name
        self.recv_queue = recv_queue
        self.server = service_tcpserver(recv_queue=self.recv_queue, port=self
                                        .port, name=self.name)

    def run(self):
        """
        Process started, start tcp service
        :return: None
        """
        try:
            self.server.start_listen()
        except Exception as e:
            logger.error(e.args)

    def get_devices(self):
        """
        Get device list
        :return: Devices list
        """
        return self.server.devices

    def is_device_exist(self, ip_port):
        return self.server.devices.has_key(ip_port)

    def devices_count(self):
        return len(self.server.devices)

    def stop(self):
        """
        Terminate the process, stop the TCP service
        :return:
        """
        # self.ab
        logger.info("Terminate tcpserver, [name]:%s, [port]:%s" % (self.name, self.port))


"""
Example
"""
# if __name__ == '__main__':
#     # Process global queue
#     global_queue = Queue()
#
#     # Create three TCP services with port numbers 8000, 8001, and 8002.
#     obj_process_tcpserver = process_tcpserver(port=8000, recv_queue=global_queue, name="TCP Server-1")
#     obj_process_tcpserver.start()
#     obj_process_tcpserver2 = process_tcpserver(port=8001, recv_queue=global_queue, name="TCP Server-2")
#     obj_process_tcpserver2.start()
#     obj_process_tcpserver3 = process_tcpserver(port=8002, recv_queue=global_queue, name="TCP Server-3")
#     obj_process_tcpserver3.start()
#
#     # The main process receives and prints messages
#     while True:
#         msg = global_queue.get()
#         print(msg.to_dict())
#
#     gen.sleep(5)
#     # process stop
#     obj_process_tcpserver2.stop()