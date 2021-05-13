# coding=utf-8
from datetime import datetime
import logging.config
from multiprocessing import Process
from multiprocessing import Queue as msg_queue
from socketserver import ThreadingTCPServer, StreamRequestHandler

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('tcpserver')

"""
采用进程启动tcpserver，同时设置连接超时时间
支持多端口开启调用
"""

"""
[trash] Message reception cutoff character
"""
recv_end_str = b"\n"
"""
The maximum interval of no data transmission,
the connection will be disconnected when timeout
"""
recv_timeout = 5
"""
Maximum number of connected nodes for the service, default: 1000.
TODO: Dynamically adjust according to the current resources of the system
"""
max_devices_count = 1000


class tcp_packet_item:
    """
    Tcp packet item
    """
    def __init__(self, server_port: int, recv_time: datetime, recv_address: str, recv_msg: str) -> None:
        """
        Structure initialization
        """
        self.server_port = server_port
        self.recv_time = recv_time
        self.recv_address = recv_address
        self.recv_msg = recv_msg

    def to_dict(self):
        """
        Convert structure to dictionary
        :return: tcp packet item dict
        """
        return {
            "server_port": str(self.server_port),
            "recv_time": self.recv_time,
            "recv_address": self.recv_address,
            "recv_msg": self.recv_msg
        }


class service_tcpserver(StreamRequestHandler):
    # Optional settings (defaults shown)
    # Timeout on all socket operations
    timeout = recv_timeout
    # Read buffer size
    rbufsize = -1
    # Write buffer size
    wbufsize = 0
    # Sets TCP_NODELAY socket option
    disable_nagle_algorithm = False
    devices = dict()
    name: str
    port: int
    max_count: int
    recv_queue: msg_queue
    tcpserver: ThreadingTCPServer
    # devices_count = 0

    def listen(self, recv_queue: msg_queue, port: int, name: str, max_count=max_devices_count):
        """
        [Important]
        Start tcp server
        TCP service init,  Must be called before the service starts.
        :param recv_queue: Receive message queue
        :param port: Tcp server open port
        :param name: Tcp server name
        :param max_count: Max connect device of tcp server
        :return: None
        """
        self.recv_queue = recv_queue
        self.port = port
        self.name = name
        self.max_count = max_count

        self.tcpserver = ThreadingTCPServer(('', self.port), self)
        logger.info("Start tcpserver, [name]: %s, [port]: %s" % (self.name, self.port))
        self.tcpserver.serve_forever()

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

    def handle(self):
        """
        Socket connection establishment and data reception processing function
        :return: None
        """
        # Add connect to the dict
        ip_port = f"{self.client_address[0]}:{self.client_address[1]}"
        # Determine if the connection has reached the upper limit
        if len(self.devices) >= self.max_count:
            # self.wfile.write(b"Connection reached the upper limit\r\n")
            logger.warning("[%s][%s]Connection reached the upper limit, devices count: %s"
                           % (self.name, ip_port, len(self.devices)))
            self.finish()
            return
        self.devices[ip_port] = {
            "stream": self,
        }
        logger.info("[%s][%s]device connected, devices count: %s"
                    % (self.name, ip_port, len(self.devices)))
        try:
            for line in self.rfile:
                logger.debug("TCP receive data [%s] from %s" % (line, ip_port))
                recv_pkt = tcp_packet_item(server_port=self.port, recv_time=datetime.now()
                , recv_address=ip_port, recv_msg=line)

                # Add msg to the queue
                if self.recv_queue is not None:
                    self.recv_queue.put(recv_pkt.to_dict())
            raise Exception("Disconnect from client")
        except Exception as err:
            # Close socket
            self.finish()
            # Del device from dict
            del self.devices[ip_port]
            logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                        % (self.name, ip_port, err.args[0], len(self.devices)))

    def get_devices(self):
        """
        Get device list
        :return: Devices list
        """
        return self.devices

    def close_device(self, ip_port):
        """
        Disconnect the specified device
        :param ip_port: Connection IP address and port number,
                        such as 192.168.1.1:12345
        :return: None
        """
        self.devices[ip_port]["stream"].finish()
        del self.devices[ip_port]
        logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                    % (self.name, ip_port, "User close", len(self.devices)))


