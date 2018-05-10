#!/usr/bin/python3
# author:  xaled (https://github.com/xaled)
# credits: https://github.com/pradyumnac/AliexpressOrders
import time
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from xaled_utils.json_min_db import JsonMinConnexion
from xaled_utils.logs import configure_logging
from xaled_scrapers.selenium import get_display
import logging
from xaled_scrapers.args import parse_args, get_additional_argument


logger = logging.getLogger(__name__)
UA_STRING = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0"
# EMAIL = 'XXXXXX'
# PASS = 'YYYYYYY'
# DRIVER_TYPE = "Chrome"
# DRIVER_PATH = "./chromedriver"

DEFAULT_ORDERS_DB_PATH = 'orders.data.json'
DEFAULT_PROTECTION_EXTENSION_MSG = "please extend protection for another 30 days"


# PROTECTION_EXTENSION = True


def update_order(order):
    global data
    data['orders'][order['order_id']] = order
    # if not order['order_id'] in data['order_ids']:
    #     data['order_ids'].append(order['order_id'])
    data.save()


def still_non_finished(order_id):
    order_ids = sorted(data['orders'].keys(), reverse=True)
    if len(order_ids) == 0:
        return True
    if not order_id in order_ids:
        return True
    if len(order_ids[order_ids.index(order_id) + 1:]) == 0:
        return True
    for oi in order_ids[order_ids.index(order_id) + 1:]:
        o = data['orders'][oi]
        if o['status'] == 'Awaiting delivery':
            return True
    return False


def parse_orders_page(src):
    node = pq(src)
    l_orders = []
    for e in node('.order-item-wraper'):
        try:
            order = {
                "order_id": pq(e)('.order-head .order-info .first-row .info-body')[0].text,
                "order_url": pq(e)('.order-head .order-info .first-row .view-detail-link')[0].attrib['href'],
                "order_dt": pq(e)('.order-head .order-info .second-row .info-body')[0].text,
                "order_store": pq(e)('.order-head .store-info .first-row .info-body')[0].text,
                "order_store_url": pq(e)('.order-head .store-info .second-row a')[0].attrib['href'],
                "order_amount": pq(e)('.order-head .order-amount .amount-body .amount-num')[0].text,
                "product_list": [{
                    "title": pq(f)('.product-right .product-title a').attr['title'],
                    "url": pq(f)('.product-right .product-title a').attr['href'],
                    "amount": pq(f)('.product-right .product-amount').text().strip(),
                    "property": pq(f)('.product-right .product-policy a').attr['title'],
                } for f in pq(e)('.order-body .product-sets')],
                "status": pq(e)('.order-body .order-status .f-left').text(),
                "status_days_left": pq(e)('.order-body .order-status .left-sendgoods-day').text().strip()
            }

            try:
                # TODO - handle not found exception
                t_button = driver.find_element_by_xpath(
                    '//*[@button_action="logisticsTracking" and @orderid="{}"]'.format(order['order_id']))
                hover = ActionChains(driver).move_to_element(t_button).perform()
                time.sleep(5)

                order['tracking_id'] = driver.find_element_by_css_selector('.ui-balloon b').text.strip().split(':')[
                    1].strip()
                try:
                    # if present, It means, tracking has begun
                    order['tracking_status'] = driver.find_element_by_css_selector('.ui-balloon .event-line-key').text
                    order['tracking_desc'] = driver.find_element_by_css_selector('.ui-balloon .event-line-desc').text
                except:
                    # Check for no event which means tracking has nto started or has not begun
                    try:
                        order['tracking_status'] = driver.find_element_by_css_selector(
                            '.ui-balloon .no-event').text.strip()
                        # If above passed, copy the tracking link and past for manual tracking
                        order['tracking_status'] = "Manual Tracking: " + driver.find_element_by_css_selector(
                            '.ui-balloon .no-event a').get_attribute('href').strip()
                        order['tracking_desc'] = ""
                    except:
                        order['tracking_status'] = '<Tracking Parse Error>'
                        order['tracking_desc'] = ""
            except:
                order['tracking_id'] = '<Error in Parsing Tracking ID>'
                order['tracking_status'] = '<Tracking Parse Error due to Error in Parsing Tracking ID>'
                order['tracking_desc'] = ""
                print("Tracking id retrieval failed for order:" + order['order_id'])
                pass
            update_order(order)
            l_orders.append(order)
        except:
            print("failed parsing 1 order")
            pass

    return l_orders


