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

user_id = {5835636444, 2061098745, 3438166282, 7931451763, 1469987603, 9963651551,1323343002, 225302172, 5924222665, 3650729351}
connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
con = db.connect(connection_text, "", "")
cursor = con.cursor()
for id in user_id:
    sql = 'select location_id, location_name from insta_followers_location where user_id = {user_id}'.format(user_id=id)
    df = pandas.read_sql(sql, con)
    df1 = df['LOCATION_ID'].values.tolist()
    df2 = df['LOCATION_NAME'].values.tolist()
    print(df)
    location_from_db = []
    location_name_db =[]
    for r in df1:
        location_from_db.append(r)
    for r in df2:
        location_name_db.append(r)
    print(location_from_db, '-', location_name_db)

    for i in range(len(location_from_db)):
        #
        location = str(location_from_db[i])
        location_name = location_name_db[i]
        #print(type(location))
        sql = 'select city_id, city_name from insta_locations where location_id = {location_id} or location_name = \'{location_name}\''.format(location_id=location, location_name=location_name)
        location_city = pandas.read_sql(sql, con)
        df1 = location_city['CITY_ID'].values.tolist()
        df2 = location_city['CITY_NAME'].values.tolist()
        print(df1, ' - ', df2)
cursor.close()
con.close()

