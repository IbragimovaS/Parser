import time
import requests
import instaloader
import datetime
import ibm_db_dbi as db

headers = {
    'Host': 'www.instagram.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Proxy-Authorization': 'Basic YWNjZXNzX3Rva2VuOjFhMGRsaGhsOGpscmsydm9xMTE5OThsaGczcXVuZmY1a3A5cGpvNXRpdWM1bXNvN2UzN2g=',
    'Connection': 'keep-alive',
    'Cookie': 'mid=XNVcpAALAAFxMTvgNsJbBCdFa89U; shbid=7017; shbts=1558613360.8308508; datr=KGXVXIUh_zazlJ_o-ZB9Nh4Q; rur=PRN; urlgen="{\"95.59.139.133\": 9198}:1hTmXA:97dsHBPwD1XcMLcUL0sbeOU_miU"; csrftoken=lA9XhctCIP1m7Zmy8Dbc2gtmfJv027qi; ds_user_id=13138309171; sessionid=13138309171%3ABudcvVrQbAsOph%3A27',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    'TE': 'Trailers'
}
L = instaloader.Instaloader()


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


def get_blog_data(data):
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

        # print(general_info['channel_name']


username = "ibragimova.s"
# password ="r2d2C3po"
# #username = "saet.morozov"
#
# L.login(username, password)  # (login)
L.two_factor_login()
session = instaloader.InstaloaderContext.get_anonymous_session()
# Obtain profile metadata
channel_id = '4141029510'
profile = instaloader.Profile.from_id(L.context, channel_id)

followers = profile.get_followers()

print(followers)

for user in followers:
    user.userid