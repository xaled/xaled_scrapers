import logging
import threading
from mitmproxy.tools import cmdline
from mitmproxy.tools.main import process_options
from mitmproxy.utils import version_check
from mitmproxy import options
from mitmproxy import master
from xaled_scrapers._mitm.addon import default_addons, InterceptAddon
logger = logging.getLogger(__name__)


def get_proxy_master(port=8080, intercept_addon=None):  # pragma: no cover
    version_check.check_pyopenssl_version()

    parser = cmdline.mitmdump()
    args = parser.parse_args(['-p', str(port), '-q'])
    args.flow_detail = 0

    try:
        dump_options = options.Options()
        dump_options.load_paths(args.conf)
        dump_options.merge(cmdline.get_common_options(args))
        dump_options.merge(
            dict(
                flow_detail = args.flow_detail,
                keepserving = args.keepserving,
                filtstr = " ".join(args.filter) if args.filter else None,
            )
        )

        server = process_options(parser, dump_options, args)
        master = InterceptMaster(dump_options, server, intercept_addon)
        return master
    except:
        logger.error("mitmproxy error.", exc_info=True)


class InterceptMaster(master.Master):
    def __init__(self, options, server, intercept_addon=None):
        self.intercept_addon = intercept_addon or InterceptAddon()

        master.Master.__init__(self, options, server)
        self.addons.add(*default_addons(self.intercept_addon))


def start_proxy_master(port=8080, intercept_addon=None):
    master = get_proxy_master(port, intercept_addon)
    t = threading.Thread(target=master.run)
    t.setDaemon(True)
    logger.info("Starting proxy server at http://%s", master.server.address)
    t.start()
    return master
