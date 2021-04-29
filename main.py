import logging
import logging.config
logging.config.fileConfig('logging.conf')

import database
import tcpserver
import udpserver
import mqttclient
import rpc
import websocket


logger = logging.getLogger('main')


logger.debug("main")
