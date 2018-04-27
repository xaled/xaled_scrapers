from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from xaled_scrapers.config import DEFAULT_CHROME_DRIVER_PATH, DEFAULT_FIREFOX_DRIVER_PATH
import logging

logger = logging.getLogger(__name__)


def get_display(visible=0, size=(1280, 1280)):
    # Display
    from pyvirtualdisplay import Display
    display = Display(visible=visible, size=size)
    # logger.info("starting display..")
    display.start()
    logger.info("Display started visible=%s, size=%s.", visible, size)
    return display


def init_driver( drivertype='firefox', driver_path=None, caps=None, window_size=None):
    drivertype = drivertype.lower()
    if drivertype == "firefox":
        if driver_path is None:
            driver_path = DEFAULT_FIREFOX_DRIVER_PATH
        driver = webdriver.Firefox(executable_path=driver_path, capabilities=caps)
        logger.info("Firefox driver started.")
    elif drivertype == "chrome":
        if driver_path is None:
            driver_path = DEFAULT_CHROME_DRIVER_PATH
        driver = webdriver.Chrome(driver_path, desired_capabilities=caps)
        logger.info("Chrome driver started.")
    elif drivertype == "phantomjs":
        driver = webdriver.PhantomJS(desired_capabilities=caps)
        logger.info("PhantomJS driver started.")
    else:
        raise Exception("Invalid Driver Type:" + drivertype)

    if window_size is not None:
        driver.set_window_size(window_size[0], window_size[1])
    return driver


def get_firefox_proxy_caps(proxy="127.0.0.1:8080"):
    proxy_dict = {
        'proxyType': 'MANUAL',
        'httpProxy': proxy,
        'ftpProxy': proxy,
        'sslProxy': proxy,
        'noProxy': []
    }
    caps = DesiredCapabilities.FIREFOX.copy()
    caps['acceptInsecureCerts'] = True
    caps['proxy'] = proxy_dict
    return caps


def get_chrome_proxy_caps(proxy="127.0.0.1:8080"):
    proxy_dict = {
        'proxyType': 'MANUAL',
        'httpProxy': proxy,
        'ftpProxy': proxy,
        'sslProxy': proxy,
        'noProxy': ""
    }
    caps = DesiredCapabilities.CHROME.copy()
    caps['acceptInsecureCerts'] = True
    caps['proxy'] = proxy_dict
    return caps