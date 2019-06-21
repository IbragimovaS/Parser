import requests
import json
import time
import datetime
import csv
import ibm_db_dbi as db
import pandas

tag = 'ny'
url = 'http://www.instagram.com/explore/tags/' + tag + '/?__a=1'
url_for_each_post = 'https://www.instagram.com/p/'
headers = {
    'Host': 'www.instagram.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Proxy-Authorization': 'Basic YWNjZXNzX3Rva2VuOjFhMGRsaGhsOGpscmsydm9xMTE5OThsaGczcXVuZmY1a3A5cGpvNXRpdWM1bXNvN2UzN2g=',
    'Connection': 'keep-alive',
    'Cookie': 'csrftoken=hqAZ4VaSOM0bg000vFF55FLIPnPHa7eM; rur=FTW; mid=XNVcpAALAAFxMTvgNsJbBCdFa89U; shbid=13034; shbts=1557488860.1422455; ds_user_id=13144385380; sessionid=13144385380%3Ack3TntdQYToGZQ%3A27;',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}

keys = ['id', 'owner', 'display_url', 'edge_liked_by', 'edge_media_to_comment', 'shortcode', 'edge_media_to_caption',
        'accessibility_caption', 'is_video', 'text']
def get_channels():
    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    sql = 'select channel_name from tl_media_channels where source_id = 1002 order by id limit(23) offset(50)'
    df = pandas.read_sql(sql, con)

    df['channel_name_wa'] = df['CHANNEL_NAME'].str.replace("'", "")
    df1 = df['channel_name_wa'].values.tolist()
    print(df1)
    channels_from_db = []
    #print("___________",count)
    for r in df1:
        print(r)
        channels_from_db.append(r)
    return channels_from_db

def jprint(data_dict):
    print(json.dumps(data_dict, indent=4))


def get_id_page(url, headers, session=None):
    print(url)
    session = session or requests.Session()

    r = session.get(url, headers=headers)
    r_code = r.status_code
    # print(r)
    print(r_code)
    if r_code == requests.codes.ok:
        # the code is 200 or valid
        return r
    else:
        return None


def get_id_for_blog(url, headers, session=None):
    print(url)
    session = session or requests.Session()

    r = session.get(url, headers=headers)
    r_code = r.status_code
    # print(r)
    print(r_code)
    if r_code == requests.codes.ok:
        # the code is 200 or valid
        return r.json()
    else:
        return None


def get_tag_data(data):
    filtered_data = []
    if data is not None:
        inner_data = data.json()
        inner_data = inner_data.get('graphql', None)
        inner_data = inner_data.get('hashtag', None)

        # getting top posts
        top_posts = inner_data.get('edge_hashtag_to_top_posts', None)
        if top_posts is not None:
            top_posts = top_posts.get('edges')

        # getting recent posts
        recent_posts = inner_data.get('edge_hashtag_to_media', None)
        if recent_posts is not None:
            recent_posts_count = recent_posts.get('count')
            recent_posts = recent_posts.get('edges')

        all_posts = top_posts + recent_posts

        filtered_data = []
        for post in all_posts:
            post = post.get('node', None)
            try:
                post_id = post['id']
            except:
                post_id = 0

            try:
                date = datetime.datetime.fromtimestamp(int(post['taken_at_timestamp'])).strftime('%d-%m-%Y-%H:%M:%S')
            except:
                date = ''

            try:
                timestamp = post['taken_at_timestamp']
            except:
                timestamp = ''

            try:
                likes = post['edge_liked_by']['count']
            except:
                likes = 0

            try:
                comments_count = post['edge_media_to_comment']['count']
            except:
                comments_count = 0

            try:
                accessibility_caption = post['accessibility_caption']
            except:
                accessibility_caption = 0

            try:
                text = post['edge_media_to_caption']['edges']
                try:
                    text = text[0]['node']['text']
                except:
                    text = ''
            except:
                text = ''

            try:
                owner_id = post['owner']['id']
            except:
                owner_id = ''

            try:
                display_url = post['display_url']
            except:
                display_url = ''

            try:
                shortcode = post['shortcode']
                post_url = 'https://www.instagram.com/p/' + shortcode + '/'
            except:
                shortcode = ''

            try:
                views_count = post['video_view_count']
                #print(views_count)
            except:
                views_count = 0

            filtered_post = {
                'post_id': post_id,
                'shortcode': shortcode,
                'date': date,
                'timestamp': timestamp,
                'likes': likes,
                'comments_count': comments_count,
                'text': text,
                'accessibility_caption': accessibility_caption,
                'display_url': display_url,
                'views': views_count,
                'post_url': post_url,
                'owner_id': owner_id,
                'owner_login': ''
            }
            filtered_data.append(filtered_post)
    return filtered_data, recent_posts_count