def parse_orders():
    orders = []
    source = driver.find_element_by_id("buyer-ordertable").get_attribute("innerHTML")

    # break_loop = False
    try:
        cur_page, total_page = (int(i) for i in
                                driver.find_element_by_xpath('//*[@id="simple-pager"]/div/label').text.split('/'))
        print(cur_page, '/', total_page)
        while (1):
            try:
                source = driver.find_element_by_id("buyer-ordertable").get_attribute("innerHTML")
                page_orders = parse_orders_page(source)
                orders.extend(page_orders)
                try:
                    if not still_non_finished(page_orders[-1]['order_id']):
                        break
                except:
                    break
            except:
                print("failed parsing page %d/%d" % (cur_page, total_page))
            try:
                if cur_page < total_page:
                    link_next = driver.find_element_by_xpath('//*[@id="simple-pager"]/div/a[text()="Next "]')
                    link_next.click()
                    cur_page, total_page = (int(i) for i in driver.find_element_by_xpath(
                        '//*[@id="simple-pager"]/div/label').text.split('/'))
                print("Page:%d/%d" % (cur_page, total_page))
            except:
                print("failed getting next link from page %d/%d" % (cur_page, total_page))
                break
            if cur_page == total_page:
                break  # break_loop = True # to break after parsing the next time
        return orders
    except Exception as e:
        print(e)
        return ([])


def login(email, passwd):
    # driver.get(
    #     "https://login.aliexpress.com/express/mulSiteLogin.htm?spm=2114.11010108.1000002.7.9c5Rcg&return=http%3A%2F%2Fwww.aliexpress.com%2F")
    driver.get("https://www.aliexpress.com/")
    # driver.find_element_by_class_name("sign-btn").click()
    driver.execute_script("document.getElementsByClassName('sign-btn')[0].click()")
    driver.get("https://login.aliexpress.com/express/mulSiteLogin.htm?return=https%3A%2F%2Fwww.aliexpress.com%2F")
    driver.switch_to_frame(driver.find_element_by_id("alibaba-login-box"))
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "fm-login-id"))
    )
    element.send_keys(email)
    driver.find_element_by_xpath("//*[@id=\"fm-login-password\"]").send_keys(passwd)
    driver.find_element_by_id("fm-login-submit").click()
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-key"))
        )
    except TimeoutException:
        print("Automatic log failed")
        if args.manual_login:
            element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, "search-key"))
            )
        else:
            raise
    print("Login success!")


def get_orders():
    driver.get("http://trade.aliexpress.com/orderList.htm?spm=2114.11010108.1000002.18.bT7Uae")
    orders = parse_orders()
    return (orders)


def send_protection_extension_request(order_id):
    try:
        order_url = "https://trade.aliexpress.com/order_detail.htm?orderId=%s" % (order_id)
        driver.get(order_url)
        driver.switch_to_frame(driver.find_element_by_id("msgDetailFrame"))
        driver.find_element_by_xpath("//*[@id=\"message-detail-textarea\"]").send_keys(
            args.protection_message)
        # driver.find_element_by_id("message-detail-textarea").send_keys(PROTECTION_EXTENSION_MSG)
        driver.find_element_by_id("send-message").click()
        print("sent protection extension requests for order_id: ", order_id)
    except:
        print("could not send protection extension request for order_id: ", order_id)


