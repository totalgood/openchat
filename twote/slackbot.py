from slackclient import SlackClient
import os
from retweetbot import RetweetBot
import time


topic_list = ('#python,#pycon,#portland,#pyconopenspaces,#pycon2017,#pycon2016,#pythonic' +
                   '#jobs,#career,#techwomen,' +
                   '#angularjs,#reactjs,#framework,#pinax,#security,#pentest,#bug,#programming,#bot,#robot,' +
                   '#calagator,#pdxevents,#events,#portlandevents,#techevents,' +
                   '#r,#matlab,#octave,#javascript,#ruby,#rubyonrails,#django,#java,#clojure,#nodejs,#lisp,#golang,' +
                   '#science,#astronomy,#math,#physics,#chemistry,#biology,#medicine,#statistics,#computerscience,#complexity,' +
                   '#informationtheory,#knowledge,#philosophy,#space,#nasa,' +
                   '#social,#economics,#prosocial,#peaceandcookies,#humility,#shoutout,' +
                   '#opendata,#openscience,#openai,#opensource,' +
                   '#data,#dataviz,#d3js,#datascience,#machinelearning,#ai,#neuralnet,#deeplearning,#iot,' +
                   '#hack,#hacking,#hackathon,#compsci,#coding,#coder,' +
                   '#mondaymotivation,#motivation,#life,#mind,' +
                   '#play,#game,#logic,#gametheory,#winning,' +
                   '#kind,#bekind,#hope,#nice,#polite,#peace,#inspired,#motivated,#inspiration,#inspiring,#quote,' +
                   '#awesome,#beawesome,#payitforward,#give,#giving,#giveandtake,#love,#pause,#quiet,' +
                   '#windows,#linux,#ubuntu,#osx,#android,#ios,' +
                   '#thankful,#gratitude,#healthy,#yoga,#positivity,#community,#ecosystem,#planet,#meditation,#bliss,'
                   ).split(',')


_message = {
    "text": "This is the tweet!",
    "attachments": [
        {
            "text": "Retweet?",
            "fallback": "You are unable to choose a game",
            "callback_id": "wopr_game",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "approve",
                    "text": "Approve",
					"style" : "primary",
                    "type": "button",
                    "value": "approve",
                    "confirm": {
                        "title": "Are you sure?",
                        "text": "This will be seen by everyone who is following you.",
                        "ok_text": "Yes",
                        "dismiss_text": "No"
                    }
                },
                {
                    "name": "reject",
                    "text": "Reject",
					"style" : "danger",
                    "type": "button",
                    "value": "reject"
                },
                {
                    "name": "another",
                    "text": "Send another one",

                    "type": "button",
                    "value": "war",
                    
                }
            ]
        }
    ]
}

def send_slack_messages(messages):
	slack_token = os.environ["SLACK_API_TOKEN"]
	sc = SlackClient(slack_token)
	for message in messages:
		sc.api_call(
		  "chat.postMessage",
		  channel=os.environ.get("SLACK_CHANNEL"),
		  text=message,
		  attachments=_message['attachments'],
		)


if __name__ == '__main__':
  bot = RetweetBot()

  for topic in topic_list[0:2]:
  	if topic.startswith('#'):
  		print topic
  		bot.get_tweets(topic + " filter:safe filter:media")
  		bot.compute_relevance_scores()
  		messages = bot.compose_relevant_slack_messages(1)
  		# print messages
  		send_slack_messages(messages)
  		bot.clear_tweets()
  		time.sleep(60)