def get_blog_data(data):
    filtered_data = []
    posts_count = []
    if data is not None:
        inner_data = data.get('graphql', None)
        inner_data = inner_data.get('user', None)

        general_info = {
            'biography': inner_data['biography'],
            'number_of_followers': inner_data['edge_followed_by']['count'],
            'full_name': inner_data['full_name'],
            'person_id': inner_data['id'],
            'posts_count': inner_data['edge_owner_to_timeline_media']['count']
        }

        all_posts = inner_data['edge_owner_to_timeline_media']['edges']
        posts_count = inner_data['edge_owner_to_timeline_media']['count']

        filtered_data = []
        for post in all_posts:
            post = post.get('node', None)
            try:
                post_id = post['id']
            except:
                post_id = 0

            try:
                date = datetime.datetime.fromtimestamp(int(post['taken_at_timestamp'])).strftime('%d-%m-%Y-%H:%M:%S')
            except:
                date = ''

            try:
                timestamp = post['taken_at_timestamp']
            except:
                timestamp = ''

            try:
                likes = post['edge_liked_by']['count']
            except:
                likes = 0

            try:
                comments_count = post['edge_media_to_comment']['count']
            except:
                comments_count = 0

            try:
                accessibility_caption = post['accessibility_caption']
            except:
                accessibility_caption = 0

            try:
                text = post['edge_media_to_caption']['edges']
                try:
                    text = text[0]['node']['text']
                except:
                    text = ''
            except:
                text = ''

            try:
                owner_id = post['owner']['id']
            except:
                owner_id = ''

            try:
                display_url = post['display_url']
            except:
                display_url = ''

            try:
                shortcode = post['shortcode']
                post_url = 'https://www.instagram.com/p/' + shortcode + '/'
            except:
                shortcode = ''
            try:
                location = post['location']['name']
            except:
                location = ''

            # try:
            #     view_count = ['edge_sidecar_to_children']['']
            # except:
            #     view_count = ''

            filtered_post = {
                'post_id': post_id,
                'shortcode': shortcode,
                'date': date,
                'timestamp': timestamp,
                'likes': likes,
                'comments_count': comments_count,
                'text': text,
                'accessibility_caption': accessibility_caption,
                'display_url': display_url,
                'post_url': post_url,
                'owner_id': owner_id,
                'owner_login': '',
                'location': location
            }
            filtered_data.append(filtered_post)
    return filtered_data, posts_count

