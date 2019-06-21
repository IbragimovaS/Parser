import time
import datetime
from datetime import datetime as dt
import ibm_db_dbi as db
import pandas
import instaloader
import time
from itertools import dropwhile, takewhile
import urllib
from urllib.request import urlretrieve
import os
import requests
headers = {
    'Host': 'www.instagram.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Proxy-Authorization': 'Basic YWNjZXNzX3Rva2VuOjFrc2x1Y3JrdjM0MnNyMTRvdnVoNnJmbWU4NDRwNGlxMDNuNnZvODRrM2M0cXIycG1hOG0=',
    'Connection': 'keep-alive',
    'Cookie': 'datr=FB7tXBpjQ29_rp71GnC05Urg; sb=FB7tXA6tThGvm6NpoWvzHqOb',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}

def get_channels():

    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    sql = 'select user_id from channels_for_faces order by id limit(10) offset(424)'
    df = pandas.read_sql(sql, con)

    df['user_id'] = df['USER_ID'].str.replace("'", "")
    df1 = df['user_id'].values.tolist()
    print(df1)
    channels_from_db = []

    for r in df1:
        print(r)
        channels_from_db.append(r)
    return channels_from_db

def get_id_for_blog(url, headers, session=None):
    session = session or requests.Session()

    r = session.get(url, headers=headers)
    r_code = r.status_code
    # print(r)
    # print(r_code)
    if r_code == requests.codes.ok:
        # the code is 200 or valid
        return r.json()
    else:
        return None

def get_blog_data(data, n):
    if data is not None:
        time.sleep(1)
        inner_data = data.get('graphql', None)
        inner_data = inner_data.get('shortcode_media', None)

        if n != 1002:
            inner_data = inner_data.get('edge_sidecar_to_children', None)
            inner_data = inner_data.get('edges', None)
            post = inner_data[n]['node']
            try:
                accessibility_caption = post['accessibility_caption']
            except:
                accessibility_caption = 0
        else:
            try:
                accessibility_caption = inner_data['accessibility_caption']
            except:
                accessibility_caption = 0
        print(accessibility_caption)
        inserted_date = datetime.datetime.now()
        general_info = {
            'caption': accessibility_caption
        }
        return general_info

        # print(general_info['channel_name']

L = instaloader.Instaloader()
followers = get_channels()
connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
con = db.connect(connection_text, "", "")
cursor = con.cursor()
for follower_id in followers:
    person = instaloader.Profile.from_id(L.context, follower_id)
    time.sleep(2)
    count = person.mediacount
    if count > 100:
        stop = 100
    else:
        stop = count
    n = 1
    id = person.userid
    if person.is_private is False:
        if person.mediacount >= 50:
            newpath = r'C:/Users/User/PycharmProjects/post_downloads/faces/' + person.username
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            posts = person.get_posts()
            for post in posts:
                nodes = post.get_sidecar_nodes()
                itter = 0
                for node in nodes:
                    itter = itter + 1
                print(post.typename, itter)
                if itter is not 0:
                    i = 0;
                    for node in post.get_sidecar_nodes():
                        media_id = post.shortcode
                        data_blog = get_id_for_blog(url='https://www.instagram.com/p/' + media_id + '/?__a=1',headers=headers)
                        print('https://www.instagram.com/p/' + media_id + '/?__a=1')
                        post_data = get_blog_data(data_blog, i)
                        if node.is_video is not True:
                            if 'человек' in post_data['caption']:
                                print('OK')
                                destination = 'C:/Users/User/PycharmProjects/post_downloads/faces/' + post.owner_username + '/' + post.shortcode + str(i) + '.jpg'
                                url = node.display_url
                                urlretrieve(url, destination)
                                time.sleep(3)
                        i = i + 1
                    n = n + 1
                else:
                    media_id = post.shortcode
                    data_blog = get_id_for_blog(url='https://www.instagram.com/p/' + media_id + '/?__a=1', headers=headers)
                    print('https://www.instagram.com/p/' + media_id + '/?__a=1')
                    post_data = get_blog_data(data_blog, 1002)
                    if post.is_video is not True:
                        try:
                            if 'человек' in post_data['caption']:
                                print('OK')
                                destination = 'C:/Users/User/PycharmProjects/post_downloads/faces/' + post.owner_username + '/' + media_id + '.jpg'
                                url = post.url
                                urlretrieve(url, destination)
                                print(type(post.typename))
                                time.sleep(3)
                        except:
                            print('file not found')
                    n = n + 1
                if n > stop:
                   break
        else:
            print('User have less than 50 posts')
    else:
        print('Account is private')
        time.sleep(3)
