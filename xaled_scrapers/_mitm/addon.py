from mitmproxy.addons import anticache
from mitmproxy.addons import anticomp
from mitmproxy.addons import check_alpn
from mitmproxy.addons import check_ca
from mitmproxy.addons import clientplayback
from mitmproxy.addons import disable_h2c_upgrade
from mitmproxy.addons import onboarding
from mitmproxy.addons import proxyauth
from mitmproxy.addons import replace
from mitmproxy.addons import script
from mitmproxy.addons import serverplayback
from mitmproxy.addons import setheaders
from mitmproxy.addons import stickyauth
from mitmproxy.addons import stickycookie
from mitmproxy.addons import streambodies
from mitmproxy.addons import streamfile
from mitmproxy.addons import upstream_auth
from mitmproxy import ctx, exceptions
import logging
logger= logging.getLogger(__name__)


def default_addons(intercept_addon=None):
    if intercept_addon is None:
        intercept_addon = InterceptAddon()
    return [
        anticache.AntiCache(),
        anticomp.AntiComp(),
        check_alpn.CheckALPN(),
        check_ca.CheckCA(),
        clientplayback.ClientPlayback(),
        disable_h2c_upgrade.DisableH2CleartextUpgrade(),
        onboarding.Onboarding(),
        proxyauth.ProxyAuth(),
        replace.Replace(),
        replace.ReplaceFile(),
        script.ScriptLoader(),
        intercept_addon,
        serverplayback.ServerPlayback(),
        setheaders.SetHeaders(),
        stickyauth.StickyAuth(),
        stickycookie.StickyCookie(),
        streambodies.StreamBodies(),
        streamfile.StreamFile(),
        upstream_auth.UpstreamAuth(),
    ]


class InterceptAddonLoader:
    def configure(self, options, updated):
        logger.debug("InterceptAddonLoader.configure")
        ordered = []
        newscripts = []

        try:
            sc = InterceptAddon()
        except ValueError as e:
            raise exceptions.OptionsError(str(e))
        ordered.append(sc)
        newscripts.append(sc)

        ochain = ctx.master.addons.chain
        pos = ochain.index(self)
        ctx.master.addons.chain = ochain[:pos + 1] + ordered + ochain[pos + 1:]

        for s in newscripts:
            ctx.master.addons.startup(s)


class InterceptAddon:
    def __init__(self):
        self.domain = ''
        self.paths = []
        self.intercepted_data = {}

    def response(self, flow):
        # logger.debug("intercepted url: %s", flow.request.host+flow.request.path)
        if flow.request.host == self.domain and flow.request.path in self.paths:
            self.intercepted_data[flow.request.path] = flow.response.text
            flow.intercept()
            flow.resume()
            logger.info('intercepted data for path: %s', flow.request.path)

    def set_intercept_params(self, domain, paths):
        logger.debug("set_intercept_params(domain=%s, paths=%s).", domain, paths)
        self.domain = domain
        self.paths = paths

    def get_intercepted_data(self):
        res = dict(self.intercepted_data)
        self.intercepted_data.clear()
        logger.debug("get_intercepted_data returning :%s.", res)
        return res

    def start(self):
        logger.debug("InterceptAddon start!")
        return self

    def done(self):
        logger.debug("InterceptAddon done!")