def get_comments_to_post(post_url):
    data_dict = get_id_page(post_url, headers)
    # get_id_for_blog
    # data_dict = get_id_for_blog(post_url, headers)
    if data_dict is not None:
        data_dict = data_dict.json()
        # jprint(data_dict)

        data = data_dict['graphql']['shortcode_media']
        post_id = data['id']
        # jprint(data)
        try:
            comments_count = data['edge_media_to_comment']['count']
            all_comments = data['edge_media_to_comment']['edges']
        except:
            comments_count = data['edge_media_to_parent_comment']['count']
            all_comments = data['edge_media_to_parent_comment']['edges']

        text_to_post = data['edge_media_to_caption']['edges']
        try:
            text_to_post = text_to_post[0]
            text_to_post = text_to_post['node']['text']
        except:
            text_to_post = ''

        filtered_comments = []
        # post['owner_login'] = data['owner']['username']

        for comment in all_comments:
            # print(comment)
            comment = comment['node']
            try:
                comment_id = comment['id']
            except:
                comment_id = 0

            try:
                text = comment['text']
            except:
                text = ''

            try:
                date = datetime.datetime.fromtimestamp(int(comment['created_at'])).strftime('%d-%m-%Y-%H:%M:%S')
            except:
                date = ''

            try:
                timestamp = comment['created_at']
            except:
                timestamp = ''

            try:
                person_id = comment['owner']['id']
            except:
                person_id = 0

            try:
                person_login = comment['owner']['username']
                person_url = 'https://www.instagram.com/' + person_login
            except:
                person_login = ''

            try:
                likes = comment['edge_like_by']['count']
            except:
                likes = 0

            filtered_comment = {
                'post_id': post_id,
                'post_url': post_url,
                'post_owner_id': data['owner']['id'],
                'comment_id': comment_id,
                'text': text,
                'date': date,
                'timestamp': timestamp,
                'likes': likes,
                'person_id': person_id,
                'person_login': person_login,
                'person_url': person_url
            }
            filtered_comments.append(filtered_comment)

        return filtered_comments, comments_count
    else:
        comments_count = 0
        filtered_comment = {
            'post_id': 'No access',
            'post_url': 'No access',
            'post_owner_id': 'No access',
            'comment_id': 'No access',
            'text': 'No access',
            'date': '00-00-0000-00:00:00',
            'timestamp': 'No access',
            'likes': 0,
            'person_id': 'No access',
            'person_login': 'No access',
            'person_url': 'No access'
        }
        return filtered_comment, comments_count


def get_comments_to_all_posts(all_posts):
    all_comments = []
    additional_post_info = []

    for post in all_posts:
        post_url = post['post_url']
        time.sleep(0.6)

        comments_to_post, count = get_comments_to_post(post_url + '?__a=1')
        print('We have', count, 'comments on', post_url, 'post.')
        for comments in comments_to_post:
            all_comments.append(comments)

    return all_comments


def write_posts_csv(data, filename='/home/ruslan/PycharmProjects/posts_insta.csv', encoding='utf-8'):
    """Recieves data as list of dictionaries, the file name as a string with format,
    encoding by default utf-8, returns csv file"""
    with open(filename, 'a', newline='', encoding=encoding) as csvfile:
        fieldnames = ['post_id', 'shortcode', 'date', 'timestamp', 'likes', 'comments_count', 'text',
                      'accessibility_caption', 'display_url', 'post_url', 'owner_id']

        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames, extrasaction='ignore')

        # writer.writeheader()

        writer.writerows(data)

        print('Data written to csv, filename')

    csvfile.close()


def write_comments_csv(data, filename='/home/ruslan/PycharmProjects/comments_insta.csv', encoding='utf-8'):
    """Recieves data as list of dictionaries, the file name as a string with format,
    encoding by default utf-8, returns csv file"""
    with open(filename, 'a', newline='', encoding=encoding) as csvfile:
        fieldnames = ['post_id', 'post_owner_id', 'comment_id', 'text', 'date', 'timestamp', 'likes', 'person_id',
                      'person_login', 'person_url']

        writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames, extrasaction='ignore')

        # writer.writeheader()

        writer.writerows(data)

        print('Data written to csv, filename')

    csvfile.close()


