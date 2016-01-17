from twitteraccess import *
import tweepy
import json
import csv
import nltk
import re
from tweepy import OAuthHandler
from collections import Counter
from nltk.corpus import stopwords
import string


#---------Authentication------------------------------------------

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
 
api = tweepy.API(auth)

#---------Collecting Data------------------------------------------

username = 'martinezmonica_'
count = 100

#stores my tweets; limited number not complete tweet count
myTweets = api.user_timeline(screen_name=username, count=count, include_rts = True)

###create csv from tweets
##outtweets = [[tweet.text.encode("utf-8")] for tweet in myTweets]
##
###output to csv file
##with open('martinezmonica_Tweets.csv', 'wb') as file:
##    writer = csv.writer(file)
##    writer.writerow(["id", "created_at", "text"])
##    writer.writerows(outtweets)

###---------Text Pre-Processing ------------------------------------------

#removed links and unwanted characters; left only text
wordlist = []
for item in myTweets:
    temp = item.text
    tweet = (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ", temp.lower()).split()))
    wordlist.extend(tweet.split())
#    print("%s \n" %tweet)

#remove stopwords
stop = stopwords.words('english') + ['rt', 'via']
filtered = [term for term in wordlist if term not in stop]

#determine word frequencies by adding words into counter object 
wordCount = Counter(filtered)

#prints top n words 
print(wordCount.most_common(10))
