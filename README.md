# xaled_scrapers
A collection of helper functions for scraping web sites.

## Installation
pip3 install xaled_scrapers

## requirements:
- Python3
- Xvbf:  `sudo apt-get install xvfb`
- selenium, pyquery pyvirtualdisplay mitmproxy: `$ sudo pip3 install selenium pyquery pyvirtualdisplay mitmproxy  xaled_utils`
- chromedriver (from https://sites.google.com/a/chromium.org/chromedriver/downloads)
- geckodriver (from https://github.com/mozilla/geckodriver/releases)

## Scripts:
### Aliexpress:
- help : `$ ./aliexpress.py --help`
- example : `$ ./aliexpress.py --headless -u example@email.com -p PaSsWoRd --verbose --protection`

### Chaabinet (bpnet.gbp.ma):
- help : `$ ./chaabinet.py --help`
- example : `$ ./chaabinet.py --headless -u 300000 -p PaSsWoRd`