# @author Monica Martinez | mtzmonica.com
#
# Uses tweepy and python to faciliated twitter user tweet/status processing:
#   collects and prints most tweeted words, hastags, and users.
#
from twitteraccess import *
import tweepy
import csv
import nltk
import re
from tweepy import OAuthHandler
from collections import Counter
from nltk.corpus import stopwords


#---------Authentication------------------------------------------

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

#---------Collecting Data------------------------------------------

#set count to a resonable number as to not exceed twitter rate limits [300tweets/15min]
username = 'martinezmonica_'
#count = 100, pages = 100 ==> 3192
count = 150
TWEETS = []

#stores my tweets; limited number not complete tweet count; By ITEM vs by PAGE
#TWEETS = tweepy.Cursor(api.user_timeline, screen_name = username, include_rts = False).items(count)

pages = tweepy.Cursor(api.user_timeline, screen_name = username).pages(count)
for i in pages:
    TWEETS = TWEETS + i
        

def to_csv(myTweets):
    outtweets = [[tweet.text.encode("utf-8")] for tweet in TWEETS]
    with open('martinezmonica_Tweets.csv', 'wb') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "created_at", "text"])
        writer.writerows(outtweets)

#-------------------------------------------------------------------

def preprocess(use_w_hashtag=True, use_w_at=True):
    count = 0
    wordlist = []
    for item in TWEETS:
        text = item.text
        count = count+1
        #Convert to lowercase
        tweet = text.lower()

        #Remove www.* or https?://*
        tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))'," ",tweet)

        #Convert hashtag to word
        if use_w_hashtag == False:           
            tweet = re.sub(r'#([^\s]+)', r'\1',tweet)

        if use_w_at == False:
            tweet = re.sub('(@[A-Za-z0-9]+)',' ', tweet) 
            
        wordlist.extend(tweet.split())

    #remove stopwords
    stop = stopwords.words('english') + ['rt', 'via', 'u', 'r', 'b', '2']
    filtered_final = [term for term in wordlist if term not in stop]
    print("%d \n" %count)
    return filtered_final

def top_words(n):   
    WORDS = Counter(preprocess(use_w_hashtag=False, use_w_at=False)).most_common(n)
    for word, num in WORDS:
        print("%s : %d" %(word, num))

def top_hashtags(n):
    wordlist = preprocess()
    hastags = [word for word in wordlist if word.startswith('#')]
    for word,num in Counter(hastags).most_common(n):
         print("%s : %d" %(word, num))

def top_mentioned(n):
    wordlist = preprocess()
    hastags = [word for word in wordlist if word.startswith('@')]
    for word,num in Counter(hastags).most_common(n):
         print("%s : %d" %(word, num))    

#top_mentioned(10)

