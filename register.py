import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from smsactivate.api import SMSActivateAPI
from time import sleep
import re
import random
import requests, warnings
from requests.packages import urllib3
import pyperclip

def shuffle(arr):
    random.shuffle(arr)
    return arr

def extract_link(text):
    pattern = r'https?://[^\s/$.?#].[^\s]*'
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return None

def register(prefix, password, first_name, last_name):
    print("正在注册临时邮箱……")
    urllib3.disable_warnings()
    warnings.filterwarnings("ignore")

    mail_base_url = "https://api.mail.tm"

    domain_response = requests.get(mail_base_url + '/domains', verify = False, proxies = None).json()
    domain = domain_response['hydra:member'][0]['domain']
    mail_address = prefix + '@' + domain

    reg_response = requests.post(url = mail_base_url + '/accounts', verify = False, proxies = None, json = {
        'address': mail_address,
        'password': password
    })
    if not reg_response.ok:
        raise Exception('Failed to register a new email!')
    
    token = requests.post(url = mail_base_url + '/token', verify = False, proxies = None, json = {
        'address': mail_address,
        'password': password
    }).json()['token']
    auth_headers = {
        "accept": "application/ld+json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    print(f'正在用邮箱 {mail_address} 注册，密码为 {password}')

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--incognito")  # 启用Chrome浏览器无痕模式

    driver = uc.Chrome(options = options)

    wait = WebDriverWait(driver, 600)  # 最长等待时间为600秒

    driver.get('https://platform.openai.com')
    driver.implicitly_wait(600)

    driver.find_element(By.LINK_TEXT, 'Sign up').click()
    sleep(0.5)
    driver.find_element(By.ID, 'email').send_keys(mail_address)
    sleep(0.5)
    driver.find_element(By.NAME, 'action').click()
    sleep(0.5)
    driver.find_element(By.ID, 'password').send_keys(password)
    sleep(0.5)
    driver.find_element(By.NAME, 'action').click()

    while True:
        sleep(5)
        ver_response = requests.get(url = mail_base_url + '/messages', headers = auth_headers, verify = False, proxies = None).json()
        if ver_response['hydra:totalItems'] > 0:
            message_id = ver_response['hydra:member'][0]['id']
            message_content = requests.get(url = mail_base_url + f'/messages/{message_id}', headers = auth_headers, verify = False, proxies = None).json()
            ver_link = extract_link(message_content['text'])
            # print(f'Debug: Get link: {ver_link}')
            break
        print('正在等待验证邮件……')

    driver.get(ver_link)

    sleep(3)
    driver.find_element(By.XPATH, "//input[@placeholder='First name']").send_keys(first_name)
    sleep(0.5)
    driver.find_element(By.XPATH, "//input[@placeholder='Last name']").send_keys(last_name)
    sleep(0.5)
    driver.find_element(By.XPATH, "//input[@placeholder='Birthday']").send_keys('11111999')
    sleep(0.5)
    driver.find_element(By.CLASS_NAME, 'btn-label-wrap').click()

    sa = SMSActivateAPI('YOUR-API-KEY')
    number = sa.getNumber(service = 'dr', country = 16, verification = False)  # dr: openai 16: 英格兰
    print(f'获取临时手机号：{number["phone"]}')

    driver.find_element(By.XPATH, '//div[@class=" css-12wvehw-control"]').click()
    element = wait.until(ec.element_to_be_clickable((By.ID, 'react-select-2-option-236')))
    element.click()
    driver.find_element(By.XPATH,
                        '//input[@class="text-input text-input-lg text-input-full" and @type="text"]').send_keys(
        str(number['phone'])[2:])
    sleep(5)
    send_sms_element = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                              '//button[@class="btn btn-full btn-lg btn-filled '
                                                              'btn-primary onb-send-code-primary" and '
                                                              '@type="submit"]')))
    send_sms_element.click()
    wait.until(ec.element_to_be_clickable((By.XPATH, '//div[@class="link-style onb-back-btn"]')))
    while sa.getStatus(id=number['activation_id'])[7:9] != 'OK':
        print('正在等待短信验证码……')
        sleep(5)
    print(f'取得短信验证码：{sa.getStatus(number["activation_id"])[10:]}')
    driver.find_element(By.XPATH,
                        '//input[@class="text-input text-input-lg text-input-full" and @type="text"]').send_keys(
        sa.getStatus(number['activation_id'])[10:])

    print('正在获取 API 秘钥……')
    driver.find_element(By.CLASS_NAME, 'user-details').click()
    driver.find_element(By.LINK_TEXT, 'View API keys').click()

    sa.setStatus(id=number['activation_id'], status=6)

    sleep(3)

    driver.find_element(By.XPATH, '//button[@class="btn btn-sm btn-filled btn-neutral" and @type="button" and @tabindex="0"]').click()
    sleep(1)
    wait.until(ec.element_to_be_clickable((By.XPATH, '//button[@class="btn btn-sm btn-filled btn-primary modal-button" and @tabindex="0" and @type="submit"]')))
    driver.find_element(By.XPATH, '//button[@class="btn btn-sm btn-filled btn-primary modal-button" and @tabindex="0" and @type="submit"]').click()
    apikey = driver.find_element(By.XPATH, '//input[@class="text-input text-input-sm text-input-full" and @type="text" and @spellcheck="false"]').get_attribute('value')
    print(f'获得 API 秘钥：{apikey}')
    print()

    pyperclip.copy(mail_address + ',' + password + ',' + apikey)
    print('完整注册信息如下')
    print(pyperclip.paste())
    print()

    driver.quit()

    with open('user_info.csv', 'a') as file:
        file.write(pyperclip.paste() + '\n')

    print('注册成功，信息已经复制到剪贴板并输出到文件！记得手动换一下 IP~')
    return driver

# 随机生成FirstName
def random_firstname():
    first_name = ['John', 'James', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Charles', 'Joseph', 'Thomas',
                  'Christopher', 'Daniel', 'Paul', 'Mark', 'Donald', 'George', 'Kenneth', 'Steven', 'Edward', 'Brian',
                  'Ronald', 'Anthony', 'Kevin', 'Jason', 'Matthew', 'Gary', 'Timothy', 'Jose', 'Larry', 'Jeffrey',
                  'Frank', 'Scott', 'Eric']
    return shuffle(first_name)[0]


# 随机生成LastName
def random_lastname():
    last_name = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor',
                 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez',
                 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen', 'Young', 'Hernandez',
                 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter',
                 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards',
                 'Collins']
    return shuffle(last_name)[0]


# 随机生成16位密码
def random_password():
    password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(16))
    return password


# 随机生成 16位邮箱前缀
def random_email_prefix():
    char = random.choice('abcdefghijklmnopqrstuvwxyz')
    # 邮箱前缀必须以字母开头
    prefix = char + ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(15))
    return prefix


def main():
    prefix = random_email_prefix()
    password = random_password()
    first_name = random_firstname()
    last_name = random_lastname()

    register(prefix, password, first_name, last_name)

if __name__ == '__main__':
    main()