def insert_into_db_test(posts):
    #connection_text = "DATABASE=sample;HOSTNAME=192.168.2.17;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=1q2w3e4R;"
    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    for row in posts:
        object_id = row.get('post_id')
        cursor.execute(
            'select object_id from tl_media_data_inst where object_id = \'{object_id}\''.format(object_id=object_id))
        one_row = cursor.fetchone()
        # print(object_id)
        if one_row is not None:
            print('Update {object_id} object.'.format(object_id=object_id), datetime.datetime.now())

            #object_id = row.get('post_id', 'null')
            inserted_date = datetime.datetime.now()
            date = "\'" + row.get('date')[6:10] + row.get('date')[2:6] + row.get('date')[:2] + " " + row.get('date')[11:] + ".0\'"
            channel_id = row.get('owner_id', 'null')
            likes = row.get('likes', 'null')
            comments = row.get('comments_count', 'null')
            caption = "\'" + str(row.get('accessibility_caption', 'null')) + "\'"
            text = "\'" + row.get('text', 'null').replace("'", "\"").replace("\n", " ").replace(",", "") + "\'"
            url_attachment = "\'" + row.get('display_url', 'null').replace("'", "''").replace(",", "") + "\'"
            url_channel = "\'" + row.get('post_url', 'null').replace("'", "''").replace(",", "") + "\'"
            source_id = 2

            sql_update = "update tl_media_data_inst set likes = {likes}, comments = {comments} where object_id = \'{object_id}\'".format(likes=likes, comments=comments, caption=caption, object_id=object_id)

            sql_history_test = "insert into tl_media_data_inst_history (object_id, inserted_date, published_date, channel_id, likes, comments, caption, text, url_attachment, url_channel, source_id) values (?,?,?,?,?,?,?,?,?,?,?)"

            cursor.execute(sql_history_test, (object_id, inserted_date, date, channel_id, likes, comments, caption, text, url_attachment, url_channel, source_id))

            cursor.execute(sql_update)
        else:
            print('Insert ', object_id, 'object.', datetime.datetime.now())

            #object_id = row.get('post_id', 'null')
            date = "\'" + row.get('date')[6:10] + row.get('date')[2:6] + row.get('date')[:2] + " " + row.get('date')[11:] + ".0\'"
            channel_id = row.get('owner_id', 'null')
            likes = row.get('likes', 'null')
            comments = row.get('comments_count', 'null')
            caption = "\'" + str(row.get('accessibility_caption', 'null')) + "\'"
            text = "\'" + row.get('text', 'null').replace("'", "\"").replace("\n", " ").replace(",", "") + "\'"
            url_attachment = "\'" + row.get('display_url', 'null').replace("'", "''").replace(",", "") + "\'"
            url_channel = "\'" + row.get('post_url', 'null').replace("'", "''").replace(",", "") + "\'"
            source_id = 2

            sql_1_test = "insert into tl_media_data_inst (object_id, published_date, channel_id, likes, comments, caption, text, url_attachment, url_channel, source_id) values (?,?,?,?,?,?,?,?,?,?)"

            cursor.execute(sql_1_test, (
            object_id, date, channel_id, likes, comments, caption, text, url_attachment, url_channel, source_id))

        con.commit()
    cursor.close()
    con.close()


def insert_into_db_test_com(comments):
    #connection_text = "DATABASE=sample;HOSTNAME=192.168.2.23;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=1q2w3e4R;"
    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    for comment in comments:
        try:
            # ['post_id', 'post_owner_id', 'comment_id', 'text', 'date', 'timestamp', 'likes','person_id', 'person_login', 'person_url']
            comment_id = comment['comment_id']
            cursor.execute('select comment_id from tl_media_comments_inst where comment_id = \'{comment_id}\''.format(
                comment_id=comment_id))
            one_row = cursor.fetchone()
            # print(comment_id)
            if one_row is not None:
                print('Update {comment_id} comment.'.format(comment_id=comment_id), datetime.datetime.now())

                likes = comment.get('likes', 'null')
                # text = "\'" + comment.get('text', 'null').replace("'", "''").replace("\n", " ").replace(",", "") + "\'"

                sql_update = "update tl_media_comments_inst set comment_likes = {likes} where comment_id = \'{comment_id}\'".format(
                    likes=likes, comment_id=comment_id)

                cursor.execute(sql_update)
            else:
                print('Insert ', comment_id, 'comment.', datetime.datetime.now())

                #comment_id = comment.get('comment_id', 'null')
                date = "\'" + comment.get('date')[6:10] + comment.get('date')[2:6] + comment.get('date')[:2] + " " + comment.get('date')[11:] + ".0\'"
                object_id = comment.get('post_id', 'null')
                likes = comment.get('likes', 'null')
                text = "\'" + comment.get('text', 'null').replace("'", "\"").replace("\n", " ").replace(",", "") + "\'"
                author_id = comment.get('person_id', 'null')
                author_name = comment.get('person_login', 'null')
                author_url = comment.get('person_url', 'null')

                sql_1_test = "insert into tl_media_comments_inst (comment_id, published_date, object_id, comment_likes, comment_text,author_id,author_name, author_url, source_id) values (?,?,?,?,?,?,?,?,?)"

                cursor.execute(sql_1_test,
                               (comment_id, date, object_id, likes, text, author_id, author_name, author_url, '2'))

            con.commit()
        except:
            jprint(comment)

    cursor.close()
    con.close()

