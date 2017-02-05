from __future__ import division
import tweepy
import os
import requests
import re
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from sutime import SUTime
import json


BAD_WORDS_URL='https://raw.githubusercontent.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/master/en'
MAX_NEGATIVE = -10000000

'''
Basic Tweet Class
'''
class RetweetBot:

	def __init__(self):
		# Twitter API setup
		auth = tweepy.OAuthHandler(os.environ.get('CONSUMER_KEY'), os.environ.get('CONSUMER_SECRET'))
		auth.set_access_token(os.environ.get('ACCESS_TOKEN'), os.environ.get('ACCESS_TOKEN_SECRET'))
		self.api = tweepy.API(auth)
		self.tweet_list = []
		self.relevance_scores = []

		# bad words
		response = requests.get(BAD_WORDS_URL)
		self.bad_words = response.text.split('\n')

		# stop words
		self.stopwords = list(stopwords.words('english'))

		# sutime
		jar_files = os.environ.get('JAR_FILES','../python-sutime/jars')
		self.sutime = SUTime(jars=jar_files, mark_time_ranges=True)

		# nltk data append
		nltk.data.path.append(os.environ.get('NLTK_CORPUS','/webapps/hackor/hackor/nltk_data'))




	'''
	 	Get all tweets
	'''
	def get_tweets(self,topic="#pycon",quantity=10,result_type="recent,popular"):
		tweet_list = self.api.search(q=topic,count=quantity,lang='en',result_type=result_type)
		print("Retrieved {} candidate tweets.".format(len(tweet_list)))
		self.tweet_list += tweet_list


	def clear_tweets(self):
		self.tweet_list = []
		self.relevance_scores = []
	'''
		Defining relevance score as the importance of the user tweeting
		Features: tweeter followers, friends, ratio number of hashtags in the tweet (smaller the better) (PageRank?)
		Remove tweets that have any bad words
	'''
	def score(self,tweet):

		if not self.isSafe(tweet.text):
			return MAX_NEGATIVE

		if tweet.text.startswith('RT'):
			return MAX_NEGATIVE

		# influencer ratio
		influencer_ratio = 0
		if tweet.user.friends_count:
			influencer_ratio = tweet.user.followers_count/tweet.user.friends_count

		#number of hashtags
		hashtags = tweet.text.count('#')

		#hashtag word length
		hashtagcount = 0
		for word in tweet.text.split():
			if word.startswith('#'):
				hashtagcount += len(word)

		final_score = influencer_ratio*(hashtagcount/140)*1.0/(1+hashtags)*tweet.favorite_count
		final_score = 1.0
		return final_score


	'''
		Computing Relevance for all tweets
	'''
	def compute_relevance_scores(self):
		for _id, tweet in enumerate(self.tweet_list):
			if self.score(tweet) > 0.0:
				self.relevance_scores.append((_id,self.score(tweet)))
		self.relevance_scores.sort(key=lambda tup:tup[1],reverse=True)

	def compose_relevant_slack_messages(self,count=1):
		messages = []
		if self.relevance_scores:
			message = ''
			for score in self.relevance_scores[0:count]:
				tweet_score = score[1]
				print tweet_score
				tweet = self.tweet_list[score[0]]
				message = "RT <https://twitter.com/"+tweet.user.screen_name+"|"+tweet.user.screen_name +">" + " " + tweet.text 
				message += "\n <https://twitter.com/"+tweet.user.screen_name+"/status/"+str(tweet.id)+"|Original Tweet>"
				messages.append(message)
		return messages

	def isSafe(self,tweet):
		result = True
		ret = tweet.replace('#','')
		for word in self.bad_words:
			regex = r"\b(?=\w)" + re.escape(word) + r"\b(?!\w)"
			if re.search(regex,ret,re.IGNORECASE):
				result = False
				break
		return result

	'''
		Get time and room number from a tweet
	'''
	def get_time_and_room(self,tweet):

		result = {}
		result['date'] = []
		result['room'] = []

		
		time_slots = self.sutime.parse(tweet)
		tweet_without_time = tweet

		for time_slot in time_slots:
			tweet_without_time = tweet_without_time.replace(time_slot.get('text'),'')
			result['date'].append(time_slot.get('value'))
		
		filter_known_words = [word.lower() for word in word_tokenize(tweet_without_time) if word.lower() not in (self.stopwords + nltk.corpus.words.words())]

		# regular expression for room
		room_re = re.compile('([a-zA-Z](\d{3})[-+]?(\d{3})?)')

		for word in filter_known_words:
			if room_re.match(word):
				result['room'].append(room_re.match(word).group())

		return result



if __name__ == '__main__':
	bot = RetweetBot()
	print bot.get_time_and_room('#importantigravity (acro yoga: poses for pair programmers) @ 5pm in open space B114! #pycon #pyconopenspaces :-)')

        

