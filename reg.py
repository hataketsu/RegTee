import random
import sys
import time
import traceback
from configparser import ConfigParser
from multiprocessing.pool import ThreadPool
from threading import Lock

import requests
from openpyxl import load_workbook
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver

PROXIES = [
    'http://lum-customer-hl_7866d962-zone-zone1-country-us:12ypsatl8zly@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone1-country-gb:12ypsatl8zly@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone2-country-us:12pqfcboroxq@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone2-country-gb:12pqfcboroxq@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone3-country-us:rthu8x05933e@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone3-country-gb:rthu8x05933e@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone4-country-us:m0wdgith1wti@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone4-country-gb:m0wdgith1wti@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone5-country-us:9jhehktl5278@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone5-country-gb:9jhehktl5278@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone6-country-us:j0au1g290vez@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-zone6-country-gb:j0au1g290vez@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-static-country-gb:8us5gf64hux8@zproxy.lum-superproxy.io:22225',
    'http://lum-customer-hl_7866d962-zone-static-country-us:8us5gf64hux8@zproxy.lum-superproxy.io:22225',
]

result_lock = Lock()


def save_result():
    with result_lock:
        wb.save(filename=filename)


def reg_acc(row):
    driver = None
    try:
        email = row[0].value
        print(f"[{email}]\tStart reg")
        password = row[1].value

        proxy = random.choice(PROXIES)

        options = {
            'proxy': {
                'http': proxy,
                'https': proxy,
                'no_proxy': ''

            }, 'verify_ssl': False
        }
        res = requests.get(
            f'https://2captcha.com/in.php?key={_2captcha_api_key}&method=userrecaptcha&googlekey={G_SITEKEY}&json=1&pageurl={TEESPRING_COM_SIGNUP}')
        print(res.text)

        driver = webdriver.Firefox(seleniumwire_options=options)
        driver.implicitly_wait(10)
        driver.get('https://teespring.com/signup')
        form = driver.find_element_by_css_selector('.js-email-signup-form')
        email_input = form.find_element_by_css_selector('[name=email]')
        password_input = form.find_element_by_css_selector('[name=password]')
        password2_input = form.find_element_by_css_selector('[name=password_confirmation]')
        email_input.send_keys(email)
        password_input.send_keys(password)
        password2_input.send_keys(password)

        request_id = res.json()['request']
        code = 'CAPCHA_NOT_READY'
        count = 1
        while code == 'CAPCHA_NOT_READY':
            time.sleep(2)
            res2 = requests.get(
                f'https://2captcha.com/res.php?key={_2captcha_api_key}&action=get&id={request_id}&json=1')
            code = res2.json()['request']
            count += 1
            print(count, res2.text)
            if count > 200:
                raise TimeoutError("captcha timeout")

        tx = form.find_element_by_css_selector('textarea')
        driver.execute_script(f"arguments[0].innerHTML='{code}'", tx)
        form.find_element_by_css_selector("[type='submit']").click()
        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.url_changes("https://teespring.com/signup"))
        except:  # login failed
            err = ''
            for e in driver.find_elements_by_css_selector('.js-email-signup-form .form__error'):
                err += e.text
            row[4].value = err
            save_result()
            return
        row[3].value = "Reg."

        driver.get('https://teespring.com/dashboard/settings')
        form = driver.find_element_by_css_selector('.update_paypal_email__form')
        email_input = form.find_element_by_css_selector("[name='user[paypal_email]']")
        email2_input = form.find_element_by_css_selector("[name='user[paypal_email_confirmation]']")
        email_input.send_keys(email)
        email2_input.send_keys(email)
        form.find_element_by_css_selector('[type=submit]').click()
        row[3].value += "Paypal."
        row[2].value = "Done"
    except Exception as e:
        row[4].value = str(e)
        save_result()
        traceback.print_exc()
    else:
        row[4].value = ''
        save_result()
    finally:
        if driver:
            driver.close()


TEESPRING_COM_SIGNUP = 'https://teespring.com/signup'
G_SITEKEY = '6LdFYQgUAAAAAE6j6MctlWXn6YIsGzb0xIyjIH4A'

config = ConfigParser()
config.read('config.ini')

_2captcha_api_key = config['default']['2captcha_api']
thread = int(config['default']['threads'])
if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = config['default']['acc_file']
    print(f'Load {filename}')
    wb = load_workbook(filename=filename)
    sheet = wb._sheets[0]

    acc_list = []
    rows = sheet.rows
    next(rows)
    total_acc = 0
    for row in rows:
        if row[0].value:
            if not row[2].value:
                acc_list.append(row)
            total_acc += 1

    print(f"Total: {total_acc} accounts")
    print(f"Remain: {len(acc_list)} accounts")
    print(f"Run with {thread} threads\n\n")
    pool = ThreadPool(thread)
    pool.map(reg_acc, acc_list)
    input("Done")