def insert_into_db_negative(posts):
    #connection_text = "DATABASE=sample;HOSTNAME=192.168.2.17;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=1q2w3e4R;"
    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    for row in posts:
        object_id = row.get('post_id')
        cursor.execute(
            'select object_id from tl_media_data_inst where object_id = \'{object_id}\''.format(object_id=object_id))
        one_row = cursor.fetchone()
        # print(object_id)
        if one_row is not None:
            print('Update {object_id} object.'.format(object_id=object_id), datetime.datetime.now())

            inserted_date = datetime.datetime.now()
            #object_id = row.get('post_id', 'null')
            date = "\'" + row.get('date')[6:10] + row.get('date')[2:6] + row.get('date')[:2] + " " + row.get('date')[11:] + ".0\'"
            channel_id = row.get('owner_id', 'null')
            likes = row.get('likes', 'null')
            comments = row.get('comments_count', 'null')
            caption = "\'" + str(row.get('accessibility_caption', 'null')) + "\'"
            text = "\'" + row.get('text', 'null').replace("'", "\"").replace("\n", " ").replace(",", "") + "\'"
            url_attachment = "\'" + row.get('display_url', 'null').replace("'", "''").replace(",", "") + "\'"
            url_channel = "\'" + row.get('post_url', 'null').replace("'", "''").replace(",", "") + "\'"
            views_count = row.get('views','null')
            source_id = 1002
            post_location = row.get('location', 'null')
            print('location update__________', post_location)

            sql_update = "update tl_media_data_inst set likes = {likes}, comments = {comments}, views = {views}, location=\'{location}\' where object_id = \'{object_id}\'".format(likes=likes, comments=comments, views=views_count, caption=caption, location=post_location, object_id=object_id)

            sql_history_test = "insert into tl_media_data_inst_history (object_id, inserted_date, published_date, channel_id, likes, comments, views, caption, text, url_attachment, url_channel, source_id, location) values (?,?,?,?,?,?,?,?,?,?,?,?,?)"

            cursor.execute(sql_history_test, (object_id, inserted_date, date, channel_id, likes, comments, views_count, caption, text, url_attachment, url_channel, source_id, post_location))

            cursor.execute(sql_update)
        else:
            print('Insert ', object_id, 'object.', datetime.datetime.now())

            inserted_date = datetime.datetime.now()
            object_id = row.get('post_id', 'null')
            date = "\'" + row.get('date')[6:10] + row.get('date')[2:6] + row.get('date')[:2] + " " + row.get('date')[11:] + ".0\'"
            channel_id = row.get('owner_id', 'null')
            likes = row.get('likes', 'null')
            comments = row.get('comments_count', 'null')
            caption = "\'" + str(row.get('accessibility_caption', 'null')) + "\'"
            text = "\'" + row.get('text', 'null').replace("'", "\"").replace("\n", " ").replace(",", "") + "\'"
            url_attachment = "\'" + row.get('display_url', 'null').replace("'", "''").replace(",", "") + "\'"
            url_channel = "\'" + row.get('post_url', 'null').replace("'", "''").replace(",", "") + "\'"
            views_count = row.get('views', 'null')
            source_id = 1002

            post_location = row.get('location', 'null')
            print('location update__________', post_location)

            sql_1_test = "insert into tl_media_data_inst (object_id, published_date, channel_id, likes, comments,views, caption, text, url_attachment, url_channel, source_id, location) values (?,?,?,?,?,?,?,?,?,?,?,?)"

            sql_history_test = "insert into tl_media_data_inst_history (object_id, inserted_date, published_date, channel_id, likes, comments,views, caption, text, url_attachment, url_channel, source_id, location) values (?,?,?,?,?,?,?,?,?,?,?,?,?)"

            cursor.execute(sql_history_test, (object_id, inserted_date, date, channel_id, likes, comments,views_count, caption, text, url_attachment, url_channel,source_id, post_location))

            cursor.execute(sql_1_test, (object_id, date, channel_id, likes, comments,views_count, caption, text, url_attachment, url_channel, source_id,post_location))

        con.commit()
    cursor.close()
    con.close()

