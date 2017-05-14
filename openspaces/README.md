# Information about the bot during OpenSpaces

The bot will be listening for the word or hasthtag `OpenSpaces` or `openspaces` to occur in a tweet. If this word is found in a tweet the bot then tries to extract a time and room number from the text. **If exactly one room and one time mention are found the bot will then schedule a retweet to be sent out approx. 15 minutes before the scheduled event**. 

## Ways to monitor the bot on Slack

There is a slack team setup that will help us monitor the bot during the conference. In this team there are three channels that provide information about the tweets the bot receives and what the bot is planning on doing.

#### Slack Channels
* `outgoing_tweets` - this channel will receive a message from the bot anytime that a bot has scheduled a tweet to be sent out in the future. Each message will contain the tweet, user's name, and user's Twitter id. 

* `need_review` - this channel will receive a message anytime a tweet is found with some relevant information but not the exactly one room and one time mention needed to add the tweet to the bot's outgoing tweets. 

* `event_conflict` - this channel will receive a message anytime a tweet is found where the time and room number exactly match that of an event that the bot has already added to its outgoing tweets. This conflict check is done to have the bot only send tweets about an event one time and not every time a specific OpenSpaces event is mentioned on Twitter. This helps us weed out retweets an original sender might recieve when promoting their OpenSpace.

## Managing bot with Django Admin

We will be using the Django Admin as an easy way to have control over what the bot is planning on sending. Below is a description of each model in the OpenSpaces Admin and the things it controls. 

* `outgoing config` - This model controls configuration information about the bot and how it functions. Changing information in the most current object in this model lets us change how the bot functions without it needing a restart. 
  * The `auto_send` field is a boolean that gives control over whether the bot will automatically stage tweets to be sent without needing additional approval.
  * The `default_send_interval` field is the number of minutes before an event that the bot will tweet its reminder.
  * The `ignore_users` field is an array field that holds a list of twitter ids of ignored users. You can add users to this list by updating the user's record in the `User` model.

* `User` - This model holds information about the users who have had a tweet picked up by the bot. 
  * `should ignore` - If you set this field to True and then save the object in the Admin the user's twitter id will be automatically added to the `ignore users` array field in the `outgoing config` model and the bot will ignore all future tweets from the user.

* `Outgoing Tweets` - This model contains a record of all the tweets that the bot is planning on sending. Below is a brief description of some of the fields that control what tweets the bot will send. **Important note: If a tweet is picked up for an event that is going to occur within the next 30 minutes it will need to be manually approved.**  
  * `approved` - This field is a boolean that determines whether or not a tweet will be picked up and sent out. To cancel or approve a tweet set this field to the appropriate option and save the object. 
  * `scheduled time` - This is the field used to decided when a tweet will be sent. If you decide to change the sending time manually make sure the outgoing message in the `tweet` field reflects the change in time.
  * `tweet` - This field is the actual tweet that the bot will send out.
  * `original tweet` - This field contains the original tweet but it is not the one the bot will send as a reminder. By default 15 minutes before an event the bot will retweet and embedded tweet that contains the user's original tweet and a message about the event coming up in 15 minutes.

* `OpenSpaces  Events` - This model controls which events the bot has already been scheduled to tweet about. When a new event is found that the bot is planning on tweeting about a record is created in this model that has information about the room, time, creator, and tweet. This model is then used to check that the bot only tweets about an event once.

* `Streamed Tweets` - This model contains all of the tweets that the bot has received. This table is used as a record of the tweets the bot has seen but doesn't control what the bot is planning on sending. 
