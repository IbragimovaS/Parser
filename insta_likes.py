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
def get_channels():

    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    sql = 'select channel_id from tl_media_channels where source_id = 1002 order by id limit(10)'
    df = pandas.read_sql(sql, con)

    df['channel_id'] = df['CHANNEL_ID'].str.replace("'", "")
    df1 = df['channel_id'].values.tolist()
    print(df1)
    channels_from_db = []

    for r in df1:
        print(r)
        channels_from_db.append(r)
    return channels_from_db


L = instaloader.Instaloader()


channel_id = {'5644930763'}

connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
con = db.connect(connection_text, "", "")
cursor = con.cursor()

for id in channel_id:

    print('Downloading posts from ', id)
    profile = instaloader.Profile.from_id(L.context, id)
    group_name = profile.username
    group_id = str(profile.userid)
    count = profile.mediacount
    posts = profile.get_posts()
    print(count)
    if count > 100:
        stop = 100
    else:
        stop = count

    n = 1
    newpath = r'C:/Users/User/PycharmProjects/post_downloads/Media/' + profile.username
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    for post in posts:

        likes = post.get_likes()
        for like in likes:
            user_name = like.username
            user_id = str(like.userid)
            count = 1
            print(user_name, ' ', user_id)
            time.sleep(1)
            cursor.execute('select count from insta_like_counter where user_id = \'{user_id}\' and group_id = \'{group_id}\''.format(user_id=user_id, group_id=group_id))
            one_row = cursor.fetchone()

            if one_row is not None:
                count = one_row[0] + 1
                print('Update {user_id} object.'.format(user_id=user_id), datetime.datetime.now())
                sql_update = "update insta_like_counter set count = {count} where user_id = \'{user_id}\' and group_id = \'{group_id}\'".format(count=count, user_id=user_id, group_id=group_id)
                cursor.execute(sql_update)
            else:
                print('Insert ', user_id, 'object.', datetime.datetime.now())
                sql_1_test = "insert into insta_like_counter(group_name, group_id, user_id, user_name, count) values (?,?,?,?,?)"
                cursor.execute(sql_1_test, (group_name, group_id, user_id, user_name, count))
            con.commit()

cursor.close()
con.close()