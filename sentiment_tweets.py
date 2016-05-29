import pandas
import matplotlib.pyplot as plt
import numpy as np

import nltk
import string
import csv
import re
from sets import Set
from collections import Counter
from nltk.corpus import stopwords
from nltk.corpus import movie_reviews
from nltk.tokenize import RegexpTokenizer
from nltk.classify import NaiveBayesClassifier

from text_analysis_tweets import get_user_tweets
from text_analysis_tweets import quick_clean
from text_analysis_tweets import from_csv


#------------------Preprocess Twitter Data-----------------------------

# global variables
tweets = []
word_tokens = []
word_features = []
tokenizer = RegexpTokenizer(r'#?\w+')
stop_words = stopwords.words('english') + ['rt', 'via', 'u', 'r', 'b', '2', 'http', 'https', 'co']  


def process_data(training_file):
    trainingData = [] #Data stored: text, sentiment

    with open(training_file, 'r') as f:
    	reader = csv.reader(f)
    	for row in reader:
    		trainingData.append(row)

    print 'Got training file: %s' % (training_file)       

    for (words, sentiment) in trainingData:   
        # tokenize using regular expressions
        words_filtered = [item.lower() for item in tokenizer.tokenize(words) if len(item) >= 3]

        # remove stop words using nltk standard library and additial words unique to twitter data
        filtered_final = [term for term in words_filtered if term not in stop_words]

        tweets.append((filtered_final, sentiment))
        word_tokens.extend(filtered_final)
    print 'Preprocessing training file: %s' % (training_file)

def get_sentiment_dict(fileName):
    words = []
    word_senti = []
    
    with open(fileName, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            words.append(row)

    for (word, sentiment) in words:
        word_senti.append((word, sentiment))
        word_tokens.extend(word)
    
    print 'Got training file: %s' % (fileName)
    return word_senti

#---------------Feature Vector and Feature Extraction-----------------

def get_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

def extract_features(input_data):
    input_words = set(input_data)
    features = {}
    for word in word_features:
        features['contains(%s) ' %word] = (word in input_words)
    return features

#--------------------------------------------------------------------------------

process_data('./Text/TrainingData.csv')
#process_data('./Text/MorePoliticalTweets.csv')

word_features = get_features(word_tokens)

#----------------Training: Data - Additional Corpora----------------------------

negMR = movie_reviews.fileids('neg')
posMR = movie_reviews.fileids('pos')
 
negfeats = [(extract_features(movie_reviews.words(fileids=[f])), 'neg') for f in negMR]
posfeats = [(extract_features(movie_reviews.words(fileids=[f])), 'pos') for f in posMR]
 
training_feats = negfeats + posfeats

negWords = get_sentiment_dict('./Text/negative.csv')
posWords = get_sentiment_dict('./Text/positive.csv')


#-------------------------Training: Classifier-------------------------------------

ALL_TRAINING = tweets + negWords + posWords + posWords
print 'Training on %d data...' % (len(ALL_TRAINING))
training_set = nltk.classify.apply_features(extract_features, ALL_TRAINING)

ALL_FEATURES = training_set + training_feats
print 'Training on %d features...' % (len(ALL_FEATURES))
classifier = NaiveBayesClassifier.train(ALL_FEATURES)



#-----------------VISUALIZATION------------------------------

def visualizeSA(labels, numsFrac, title):
    colors = ['red', 'royalblue']
    explode = (0.1, 0, 0, 0)  # explode 1st slice
     
    # Plot
    plt.pie(numsFrac, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
     
    plt.axis('equal')
    plt.title(candidate)
    plt.savefig(title+'.png', format="png")
    #plt.show()

def candidateAnalysis(fileName, candidate):
    print "Analyzing %s Tweets " % (candidate)

    Data = from_csv(fileName) 
    Tweets = []
    sentiment = []
    
    ctn = 0
    for tweet in Data:
        tmp = Data[ctn]
        text = ''.join(tmp)
        Tweets.append(quick_clean(text))
        ctn += 1

    for item in Tweets:
        #print 'Test tweet: %s' % (item)
        sentiment.append(classifier.classify(extract_features(item.split())))

    #count number of pos and num neg -- counter
    #visualize with pie chart
    nums = Counter(sentiment)
   
    wordData = []
    numData = [] 
    fracs = []
    total = 0.0
    

    for item in nums.items():
        wordData.append(item[0])
        numData.append(item[1])

    for i in numData:
        total += i

    for i in numData:
        fracs.append(i/total*100)

    visualizeSA(wordData, numData, candidate)

#-------------------------TESTING-------------------------------------

print classifier.show_most_informative_features(20)

#candidateAnalysis('@HillaryClinton')
#candidateAnalysis('./Candidate_Data/DTTweets.csv','Candidate Tweets: Donald Trump')
#candidateAnalysis('./Candidate_Data/HCTweets.csv','Candidate Tweets: Hillary Clinton')
#candidateAnalysis('./Candidate_Data/BSTweets.csv','Candidate Tweets: Bernie Sanders')
#candidateAnalysis('./Candidate_Data/TCTweets.csv','Candidate Tweets: Ted Cruz')
#candidateAnalysis('./Candidate_Data/JCTweets.csv','Candidate Tweets: John Kasich')

