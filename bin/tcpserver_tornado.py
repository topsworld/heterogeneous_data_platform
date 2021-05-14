# coding=utf-8
import datetime
import logging.config
from multiprocessing import Process, Queue
from tornado.tcpserver import TCPServer
from tornado import gen, ioloop

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


class service_tcpserver(TCPServer):
    def __init__(self, recv_queue, port=8000, name="no set"
                 , timeout=recv_timeout, *args, **kwargs):
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
            logger.debug("[%s]: %s" % (self.name, self.devices))
            yield gen.sleep(5)

    def add_callback(self, func):
        """
        Add TCP callback function, such as connection list update, etc.
        :param func: Callback function
        :return: None
        """
        self.io_loop.add_callback(func)

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

    @gen.coroutine
    def handle_stream(self, stream, address):
        """
        Connection establishment and message reception processing function
        (asynchronous call using coroutine)
        :param stream: Socket entity
        :param address: IP address and port number, The format is (IP,Port)
        :return: None
        """
        # Add connect to the dict
        ip_port = address[0] + ":" + str(address[1])
        self.devices[ip_port] = {
            "stream": stream,
        }
        logger.info("[%s][%s]device connected, devices count: %s"
                    % (self.name, ip_port, len(self.devices)))

        # Listen to the message
        while True:
            try:
                data = yield gen.with_timeout(datetime.timedelta(seconds=self.timeout),
                                              stream.read_until(recv_end_str))
                yield stream.write(data)
                logger.debug("Receive data [%s] from %s" % (data, ip_port))

                recv_pkt = tcp_packet_item()
                recv_pkt.server_port = self.port
                recv_pkt.recv_address = ip_port
                recv_pkt.recv_msg = data

                # Add msg to tht queue
                if self.recv_queue is not None:
                    self.recv_queue.put(recv_pkt)

            except Exception as err:
                # Close socket
                stream.close()
                # Del device from dict
                del self.devices[ip_port]
                logger.info("[%s][%s] device disconnected ( %s ), devices count: %s"
                            % (self.name, ip_port, err.args[0], len(self.devices)))
                break

    def get_devices(self):
        """
        Get device list
        :return: Devices list
        """
        return self.devices

    @gen.coroutine
    def start_listen(self):
        """
        Start tcp server
        :return: None
        """
        # self.bind(self.port)
        # self.start(1) 

        self.listen(self.port)
        # Add callback func
        # self.add_callback(self.report_devices)
        logger.info("Start tcpserver, [name]:%s, [port]: %s" % (self.name, self.port))
        self.io_loop.start()


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
        self.server = service_tcpserver(port=self.port, recv_queue=self.recv_queue, name=self.name)

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
        self.terminate()
        logger.info("Terminate tcpserver, [name]:%s, [port]:%s" % (self.name, self.port))


"""
Example
"""
if __name__ == '__main__':
    # Process global queue
    global_queue = Queue()

    # Create three TCP services with port numbers 8000, 8001, and 8002.
    obj_process_tcpserver = process_tcpserver(port=8000, recv_queue=global_queue, name="TCP Server-1")
    obj_process_tcpserver.start()
    obj_process_tcpserver2 = process_tcpserver(port=8001, recv_queue=global_queue, name="TCP Server-2")
    obj_process_tcpserver2.start()
    obj_process_tcpserver3 = process_tcpserver(port=8002, recv_queue=global_queue, name="TCP Server-3")
    obj_process_tcpserver3.start()

    # The main process receives and prints messages
    while True:
        msg = global_queue.get()
        print(msg.to_dict())

    # gen.sleep(5)
    # process stop
    # obj_process_tcpserver2.stop()
