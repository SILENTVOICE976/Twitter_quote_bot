import tweepy
import praw
import time
import sys
import random

reddit = praw.Reddit(client_id = '',
                     client_secret = '', 
                     user_agent = '',
                     username = '',
                     password = '')

FILE_NAME = 'lastseenmention.txt'

auth = tweepy.OAuthHandler('','')

auth.set_access_token('','')

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tweetNumber = 3
#INTERVAL = 60 * 60 * 12  # tweet every 12 hours
INTERVAL = 60  # every 15 seconds, for testing
terms = ["#programming","#javascript","#python"]
#get a tweet

def quote_tweet():
    subreddit = reddit.subreddit('quotes')
    hot_python = subreddit.hot(limit=10)

    for submission in hot_python:
        if not submission.stickied:
            if submission.score > 100:
                print('fetching quote from sub-reddit...')
                print(submission.title + ' - Upvotes >' + str(submission.score))
                quote = submission.title
                break
    return quote

#api.update_status('I am a bot and this is my first tweet')

def new_tweet():
    newTweet = quote_tweet() + '\n #quote ' + ' #quoteoftheday'
    print('posting new tweet...')
    try:
       api.update_status(newTweet)
       time.sleep(5)
    except tweepy.TweepError as e:
        print(e.reason)
        time.sleep(9)

#get all mentions

def read_last_seen(FILE_NAME):
    file_read = open(FILE_NAME, 'r')
    last_seen_id = int(file_read.read().strip())
    file_read.close()
    return last_seen_id

def store_last_seen(FILE_NAME, last_seen_id):
    file_write = open(FILE_NAME, 'w')
    file_write.write(str(last_seen_id))
    file_write.close()
    return 

#reply to mention with keyword hello

def reply_mention():
    print('replying to mentions...')
    tweets_mentions = api.mentions_timeline(read_last_seen(FILE_NAME), tweet_mode='extended')
    for tweet_mention in reversed(tweets_mentions):
        if 'hello' in tweet_mention.full_text.lower(): 
            try:
                print(str(tweet_mention.id) + ' - ' + tweet_mention.full_text)
                api.update_status("@" + tweet_mention.user.screen_name + " Thanks For tweeting at me :)", tweet_mention.id)
                api.create_favorite(tweet_mention.id)
                store_last_seen(FILE_NAME, tweet_mention.id)
                time.sleep(10)
            except tweepy.TweepError as e:
                print(e.reason)
                time.sleep(9)
                continue

#search hashtag and retweet method

def search_hashtag():
	# Find 'new' tweets (under hashtags/search terms)
    
    query = random.choice(terms)
    print("Searching under term..." + query)
    for tweet_hashtag in tweepy.Cursor(api.search, q=query, lang="en").items(tweetNumber):
        try:
            if (tweet_hashtag.user.followers_count < 100 and tweet_hashtag.user.statuses_count < 2500):
                print("Ignoring user " + tweet_hashtag.user.screen_name)
                continue
            else:
                tweet_hashtag.retweet()
                api.create_favorite(tweet_hashtag.id)
                print("Retweet Done!")
                print(tweet_hashtag.user.screen_name)
                time.sleep(10)
        except tweepy.TweepError as e:
            print(e.reason)
            time.sleep(9)
        except StopIteration:
            break

#follow user who follow you method

def follow_user():
    print ('following all followers...')
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
           try:
              follower.follow()
              time.sleep(10)
              print('Followed - '+ follower.screen_name)
           except tweepy.TweepError as e:
              print(e.reason)
              time.sleep(9)
              continue              

#ufollow user who doesnot follow you method

def unfollow_user():
    print ("Loading followers..")
    followers = []
    for follower in tweepy.Cursor(api.followers).items():
        followers.append(follower)

    print ("Found %s followers, finding friends.." % len(followers))
    friends = []
    for friend in tweepy.Cursor(api.friends).items():
        friends.append(friend)

    # creating dictionaries based on id's is handy too

    friend_dict = {}
    for friend in friends:
        friend_dict[friend.id] = friend

    follower_dict = {}
    for follower in followers:
        follower_dict[follower.id] = follower

    # now we find all your "non_friends" - people who don't follow you
    # even though you follow them.

    non_friends = [friend for friend in friends if friend.id not in follower_dict]

    print ("Unfollowing %s people who don't follow you back" % len(non_friends))
    
     #unfollow friends 

    for nf in non_friends:
        print ("Unfollowing %s" % nf.screen_name)
        try:
            nf.unfollow()
            time.sleep(10)
        except:
            print ("failed, sleeping for 15 minutes")
            time.sleep(9)
            continue


while True:
     search_hashtag()
     time.sleep(10)
     reply_mention()
     time.sleep(10)
     follow_user()
     time.sleep(10)
     unfollow_user()
     time.sleep(5)
     new_tweet()
     time.sleep(3)
     time.sleep(INTERVAL)