def parse_days_lefts(status_days_left):
    if status_days_left == '':
        return 3153600000.0
    arr = status_days_left.split(':')[1].split()
    sum = 0.0
    for i in range(len(arr) // 2):
        u, c = arr[-1 - i * 2], float(arr[-2 - i * 2])
        if 'second' in u:
            sum += c
        elif 'minute' in u:
            sum += c * 60.0
        elif 'hour' in u:
            sum += c * 3600.0
        elif 'day' in u:
            sum += c * 86400.0
    return sum


def init_driver_(drivertype="Chrome", driver_path="./chromedriver"):
    if drivertype == "Chrome":
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_argument("user-agent=" + UA_STRING)
        if driver_path is None:
            driver = webdriver.Chrome(chrome_options=opts)
        else:
            driver = webdriver.Chrome(driver_path, chrome_options=opts)
    elif drivertype == "PhantomJS":
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (UA_STRING)
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
    else:
        raise Exception("Invalid Driver Type:" + drivertype)
    driver.set_window_size(1366, 680)
    return driver


def resize_string(obj, size):
    if len(obj) < size:
        return obj + " "*(size - len(obj))
    return obj[:size]

def parse_days_left(days_left):
    try:
        return " ".join(days_left.split(":")[1].split()[:2])
    except:
        return days_left


if __name__ == "__main__":
    configure_logging(modules=['xaled_scrapers', 'xaled_utils'])
    additional_arguments = list()
    additional_arguments.append(get_additional_argument('-u', '--user', required=True))
    additional_arguments.append(get_additional_argument('-p', '--password', required=True))
    additional_arguments.append(get_additional_argument('--db-path', default=DEFAULT_ORDERS_DB_PATH))
    additional_arguments.append(get_additional_argument('-P', '--protection', action='store_true'))
    additional_arguments.append(get_additional_argument('-m', '--manual-login', action='store_true'))
    additional_arguments.append(
        get_additional_argument('--protection-message', default=DEFAULT_PROTECTION_EXTENSION_MSG))
    args = parse_args(additional_argument=additional_arguments)

    data = JsonMinConnexion(args.db_path, template={'order_ids': [], 'orders': {}})
    try:
        if args.headless:
            display = get_display(size=(1500, 800))
        driver = init_driver_()
        # driver = init_driver(drivertype=args.driver_type, driver_path=args.driver_path)
        login(args.user, args.password)

        orders = get_orders()
        for o in orders:
            if o['status'].strip() in ['Awaiting Shipment', 'Finished', 'Fund Processing']:
                continue  # ignore non shipped and finished orders
            tt = parse_days_lefts(o["status_days_left"])
            if 86400 < tt < 14 * 86400:  # 2 weeks
                if args.protection:
                    print("- SENDING PROECTECTION EXTENSION REQUEST FOR ORDER: #%s %s (%s)"%
                          (o['order_id'], o['product_list'][0]['title'][:50], o['status_days_left']))
                else:
                    print("- NOT SENDING PROECTECTION EXTENSION REQUEST FOR ORDER: #%s %s (%s)"%
                          (o['order_id'], o['product_list'][0]['title'][:50], o['status_days_left']))
            elif 0 < tt <= 86400:
                print("- ORDER ABOUT TO EXPIRE; %s (%s)" % (o['product_list'][0]['title'][:50], o['status_days_left']))
            if o['tracking_status'] == 'Delivered' and o['status'] != 'Finished':
                print("- ORDER DELIVERED: #%s %s (%s)" %
                      (o['order_id'], o['product_list'][0]['title'][:50], o['status_days_left']))

        if args.verbose:
            print("\nlist of retrieved orders:")
            print("%s | %s | %s | %s | %s | %s" %
                  (resize_string('order_id', 15), resize_string('product title', 40),
                   resize_string('status', 20), resize_string('days left', 10),
                   resize_string('tracking_status', 25), resize_string('tracking_desc', 25)))
            for o in orders:
                print("%s | %s | %s | %s | %s | %s" %
                      (resize_string(o['order_id'], 15), resize_string(o['product_list'][0]['title'], 40),
                       resize_string(o['status'],20), resize_string(parse_days_left(o['status_days_left']), 10),
                       resize_string(o['tracking_status'],25), resize_string(o['tracking_desc'],25)))
    finally:
        try: driver.quit()
        except: pass
        if args.headless:
            try: display.stop()
            except: pass