def insert_into_db_negative_com(comments):
    #connection_text = "DATABASE=sample;HOSTNAME=192.168.2.23;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=1q2w3e4R;"
    connection_text = "DATABASE=PRODDB;HOSTNAME=192.168.252.11;PORT=50000;PROTOCOL=TCPIP;UID=db2inst1;PWD=Qjuehnghj1;"
    con = db.connect(connection_text, "", "")
    cursor = con.cursor()
    for comment in comments:
        try:
            # ['post_id', 'post_owner_id', 'comment_id', 'text', 'date', 'timestamp', 'likes','person_id', 'person_login', 'person_url']
            comment_id = comment['comment_id']
            cursor.execute('select comment_id from tl_media_comments_inst where comment_id = \'{comment_id}\''.format(
                comment_id=comment_id))
            one_row = cursor.fetchone()
            # print(comment_id)
            if one_row is not None:
                print('Update {comment_id} comment.'.format(comment_id=comment_id), datetime.datetime.now())

                likes = comment.get('likes', 'null')
                # text = "\'" + comment.get('text', 'null').replace("'", "''").replace("\n", " ").replace(",", "") + "\'"

                sql_update = "update tl_media_comments_inst set comment_likes = {likes} where comment_id = \'{comment_id}\'".format(likes=likes, comment_id=comment_id)

                cursor.execute(sql_update)
            else:
                print('Insert ', comment_id, 'comment.', datetime.datetime.now())

                comment_id = comment.get('comment_id', 'null')
                date = "\'" + comment.get('date')[6:10] + comment.get('date')[2:6] + comment.get('date')[:2] + " " + comment.get('date')[11:] + ".0\'"
                object_id = comment.get('post_id', 'null')
                likes = comment.get('likes', 'null')
                text = "\'" + comment.get('text', 'null').replace("'", "\"").replace("\n", " ").replace(",", "") + "\'"
                author_id = comment.get('person_id', 'null')
                author_name = comment.get('person_login', 'null')
                author_url = comment.get('person_url', 'null')

                sql_1_test = "insert into tl_media_comments_inst (comment_id, published_date, object_id, comment_likes, comment_text,author_id,author_name, author_url, source_id) values (?,?,?,?,?,?,?,?,?)"

                cursor.execute(sql_1_test,
                               (comment_id, date, object_id, likes, text, author_id, author_name, author_url, '1002'))

            con.commit()
        except:
            jprint(comment)

    cursor.close()
    con.close()


key_words = {
#     'уменяестьвыбор',
#     'отправдынеубежишь',
#     'бессмертныйполк',
#     'шалкет',
#     'уменяестьголос',
#     'новостикз',
#     'новостиалматы',
# 'двк',
# 'назарбаев',
# 'аблязов',
# 'диктатура',
# 'экстримисты',
# 'экстримизм',
# 'террористы',
# 'несправедливость',
# 'революция',
# 'Ihaveachoice',
# 'forafairelectio',
# 'toqayevteam',
    'менояндым',
}
while True:
    # channels_from_db = get_channels()
    # print(channels_from_db)
    # for neg_blog in channels_from_db:
    #     data_blog = get_id_for_blog(url='https://www.instagram.com/' + neg_blog + '/?__a=1', headers=headers)
    #
    #     all_posts_blog, posts_count_blog = get_blog_data(data_blog)
    #
    #     print('We have', posts_count_blog, 'posts on this blog.')
    #     all_comments = get_comments_to_all_posts(all_posts_blog)
    #     insert_into_db_negative(all_posts_blog)
    #     insert_into_db_negative_com(all_comments)

    for word in key_words:
        data_word = get_id_page(url='http://www.instagram.com/explore/tags/' + word + '/?__a=1', headers=headers)

        all_posts_tag, posts_count_tag = get_tag_data(data_word)

        print('We have', posts_count_tag, 'posts with this tag')
        all_comments = get_comments_to_all_posts(all_posts_tag)
        insert_into_db_negative(all_posts_tag)
        insert_into_db_test_com(all_comments)





















