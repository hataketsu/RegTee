import random
import sys
import time
import traceback
from configparser import ConfigParser
from multiprocessing.pool import ThreadPool
from threading import Lock

import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

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
cookies = {
    'AWSALB': 'Kc1HWTLmekFs11nTu/hGCLfQ7LTwnCEAzcCpeIEHCS50QxbdE55KQ/osy58a6iGk9RpEeUL1aUgLnOqvyz9dorTryKcyde0zWY0A2AQqrVlBNpr/+jFc5BX4LrAd',
    '_teespring_session_5': 'VUlFUTBmTndNcUJINFc4dEhqcWlRZ25kRGdwb3g5T0pPbDdkMmFTT3h5SWwxVnAxeG9OYVNoTUVPdUVLNEEybld4Y0lTWHp2NVMyK2VZN0J4clIzL0pmcjU1V1JkSXBmcEZ4ZzNJcXBYZzF1VXI2N3hjcjBFWTVQMFV5MWQ0dVVTUmVLbHVBd1lkUmtOcTBPN0w1TjVpTGQ5cTR5aVQrSEJ2YnlMV2N6VnB4V3dGRHJ3bjBObmhRRnh2SlRJTnNpWSsxbHlDejJUNEc4dnpGdmN4MzhUZjZTeXhLYzZyQW1NMUFLMEY2cHd4WndQSTNTbDFYRXVTaEtkVi9vL1doeGR4V2dVeXN0OWI0WG44UjcyVmpnWHlVWTNSL2dZTVFZcnlDWHZRVG5rR3h5Q0k1NHRWdk9Gd21WLzN4Qi8rRUxIbTBSMklBM1FpdVNPNnhFVTNLaWRhUU5uN2ZxSCsyd0hlSWRCN3BqUk01SUJra1BBM0RsTmZkdU45ejlQcTNWSkk3TWhNL081K0ozWjcvSThYdThUanBleGRZQ3JLcm1uRFdkRno5YmpmKzRZYys3aTVKK203OXJISkNnM3Q2akhVU0ZuYloxMS9SaFFQWDNJS3RZN1NQbXprZUtRT2MwYVVndjI0SGlIK0pwV0xMbVFYdzBETUdYVHE4RlNjS1E1ZW1kZmhyNGlPVERiWHpLaFlWYlpKejBEblRNamRGeWtLWTJHdHZPNFFIUzkzQ2s5dEV1Z3czdjVPTGQvL0JhLS05ZUpQSnFYbFVLY2xQd1Z0N3MyU0lBPT0%3D--db095f3c3aeb0f1a92aff7db23ae8280b4a8c333',
}
headers = {
    'sec-fetch-mode': 'cors',
    'csrtoken': 'undefined',
    'x-requested-with': 'XMLHttpRequest',
    'X-CSRF-Token': '8pTSQX4NvHwHfSbpmAbftC5JrPYHv1l5MwKENYjjYD/gMyRO8V+ddaf9v8C+NtxrS2UF77nvRmzUAqk/LcEk3w==',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'referer': 'https://teespring.com/signup',
    'authority': 'teespring.com',
    'sec-fetch-site': 'same-origin',
    'dnt': '1',
    'origin': 'https://teespring.com',
}

result_lock = Lock()


def save_result():
    with result_lock:
        wb.save(filename=filename)


def reg_acc(row):
    try:
        email = row[0].value
        print(f"[{email}]\tStart reg")
        password = row[1].value
        time.sleep(random.randint(0, 10))
        start_time = time.time()
        if captcha == 'anticaptcha':
            code = get_anticaptcha()
        else:
            code = get_2captcha()
        delta_time = time.time() - start_time
        print(f"[{email}]\tCaptcha time: {int(delta_time)}s")

        data = {
            'email': email,
            'password': password,
            'password_confirmation': password,
            'g-recaptcha-response': code,
            'remember_user': 'on'
        }
        s = requests.Session()
        proxy = random.choice(PROXIES)
        proxies = {
            'http': proxy,
            'https': proxy
        }
        s.proxies = proxies
        ip = s.get('http://lumtest.com/myip.json').json()['ip']
        print(f"[{email}]\tIP: {ip}")
        row[5].value = ip
        s.headers = headers
        response = s.post(TEESPRING_COM_SIGNUP, data=data, cookies=cookies)
        row[2].value = response.text
        if 'Retry later' in response.text:
            row[2].value = ''
            row[4].value = 'Blocked IP'
            print(f"[{email}]\tFail: Blocked IP")
            save_result()
            reg_acc(row)
            return
        save_result()
        result = response.json()
        if 'message' in result and result['message'] == "Success!":
            row[3].value = "Success"
            save_result()
            print(f"[{email}]\tSuccess")
        elif 'field' in result and result['field'] == 'recaptcha':
            row[4].value = response.text
            row[2].value = ""
            save_result()
            print(f"[{email}]\tRetry captcha")
            reg_acc(row)
        else:
            print(f"[{email}]\tFail!")

        print(s.cookies)
        setting_page = s.get('https://teespring.com/dashboard/settings').text
        setting_page_bs = BeautifulSoup(setting_page, 'html.parser')
        paypal_form = setting_page_bs.select('.update_paypal_email__form')[0]
        action = paypal_form.attrs['action']
        token = paypal_form.select('input[name="authenticity_token"]')[0].attrs['value']
        data = {
            'utf8': '\u2713',
            'authenticity_token': token,
            'user[paypal_email]': email,
            'user[paypal_email_confirmation]': email,
            'commit': 'Set Paypal address'
        }

        response = s.post('https://teespring.com' + action, data=data)

    except Exception as e:
        row[4].value = str(e)
        save_result()
        traceback.print_exc()

    else:
        row[4].value = ''
        save_result()


def get_anticaptcha():
    client = AnticaptchaClient(api_key)
    task = NoCaptchaTaskProxylessTask(TEESPRING_COM_SIGNUP, G_SITEKEY)
    print(f"Money left: {client.getBalance()}")
    job = client.createTask(task)
    job.join()
    code = job.get_solution_response()
    return code


def get_2captcha():
    res = requests.get(
        f'https://2captcha.com/in.php?key={_2captcha_api_key}&method=userrecaptcha&googlekey={G_SITEKEY}&json=1&pageurl={TEESPRING_COM_SIGNUP}')
    print(res.text)
    try:
        request_id = res.json()['request']
    except:
        print('Error', res.text)
    code = 'CAPCHA_NOT_READY'
    count = 1
    while code == 'CAPCHA_NOT_READY':
        time.sleep(2)
        res2 = requests.get(
            f'https://2captcha.com/res.php?key={_2captcha_api_key}&action=get&id={request_id}&json=1')
        code = res2.json()['request']
        count += 1
    return code


TEESPRING_COM_SIGNUP = 'https://teespring.com/signup'
G_SITEKEY = '6LdFYQgUAAAAAE6j6MctlWXn6YIsGzb0xIyjIH4A'

config = ConfigParser()
config.read('config.ini')

api_key = config['default']['anticaptcha_api']
_2captcha_api_key = config['default']['2captcha_api']
captcha = config['default']['captcha']
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
