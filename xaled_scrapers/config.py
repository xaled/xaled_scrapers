from os.path import join, realpath, dirname

if __name__ == '':
    SCRIPT_DIR = realpath(__name__)
else:
    SCRIPT_DIR = dirname(realpath(__name__))

MITMP_SCRIPT = join(SCRIPT_DIR, "json_ipc_proxy.py")
MITMDUMP = '/usr/local/bin/mitmdump'
DEFAULT_CHROME_DRIVER_PATH = './chromedriver'
DEFAULT_FIREFOX_DRIVER_PATH = './geckodriver'