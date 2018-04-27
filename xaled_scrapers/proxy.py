import logging
from xaled_scrapers._mitm.master import start_proxy_master
logger = logging.getLogger(__name__)


class Proxy():
    def __init__(self, port=8080):
        self.port = port
        self.process = None
        self.server = None
        self.proxy_address = '127.0.0.1:%d' % port
        self.master = start_proxy_master(port)

    def set_intercept_params(self, domain, paths):
        self.master.intercept_addon.set_intercept_params(domain, paths)

    def get_intercept_data(self):
        return self.master.intercept_addon.get_intercepted_data()

    def stop(self):
        self.master.shutdown()