#!/usr/bin/python3
# author:  xaled (https://github.com/xaled)
# chaabinet account history scraper
import time
import logging
import json
from xaled_utils.json_min_db import JsonMinConnexion
from xaled_scrapers.selenium import get_firefox_proxy_caps, init_driver, get_display
from xaled_scrapers.args import get_additional_argument, parse_args
from xaled_scrapers.proxy import Proxy
from xaled_utils.logs import configure_logging

logger = logging.getLogger(__name__)
DEFAULT_DB_PATH = "chaabinet.data.json"


def login(user, password):
    global data, driver, proxy
    proxy.set_intercept_params('bpnet.gbp.ma',
                               ['/DashBoard/GetUserAccountBalanceEvolution', '/DashBoard/GetAccountStatement'])
    driver = init_driver(caps=get_firefox_proxy_caps(proxy=proxy.proxy_address))
    # driver.get("https://bpnet.gbp.ma/")
    driver.get("https://bpnet.gbp.ma/Account/Login")
    driver.find_element_by_id("UserName").send_keys(user)
    driver.find_element_by_id("Password").send_keys(password)
    driver.find_element_by_id("btnLogin").click()


def parse_operations():
    global data, driver, proxy
    intercpeted_data = proxy.get_intercept_data()
    wait = 0
    while len(intercpeted_data) < 2 and wait < 10:
        logger.info("Sleeping for 2s...")
        time.sleep(2)
        wait += 2
        intercpeted_data.update(proxy.get_intercept_data())

    # wait, sometimes you need to wait
    try:
        operations = json.loads(intercpeted_data['/DashBoard/GetAccountStatement'])
        for operation in operations:
            operation = dict(operation)
            opid = operation['RefOpe'] + '-' + operation['Dateope']
            operation['opid'] = opid
            if opid not in data['operation-ids']:
                data['operation-ids'].append(opid)
            data['operations'][opid] = operation
    except:
        logger.error("Error parsing AccountStatement.", exc_info=True)

    try:
        evolution = json.loads(intercpeted_data['/DashBoard/GetUserAccountBalanceEvolution'])[0]['BalanceEvolution']
    except:
        logger.error("Error parsing UserAccountBalanceEvolution.", exc_info=True)
        evolution = []
    for item in evolution:
        data['evolution'][item['Dateope']] = float(item['Solde'].replace(',', '.'))
    data.save()


def check_factures():
    global data, driver, proxy
    i = -1
    res = list()
    while True:
        i += 1
        try:
            driver.get('https://bpnet.gbp.ma/Payment/Favorite')
            driver.execute_script("window.scrollTo(0, 2000)")
            factures = driver.find_elements_by_xpath("//button[@class='unstylled_btn']")
            labels = [e.text for e in driver.find_elements_by_xpath("//td[contains(@class,'operationLibelle')]/span")]
            if i >= len(factures):
                break
            logger.info("getting facture #%d", (i+1))
            factures[i].click()
            driver.execute_script("window.scrollTo(0, 2000)")
            if driver.current_url != 'https://bpnet.gbp.ma/PaymentCategory/1': # ignore category = recharges mobiles
                nbr_factures = len(driver.find_elements_by_xpath("//tr[@class='negatif_transaction']"))
                if nbr_factures > 0:
                    res.append({'label': labels[i], '#': nbr_factures})
        except:
            logger.error("error parsing facture #%d", (i+1), exc_info=True)
    return res


def main(user, password):
    global data, driver, proxy

    if args.headless:
        display = get_display()
    proxy = Proxy()
    try:
        login(user, password)
        parse_operations()
        factures = check_factures()
        for f in factures:
            print("- %s: %d new factures." % (f['label'], f['#']))
    finally:
        driver.quit()
        proxy.stop()
        if args.headless:
            display.stop()
    # time.sleep(1)


if __name__ == "__main__":
    configure_logging(modules=["xaled_selenium","kutils"])
    additional_arguments = list()
    additional_arguments.append(get_additional_argument('-u', '--user', required=True))
    additional_arguments.append(get_additional_argument('-p', '--password', required=True))
    additional_arguments.append(get_additional_argument('--db-path', default=DEFAULT_DB_PATH))
    args = parse_args(additional_argument=additional_arguments)

    data = JsonMinConnexion(args.db_path, template={'operations': {}, 'operation-ids': [], 'evolution':{}})
    main(args.user, args.password)
