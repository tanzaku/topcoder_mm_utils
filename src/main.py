

import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import os
from selenium.webdriver.common.action_chains import ActionChains

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
challenge_id = os.getenv('CHALLENGE_ID')
submit_file_path = os.getenv('SUBMIT_FILE_PATH')
screenshot_dir = os.getenv('SCREENSHOT_DIR')

if username is None:
    raise ValueError('Environment variable USERNAME is required.')

if password is None:
    raise ValueError('Environment variable PASSWORD is required.')

if challenge_id is None:
    raise ValueError('Environment variable CHALLENGE_ID is required.')

if submit_file_path is None:
    raise ValueError('Environment variable SUBMIT_FILE_PATH is required.')

driver = None


def screenshot(filename):
    global driver
    global screenshot_dir
    if screenshot_dir is not None:
        driver.save_screenshot(f'{screenshot_dir}/{filename}')


def init_driver():
    global driver
    options = webdriver.ChromeOptions()
    # options.add_argument('--user-data-dir=./profile')
    # options.add_argument('--profile-directory=Default')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1280,1024')
    options.add_argument('--disable-gpu')
    options.add_argument('--incognito')

    driver = webdriver.Chrome(options=options)

    print('start chrome')


def login():
    global driver
    try:
        driver.get('https://accounts.topcoder.com/member')
        username_box = driver.find_element_by_id('username')
        password_box = driver.find_element_by_id('current-password-input')
        username_box.send_keys(username)
        password_box.send_keys(password)
        screenshot('1_login.png')
        password_box.submit()
        print('login')
        time.sleep(3)
    except NoSuchElementException as e:
        pass


def submit():
    global driver
    global submit_file_path

    driver.get(f'https://www.topcoder.com/challenges/{challenge_id}/submit')
    screenshot('2_open_submit_page.png')

    # アップロードフォームを表示
    show_upload_box = driver.find_element_by_xpath(
        '//div[@aria-label="Select file to upload"]')
    show_upload_box.click()
    time.sleep(1)
    screenshot('3_open_upload_form.png')

    # アップロード
    upload_box = driver.find_element_by_xpath('//input[@type="file"]')
    upload_box.send_keys(submit_file_path)

    # アップロード終了まで待つ
    time.sleep(5)
    screenshot('4_uploaded.png')

    # 同意しますか？のチェックボックス
    agree_box = driver.find_element_by_xpath('//input[@id="agree"]')

    # Use ActionChains because `agree_box.click()` is not working.
    actions = ActionChains(driver)
    actions.move_to_element(agree_box).click().perform()

    # submit
    submit_box = driver.find_element_by_xpath('//button[@type="submit"]')
    submit_box.click()
    print('submit')

    time.sleep(3)

    screenshot('5_result.png')


init_driver()
login()
submit()

driver.quit()
