from __future__ import division
import tweepy
import os
import requests
import re

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




        

