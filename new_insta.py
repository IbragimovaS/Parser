from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
import requests
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import ibm_db_dbi as db
import math
from selenium.webdriver.common.keys import Keys

headers = {
    'Host': 'www.instagram.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Proxy-Authorization': 'Basic YWNjZXNzX3Rva2VuOjFhMGRsaGhsOGpscmsydm9xMTE5OThsaGczcXVuZmY1a3A5cGpvNXRpdWM1bXNvN2UzN2g=',
    'Connection': 'keep-alive',
    'Cookie': 'mid=XNVcpAALAAFxMTvgNsJbBCdFa89U; shbid=7017; shbts=1558935177.2294877; datr=KGXVXIUh_zazlJ_o-ZB9Nh4Q; rur=FRC; urlgen="{\"95.59.139.133\": 9198}:1hVGQs:tCj1MFXdF2C8bqXM4naGKtY_jMc"; csrftoken=Po3tpumdgJVGfB9R2PLV3RBbvnZRC68P; ds_user_id=13114830691; sessionid=13114830691%3ANlcYOele3I5fGx%3A25',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}
def get_id_for_blog(url, headers, session=None):
    session = session or requests.Session()

    r = session.get(url, headers=headers)
    r_code = r.status_code
    #print(r)
    #print(r_code)
    if r_code == requests.codes.ok:
        # the code is 200 or valid
        return r.json()
    else:
        return None

def get_blog_data(data, n):
    if data is not None:
        time.sleep(0.7)
        inner_data = data.get('graphql', None)
        inner_data = inner_data.get('user', None)

        biography = inner_data['biography']
        number_of_followers = inner_data['edge_followed_by']['count']
        number_of_following = inner_data['edge_follow']['count']
        full_name = inner_data['full_name']
        channel_id = inner_data['id']
        channel_name = inner_data['username']
        posts_count = inner_data['edge_owner_to_timeline_media']['count']
        inserted_date = datetime.datetime.now()
        general_info = {
            'biography': biography,
            'number_of_followers': number_of_followers,
            'number_of_following': number_of_following,
            'full_name': full_name,
            'channel_id': channel_id,
            'channel_name': channel_name,
            'posts_count': posts_count
        }
        return general_info

        #print(general_info['channel_name']

chrome_options = Options()
chrome_options.add_argument('--lang=en')
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
#chrome_options.add_argument('--proxy-server=46.102.106.37:13228')
driver_path = "C:/Users/User/Desktop/chromedriver.exe"
browser = webdriver.Chrome(driver_path, options=chrome_options)
browser.get('https://www.instagram.com/accounts/login/')

username = "samat.ivanov"
password ="r2d2C3po"
#username = "saet.morozov"

browser.implicitly_wait(100)
try:
    cookies = 'C:/Users/User/Desktop/cookies.txt'
    with open(cookies, "a") as cookies_file:
        browser.add_cookie(cookies_file)
except:
    browser.find_element_by_xpath("//input[@name='username']").send_keys(username)
    browser.find_element_by_xpath("//input[@name='password']").send_keys(password)
    button = browser.find_element_by_xpath("//button[contains(.,'Log In')]")
    ActionChains(browser)\
        .move_to_element(button)\
        .click().perform()
    cookies = 'C:/Users/User/Desktop/cookies.txt'
    with open(cookies, "a") as cookies_file:
        cookies_file.write(str(browser.get_cookies()))
    sleep(1)


browser.find_element_by_xpath('//*[@id="react-root"]/div/div[2]/a[2]').click()

browser.find_element_by_xpath("//button[contains(.,'Not Now')]").click()
names = {
'diana_kz.13',
}
sleep(2)
connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
con = db.connect(connection_text, "", "")
cursor = con.cursor()

for name in names:
    browser.get('https://www.instagram.com/' + name)
    print('https://www.instagram.com/', name)
    sleep(1)
    try:
        number_of_followers = int(browser.find_element_by_xpath("//li[2]/a/span").get_attribute('title').replace(",", ""))
    except:
        number_of_followers = int(browser.find_element_by_xpath("//li[2]/a/span").get_attribute('title'))
    #CHANNEL_INFO
    data_blog = get_id_for_blog(url='https://www.instagram.com/' + name + '/?__a=1', headers=headers)
    channel_info = get_blog_data(data_blog, 0)
    channel_id = channel_info['channel_id']

    cursor.execute('select id from INSTA_CHANNEL_DATA where channel_id = \'{channel_id}\''.format(channel_id=channel_id))
    one_row = cursor.fetchone()
    #print(one_row)
    #print(channel_info['channel_id'])
    time.sleep(2)
    followers_panel = browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/header/section/ul/li[2]/a')
    ActionChains(browser)\
        .move_to_element(followers_panel)\
        .click().perform()
    sleep(2)
    followers_panel = browser.find_element_by_xpath('/html/body/div[3]/div/div[2]')
    print(number_of_followers, "_____")
    i = 0
    next_length = len(browser.find_elements_by_class_name('FPmhX'))

    while next_length != number_of_followers:

        next_length = len(browser.find_elements_by_class_name('FPmhX'))
        i += 1
        browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_panel)
        time.sleep(random.randint(100, 500) / 1000)
        followerlist = []
        print('___', next_length)
        profiles = browser.find_elements_by_class_name("FPmhX")
        k = 1
        for element in profiles:
            user_name = element.get_attribute('title')
            #print(user_name)
            cursor.execute('select id from INSTA_CHANNEL_DATA where channel_id = \'{channel_id}\' and user_name = \'{user_name}\''.format(channel_id=channel_id, user_name=user_name))
            row = cursor.fetchone()
            if row is None:
                try:
                    if element.get_property('href'):
                        profileurl = element.get_attribute('href')
                        profilename = element.get_attribute('title')
                        data_blog = get_id_for_blog(url='https://www.instagram.com/' + profilename + '/?__a=1',
                                                    headers=headers)
                        followers_data = get_blog_data(data_blog, k)
                        user_id = followers_data['channel_id']
                        user_name = followers_data['channel_name']
                        user_scr_name = followers_data['full_name']
                        user_url = profileurl
                        followed_by = followers_data['number_of_followers']
                        followed_to = followers_data['number_of_following']
                        try:
                            if one_row is None:
                                print('Insert into', channel_id, ' - ', user_id, 'object.')
                                sql = "insert into insta_channel_data(channel_id, user_id, user_name) values (?,?,?)"
                                cursor.execute(sql, (channel_id, user_id, user_name))
                                cursor.execute('select id from insta_followers_data where user_id = \'{user_id}\''.format(user_id=user_id))
                                one_row1 = cursor.fetchone()
                        except:
                            print(user_id, '______', user_name)
                        print("_______________", one_row1)
                        if one_row1 is None:
                            try:
                                print('Insert ', user_id, 'object into followers_data')
                                sql1 = "insert into insta_followers_data (user_id, user_name, user_scr_name, user_url, followed_by, followed_to) values (?,?,?,?,?,?)"
                                cursor.execute(sql1,
                                               (user_id, user_name, user_scr_name, user_url, followed_by, followed_to))
                            except:
                                print(user_id, '______', user_name)
                            k = k + 1
                except:
                    print("Smth wrong!")
                con.commit()
        if next_length > number_of_followers or math.fabs(next_length - number_of_followers) < 5:
            break

cursor.close()
con.close()
browser.close()


