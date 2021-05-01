# coding=utf-8
import logging.config
from socketserver import BaseRequestHandler, ThreadingUDPServer
from multiprocessing import Queue as msg_queue, Process

# logging.config.fileConfig('logging.conf')
logger = logging.getLogger('udpserver')

udp_replay_str = b"ok\r\n"


class udp_packet_item:
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


class service_udpserver(BaseRequestHandler):
    recv_queue: msg_queue
    port: int
    name: str
    udpserver: ThreadingUDPServer

    def listen(self, recv_queue: msg_queue, port: int, name: str):
        self.recv_queue = recv_queue
        self.port = port
        self.name = name

        # Start udp server
        self.udpserver = ThreadingUDPServer(('', self.port), self)
        logger.info("Start udpserver, [name]:%s, [port]: %s" % (self.name, self.port))
        self.udpserver.serve_forever()

    def handle(self):
        ip_port = self.client_address
        # logger.info("[%s][%s]device connected."
        #             % (self.name, ip_port))
        # Get message and client socket
        udp_msg, sock = self.request
        # Replay
        sock.sendto(udp_replay_str, self.client_address)

        # Packet msg
        logger.debug("UDP receive data [%s] from %s" % (udp_msg, ip_port))
        recv_pkt = udp_packet_item()
        recv_pkt.server_port = self.port
        recv_pkt.recv_address = ip_port
        recv_pkt.recv_msg = udp_msg
        # Add msg to the queue
        if self.recv_queue is not None:
            self.recv_queue.put(recv_pkt)


# serv = ThreadingUDPServer(('', 8000), service_udpserver)
# serv.serve_forever()


class process_udpserver(Process):
    """
    UDP service process, Inherited from multiprocessing Process
    """

    def __init__(self, port: int, recv_queue: msg_queue, name="udp: no set"):
        """
        UDP service process
        :param port: UDP service open port, such as 12345
        :param recv_queue: UDP service receive queue
                (Used for process data interaction)
                from multiprocessing import Queue
        :param name: TCP Service name, default: no set
        """
        super(process_udpserver, self).__init__()
        self.port = port
        self.name = name
        self.recv_queue = recv_queue
        self.obj_service_udpserver = service_udpserver

    def run(self):
        """
        Process started, start tcp service
        :return: None
        """
        try:
            self.obj_service_udpserver.listen(self.obj_service_udpserver
                                              , self.recv_queue, self.port, self.name)
        except Exception as e:
            logger.error(e.args)

    def stop(self):
        """
        Terminate the process, stop the TCP service
        :return:
        """
        self.terminate()
        logger.info("Terminate udpserver, [name]:%s, [port]:%s" % (self.name, self.port))


"""
Example
"""
# if __name__ == '__main__':
#     # Process global queue
#     global_queue = msg_queue()
#
#     # Create three TCP services with port numbers 8000, 8001, and 8002.
#     obj_process_udpserver = process_udpserver(port=8000, recv_queue=global_queue, name="UDP Server-1")
#     obj_process_udpserver.start()
#     obj_process_udpserver2 = process_udpserver(port=8001, recv_queue=global_queue, name="UDP Server-2")
#     obj_process_udpserver2.start()
#     obj_process_udpserver3 = process_udpserver(port=8002, recv_queue=global_queue, name="UDP Server-3")
#     obj_process_udpserver3.start()
#
#     # The main process receives and prints messages
#     while True:
#         msg = global_queue.get()
#         print(msg.to_dict())