# obj_service_tcpserver = service_tcpserver
# obj_service_tcpserver.init(obj_service_tcpserver, None, 8000, "no set")
# service_tcpserver.start_listen(service_tcpserver)


# serv = ThreadingTCPServer(('', 8000), service_tcpserver)
# serv.serve_forever()


class process_tcpserver_single_port(Process):
    """
    TCP service process, Inherited from multiprocessing Process
    """

    def __init__(self, port: int, recv_queue: msg_queue, name="tcp: no set"):
        """
        TCP service process
        :param port: TCP service open port, such as 12345
        :param recv_queue: TCP service receive queue
                (Used for process data interaction)
                from multiprocessing import Queue
        :param name: TCP Service name, default: no set
        """
        super(process_tcpserver_single_port, self).__init__()
        self.port = port
        self.name = name
        self.recv_queue = recv_queue
        self.obj_service_tcpserver = service_tcpserver

    def run(self):
        """
        Process started, start tcp service
        :return: None
        """
        try:
            self.obj_service_tcpserver.listen(self.obj_service_tcpserver
                                              , self.recv_queue, self.port, self.name)
        except Exception as e:
            logger.error(e.args)

    def get_devices(self):
        """
        Get device list
        :return: Devices list
        """
        return self.obj_service_tcpserver.devices

    def is_device_exist(self, ip_port):
        return self.obj_service_tcpserver.devices.has_key(ip_port)

    def devices_count(self):
        return len(self.obj_service_tcpserver.devices)

    def stop(self):
        """
        Terminate the process, stop the TCP service
        :return:
        """
        self.terminate()
        logger.info("Terminate tcpserver, [name]:%s, [port]:%s" % (self.name, self.port))



class process_tcpserver:
    def __init__(self, tcp_server_info_dict: dict()):
        self.tcp_server_info_dict = tcp_server_info_dict
        for port_str, info in self.tcp_server_info_dict["port"].items():
            info["instance"] = process_tcpserver_single_port(
                port=int(port_str), recv_queue=self.tcp_server_info_dict["queue"]
                , name=info["name"])

    def start(self):
        for port_str, info in self.tcp_server_info_dict["port"].items():
            info["instance"].start()




"""
Example
"""
# if __name__ == '__main__':
#     # Process global queue
#     global_queue = msg_queue()

#     # Create three TCP services with port numbers 8000, 8001, and 8002.
#     obj_process_tcpserver1 = process_tcpserver(port=8000, recv_queue=global_queue, name="TCP Server-1")
#     obj_process_tcpserver1.start()
#     obj_process_tcpserver2 = process_tcpserver(port=8001, recv_queue=global_queue, name="TCP Server-2")
#     obj_process_tcpserver2.start()
#     obj_process_tcpserver3 = process_tcpserver(port=8002, recv_queue=global_queue, name="TCP Server-3")
#     obj_process_tcpserver3.start()
#     obj_process_tcpserver4 = process_tcpserver(port=8003, recv_queue=global_queue, name="TCP Server-4")
#     obj_process_tcpserver4.start()
#     obj_process_tcpserver5 = process_tcpserver(port=8004, recv_queue=global_queue, name="TCP Server-5")
#     obj_process_tcpserver5.start()
#     obj_process_tcpserver6 = process_tcpserver(port=8005, recv_queue=global_queue, name="TCP Server-6")
#     obj_process_tcpserver6.start()
#     obj_process_tcpserver7 = process_tcpserver(port=8006, recv_queue=global_queue, name="TCP Server-7")
#     obj_process_tcpserver7.start()
#     obj_process_tcpserver8 = process_tcpserver(port=8007, recv_queue=global_queue, name="TCP Server-8")
#     obj_process_tcpserver8.start()

#     # The main process receives and prints messages
#     while True:
#         msg = global_queue.get()
#         print(msg.to_dict())

    # gen.sleep(5)
    # process stop
    # obj_process_tcpserver2.stop()
