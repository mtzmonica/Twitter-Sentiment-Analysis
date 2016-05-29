import pandas
import matplotlib.pyplot as plt
import numpy as np

import nltk
import tweepy

import json
import csv
import re
from twitteraccess import *
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

#--------------------AUTHENTICATION---------------------------------


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

#-------------------------------------------------------------------

#specify: number of tweets to get (MAX), the query string (hashtag) 
def get_public_tweets(MAX, queryStr):
    data = tweepy.Cursor(api.search, q=queryStr, lang ='en').items(MAX)
    # save tweets: text, location
    tweets = []
    for tweet in data:
        decoded = json.loads(json.dumps(tweet._json)) 
        #text = decoded['text'].enccode('ascii', 'ignore')
        tweets.append(decoded['text'].encode('ascii', 'ignore'))
    print "Got public tweets for %s" % (queryStr)
    return tweets

def get_user_tweets(MAX, username):
    data = tweepy.Cursor(api.user_timeline, screen_name = username, include_rts = False).items(MAX)
    tweets = []
    for tweet in data:
        decoded = json.loads(json.dumps(tweet._json))
        tweets.append(decoded['text'].encode('ascii', 'ignore'))
    print "Got user tweets for %s" % (username)
    return tweets

def to_csv(name, TWEETS):
    #outtweets = [[tweet.encode('ascii', 'ignore')] for tweet in TWEETS]
    output_file = name+'CandidateTweets.csv'
    with open(output_file, 'wb') as file:
        writer = csv.writer(file)
        writer.writerow(["text", "location"])
        #writer.writerows(TWEETS)
        for row in TWEETS:
            tmp = quick_clean(row)
            writer.writerow([tmp])
            #writer.writerow([s.encode('utf8') if type(s) is unicode else s for s in row])
    print "Created file: %s " % (output_file)

def get_data(candidate, num):
    data  = get_user_tweets(num, candidate)
    more_data = []
    for item in data:
       tmp = quick_clean(item)
       more_data.append(tmp)
    to_csv(data)

def from_csv(filename):
    candidate_data = [] #Data stored: text, sentiment
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            candidate_data.append(row)
    print 'Got candidate tweet file: %s' % (filename)       
    return candidate_data

#-------------------------------------------------------------------
def quick_clean(tweet):
    tweet = re.sub(r'RT', "" , tweet) 
    tweet = re.sub(r'@[^\s]+', "" , tweet) 
    tweet = re.sub(r'(https?:\/\/|(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})', "" , tweet)
    return tweet

def preprocess(TWEETS, typeTweet):
    wordlist = []
    tokenizer = RegexpTokenizer(r'#?\w+') 
    #normalize text -- TOKENIZE USING REGEX TOKENIZER
    cnt = 0
    for item in TWEETS:
        text = TWEETS[cnt]
        tweet = ''.join(text)
        tweet = tweet.lower().strip('\n')
        
        tweet = re.sub(r'[0-9]+', "" , tweet)
        tweet = re.sub(r'@[^\s]+', "" , tweet)
        tweet = re.sub(r'#\w+primary', "" , tweet)                    
        wordlist.extend(tokenizer.tokenize(tweet))
        cnt += 1

    #remove stopwords
    stop = stopwords.words('english') + ['rt', 'via', 'u', 'r', 'b', '2', 'http', 
                                        'https', 'co', 'live', 'hall', 'town', 'watch', 
                                        'tune', 'time', 'tonight', 'today', 'campaign', 
                                        'debate', 'wants', 'without', 'dont', 
                                        '#hillaryclinton', '#berniesanders', '#donaldtrump', 
                                        '#tedcruz', "#johnkasich", '#politics']
    filtered = [term for term in wordlist if term not in stop] 
    filtered_final = [term for term in filtered if len(term)>3] 
    print 'Preprocessed %s tweets' % (typeTweet)
    return filtered_final

def top_words(TWEETS, num): 
    words = [word for word in TWEETS if not word.startswith('#')]  
    top_words = Counter(words).most_common(num)
    #for word, n in top_words:
    #    print("%s : %d" %(word, n))
    return top_words


def top_hashtags(TWEETS, num):
    hastags = [word for word in TWEETS if word.startswith('#')]
    top_hashtags = Counter(hastags).most_common(num)
    #for word,n in top_hashtags:
    #     print("%s : %d" %(word, n))
    return top_hashtags
 
def visualize(labels, numData, candidate, color):

    # Example data
    y_pos = np.arange(len(labels))
    error = np.random.rand(len(labels))

    fig, ax = plt.subplots()
    
    rects = plt.barh(y_pos, numData, xerr=error, color=color, align='center', alpha=0.4)
    plt.yticks(y_pos, labels)
    plt.xlabel('Term Frequency')
    plt.ylabel('Terms')
    plt.title(candidate+ " Tweets")
    fig.tight_layout()
    plt.savefig(candidate+'.png', format="png")
    #plt.show()

#---------------------ANALYSIS: DATA VISUALIZATON---------------------------

def analyze(filename, candidate, dataType, num, color):
    can_data = preprocess(from_csv(filename), 'user') 
    
    if (dataType == "words"):
        can_counter_words = top_words(can_data, num)

        words_w = []
        words_count_w = []
        
        for word,num in can_counter_words:
            words_w.append(word)
            words_count_w.append(num)
        
        visualize(words_w, words_count_w, candidate, color)    

    if (dataType == "hashtag"):
        can_counter_ht = top_hashtags(can_data, num)

        words_ht = []
        words_count_ht = []

        for word,num in can_counter_ht:
            words_ht.append(word)
            words_count_ht.append(num)

        visualize(words_ht, words_count_ht, candidate, color)

#------------------------------------------------------------------

hcColor = 'royalblue'
bsColor = 'cornflowerblue'
dtColor = 'darkred'
tcColor = 'crimson'
jkColor = 'firebrick'

#analyze('./Candidate_Data/clintonCandidateTweets.csv', 'User Tweets: Hillary Clinton', 'hashtag', 15,hcColor)
#analyze('./Candidate_Data/sandersCandidateTweets.csv', 'User Tweets: Bernie Sanders', 'hashtag', 15, bsColor)
#analyze('./Candidate_Data/trumpCandidateTweets.csv', 'User Tweets: Donald Trump', 'hashtag', 15, dtColor)
#analyze('./Candidate_Data/cruzCandidateTweets.csv', 'User Tweets: Ted Cruz', 'hashtag', 15, tcColor)
#analyze('./Candidate_Data/kasichCandidateTweets.csv', 'User Tweets: John Kasich', 'hashtag', 15, jkColor)
