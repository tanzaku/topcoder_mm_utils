

import time
from datetime import datetime
from collections import defaultdict

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import os
from selenium.webdriver.common.action_chains import ActionChains

import psycopg2
import psycopg2.extras

username = os.getenv('TC_USERNAME')
password = os.getenv('TC_PASSWORD')
screenshot_dir = os.getenv('SCREENSHOT_DIR')
pg_db_host = os.getenv('PG_DB_HOST')
pg_db_username = os.getenv('PG_DB_USERNAME')
pg_db_password = os.getenv('PG_DB_PASSWORD')
pg_db_name = os.getenv('PG_DB_NAME')
pg_db_port = os.getenv('PG_DB_PORT')

if username is None:
    raise ValueError('Environment variable TC_USERNAME is required.')

if password is None:
    raise ValueError('Environment variable TC_PASSWORD is required.')

if pg_db_host is None:
    raise ValueError('Environment variable PG_DB_HOST is required.')

if pg_db_username is None:
    raise ValueError('Environment variable PG_DB_USERNAME is required.')

if pg_db_password is None:
    raise ValueError('Environment variable PG_DB_PASSWORD is required.')

if pg_db_name is None:
    raise ValueError('Environment variable PG_DB_NAME is required.')

if pg_db_port is None:
    raise ValueError('Environment variable PG_DB_PORT is required.')

driver = None
screenshot_index = 0


def screenshot(filename):
    global driver
    global screenshot_dir
    global screenshot_index
    if screenshot_dir is not None:
        driver.save_screenshot(
            f'{screenshot_dir}/{screenshot_index}_{filename}')
        screenshot_index = screenshot_index + 1


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
        screenshot('login_form.png')
        username_box = driver.find_element_by_id('username')
        password_box = driver.find_element_by_id('current-password-input')
        username_box.send_keys(username)
        password_box.send_keys(password)
        screenshot('fill_login_form.png')
        password_box.submit()
        print('login')
        time.sleep(5)
    except NoSuchElementException as e:
        print('Already logged in?', e)


def get_standings(challenge_id):
    global driver

    submisisons_url = f'https://www.topcoder.com/challenges/{challenge_id}?tab=submissions'
    for i in range(10):
        if driver.current_url != submisisons_url:
            print(
                f'Current url is {driver.current_url}. Connect to {submisisons_url}')
            driver.get(submisisons_url)

        time.sleep(60)
        screenshot('open_standings_page.png')

        # 順位表ロード待ち
        try:
            # 大分類(Rank User Score)
            # TODO 大分類が見つかったらtryの文脈から抜ける
            standings = driver.find_element_by_xpath(
                '//div[contains(text(), "Rank")]/..')

            # Rank, User, Scoreの存在をチェックする？
            # standings.find_element_by_xpath('./div[contains(text(), "Rank")]')
            # standings.find_element_by_xpath('./div[contains(text(), "User")]')
            # standings.find_element_by_xpath('./div[contains(text(), "Score")]')
        except NoSuchElementException as e:
            print(f'{i}th try is failure. Not loaded page yet.', e)
            continue

        # 順位表のカラムを構築
        try:
            # 小分類(Rank(Final Provisional), User(Rating Username), Score(Final Provisional Time))
            standings_titles = standings.find_element_by_xpath(
                'following-sibling::div')

            # 提出が無い時は順位表が表示されてても、
            standings_user = standings_titles.find_element_by_xpath(
                'following-sibling::div')

            titles = list()
            raw_titles = set()
            for e in standings_titles.find_elements_by_xpath('descendant::*[not(*)]'):
                text = e.text.strip()
                if not text:
                    continue

                # Final, Provisionalは2回出てきて、最初がRank、2度目がScore
                if text in raw_titles:
                    text = text + ' score'

                raw_titles.add(text)
                if text in ['Final', 'Provisional']:
                    text = text + ' rank'
                titles.append(text)

            titles.append('History')
        except NoSuchElementException as e:
            print('Empty competitor.', e)
            return (None, None)

        # 順位表をパース
        table = list()
        try:
            i = 0
            while True:
                print('user', i)
                userdata = defaultdict(str)
                column_index = 0
                for e in standings_user.find_elements_by_xpath('descendant::*[not(*)]'):
                    text = e.text.strip()
                    if text:
                        userdata[titles[column_index]] = text
                        column_index += 1
                table.append(userdata)
                standings_user = standings_user.find_element_by_xpath(
                    'following-sibling::div')
                i += 1
        except NoSuchElementException as e:
            print('End of users', e)

        return (titles, table)


init_driver()
login()

pg_db_url = f'postgresql://{pg_db_username}:{pg_db_password}@{pg_db_host}:{pg_db_port}/{pg_db_name}'
connection = psycopg2.connect(pg_db_url)

with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    cur.execute("select id, tc_match_id, enable_crawling from ms_crawling_match")
    crawling_matches = cur.fetchall()

with connection.cursor() as cur:
    for crawling_match in crawling_matches:
        print('crawling match', crawling_match)

        if not crawling_match['enable_crawling']:
            continue

        (titles, table) = get_standings(crawling_match['tc_match_id'])

        if titles == None:
            continue

        dt = datetime.now()
        stmt = f'''insert into ms_crawling(match_id, crawling_at) values({crawling_match['id']}, '{dt}') returning id'''
        cur.execute(stmt)
        crawling_id = cur.fetchone()[0]
        print('crawling', crawling_id, stmt)
        standings_no = 0
        for row in table:
            standings_no += 1
            final_rank = row['Final rank']
            provisional_rank = row['Provisional rank']
            rating = row['Rating']
            username = row['Username']
            final_score = row['Final score']
            provisional_score = row['Provisional score']
            time_at = row['Time']
            history = row['History']
            cur.execute(
                f'''insert into ms_standings(crawling_id, standings_no, final_rank, provisional_rank, rating, user_name, final_score, provisional_score, time_at, history)
                    values('{crawling_id}', {standings_no}, '{final_rank}', '{provisional_rank}', '{rating}', '{username}', '{final_score}', '{provisional_score}', '{time_at}', '{history}')''')
        connection.commit()


driver.quit()
