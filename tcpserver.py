# coding=utf-8
import logging.config
import threading
import time
from tornado.tcpserver import TCPServer
from tornado.iostream import StreamClosedError
from tornado import gen, ioloop
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('tcpserver')


class service_tcpserver(TCPServer):
    def __init__(self, *args, **kwargs):
        super(service_tcpserver, self).__init__(*args, **kwargs)
        self.devices = list()

    @gen.coroutine
    def handle_stream(self, stream, address):
        self.devices.append(address)
        logger.debug("[%s:%s]device connected, devices count: %s"
                     % (address[0], address[1], len(self.devices)))
        while True:
            try:
                data = yield stream.read_until(b"\n")
                yield stream.write(data)
                print("receive data ", data, " from ", address)
            except StreamClosedError:
                self.devices.remove(address)
                logger.debug("[%s:%s]device disconnected, devices count: %s"
                             % (address[0], address[1], len(self.devices)))
                break

    def get_devices(self):
        return self.devices

    def start_listen(self, port=8000):
        self.listen(port)
        ioloop.IOLoop.current().start()


class thread_tcpserver(threading.Thread):
    def __init__(self):
        try:
            threading.Thread.__init__(self)
            self.running = True
            self.server = service_tcpserver()

        except Exception as e:
            logger.error(e.args)

    def run(self):
        try:
            self.server.start_listen(8000)
            while self.running:
                time.sleep(0.001)
        except Exception as e:
            logger.error(e.args)

    def stop(self):
        self.running = False
        self.server.stop()

    def delay_ms(self, tout):
        ct = tout
        while self.running and ct > 0:
            time.sleep(0.001)
            ct -= 1


if __name__ == '__main__':
    # obj_thread_tcpserver = thread_tcpserver()
    # obj_thread_tcpserver.setDaemon(False)
    # obj_thread_tcpserver.start()
    # time.sleep(5)
    # obj_thread_tcpserver.stop()
    ss = service_tcpserver()
    ss.start_listen(8000)
    ss1 = service_tcpserver()
    ss1.start_listen(8001)
    ioloop.IOLoop.current().start()
