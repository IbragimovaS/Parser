import tweepy
import sys

consumer_key= 'VCwKiz8UHa4GNHrgkHBhPrtL8'
consumer_secret= '32GQN7EFIdaEMuWXZVZX2tsgtgwFjzkOhTbsLYJ01emOa6Zy3n'
access_token= '1126386395709419520-yirS4EPwOnDB7GF3RaCkMF2qtA4gnj'
access_token_secret= 'yHXaTjcKNDORhLpk3Eb06y5PeWx6LgDWgRlAnlIt6uPhk'

def tweet_url(t):
    return "https://twitter.com/%s/status/%s" % (t.user.screen_name, t.id)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
new_search = "Токаев -filter:retweets"
date_since = "2019-05-22"

replies = []

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

for full_tweets in tweepy.Cursor(api.search, q=new_search, since=date_since, timeout=9).items(10):
    img = full_tweets.entities.get('media')

   # img = img.get('media', None)
    #img = img['media_url']
    print('______', img)
    try:
        url_11=img[0]['media_url']
        print('PIKCHAA', url_11)
    except:
        print('asd')
    query = 'to:' + full_tweets.user.screen_name
    count = 0
    for twit in tweepy.Cursor(api.search, q=query, result_type='recent', timeout=9).items(1000):
        if hasattr(twit, 'in_reply_to_status_id_str'):
            if (twit.in_reply_to_status_id_str == full_tweets.id_str):
                replies.append(twit.text)
                count = count + 1
    print("Tweet :", full_tweets.text.translate(non_bmp_map), 'count: ', count)
    for elements in replies:
        print("Replies :", elements)
    replies.clear()
