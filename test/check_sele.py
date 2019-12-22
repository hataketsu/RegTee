import time
import random
import requests
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver

options = {
    'proxy': {
        'http': 'http://lum-customer-hl_7866d962-zone-zone1-country-us:12ypsatl8zly@zproxy.lum-superproxy.io:22225',
        'https': 'http://lum-customer-hl_7866d962-zone-zone1-country-us:12ypsatl8zly@zproxy.lum-superproxy.io:22225',
        'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
    }
}
TEESPRING_COM_SIGNUP = 'https://teespring.com/signup'
G_SITEKEY = '6LdFYQgUAAAAAE6j6MctlWXn6YIsGzb0xIyjIH4A'

_2captcha_api_key = 'ee096299296383d6506c5c21b4a3568f'
res = requests.get(
    f'https://2captcha.com/in.php?key={_2captcha_api_key}&method=userrecaptcha&googlekey={G_SITEKEY}&json=1&pageurl={TEESPRING_COM_SIGNUP}')
print(res.text)
profile = webdriver.FirefoxProfile()
profile.set_preference('intl.accept_languages', 'en-US, en')
options2 = Options()
options2.headless = False
driver = webdriver.Firefox(seleniumwire_options=options, firefox_profile=profile, options=options2)
driver.implicitly_wait(10)
driver.get('https://teespring.com/signup')
form = driver.find_elements_by_css_selector('.js-email-signup-form')[0]
email_input = form.find_element_by_css_selector('[name=email]')
password_input = form.find_element_by_css_selector('[name=password]')
password2_input = form.find_element_by_css_selector('[name=password_confirmation]')
email_input.send_keys(f'lecanhdwe{random.randint(100000000,1000000000)}@gmail.com')
password_input.send_keys('Zx123123')
password2_input.send_keys('Zx123123')
tx = form.find_element_by_css_selector('textarea')
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
driver.execute_script(f"arguments[0].innerHTML='{code}'", tx)
form.find_element_by_css_selector("[type='submit']").click()
# driver.get('https://teespring.com/dashboard/campaigns_overview')
print('start waiting')

WebDriverWait(driver, 20).until(expected_conditions.url_to_be('https://teespring.com/welcome'))
