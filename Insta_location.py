import time
import requests
from time import sleep
import datetime
import ibm_db_dbi as db
import pandas

headers = {
    'Host': 'www.instagram.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Proxy-Authorization': 'Basic YWNjZXNzX3Rva2VuOjFhMGRsaGhsOGpscmsydm9xMTE5OThsaGczcXVuZmY1a3A5cGpvNXRpdWM1bXNvN2UzN2g=',
    'Connection': 'keep-alive',
    'Cookie': 'XNVcpAALAAFxMTvgNsJbBCdFa89U; shbid=10592; shbts=1558345962.282848; datr=KGXVXIUh_zazlJ_o-ZB9Nh4Q; rur=PRN; urlgen="{\"95.59.139.133\": 9198}:1hSwjH:b5wKKANZ7D4O6s6RJWPnFpgWFvo"; csrftoken=GLr0ww2dU2qgw6hPQrqLI0RTotiRDdKK; ds_user_id=13114830691; sessionid=13114830691%3A6eNgWrNfq5nahe%3A29',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}

def get_channels():
    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    sql = 'select user_name FROM DB2INST1.insta_followers_data'
    df = pandas.read_sql(sql, con)
    df['channel_id_wa'] = df['USER_NAME'].str.replace("'", "")
    df1 = df['channel_id_wa'].values.tolist()
    channels_from_db = []
    for r in df1:
        channels_from_db.append(r)
    return channels_from_db

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
        channel_id = inner_data['id']
        channel_name = inner_data['username']
        posts_count = inner_data['edge_owner_to_timeline_media']['count']
        edges = inner_data['edge_owner_to_timeline_media']['edges']
        inserted_date = datetime.datetime.now()
        general_info = {
            'channel_id': channel_id,
            'channel_name': channel_name,
            'posts_count': posts_count,
            'edges': edges
        }
        return general_info

def get_post_location(data, n):
    if data is not None:
        time.sleep(0.7)
        inner_data = data.get('node', None)

        if inner_data['location'] != None:
            location = inner_data['location']['name']
            location_id = inner_data['location']['id']
        else:
            location = None
            location_id = None
        posts_location = {
            'location': location,
            'location_id': location_id,
        }
        return posts_location

sleep(2)

names = get_channels()
connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
con = db.connect(connection_text, "", "")
cursor = con.cursor()

for name in names:
    try:
        #CHANNEL_INFO
        print(name)
        data_blog = get_id_for_blog(url='https://www.instagram.com/' + name + '/?__a=1', headers=headers)
        channel_info = get_blog_data(data_blog, 0)
        edges = channel_info['edges']
        user_id = channel_info['channel_id']
        cursor.execute('select user_id from insta_followers_location where user_id = \'{user_id}\''.format(user_id=user_id))
        one_row = cursor.fetchone()
        for edge in edges:
            location_post = get_post_location(edge, 0)
            location_id = location_post['location_id']
            location_name = location_post['location']

            if one_row is None:
                print('Insert into', channel_info['channel_id'], "-", location_id, '-', location_name)
                sql = "insert into insta_followers_location (user_id, location_name, location_id) values (?,?,?)"
                cursor.execute(sql, (user_id, location_name, location_id))
        con.commit()
    except:
        print("User", name, "not found!")
cursor.close()
con.close()

