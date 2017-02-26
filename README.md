# twote

twote = Twitter Vote (portmanteau)

Django app and Twitter+Slack Bot to manage and promote a self-service event schedule, using Twitter and Slack. "Votes" are the tweet likes and moderator ratings of tweets for inclusion or exclusion from the community announcement (Tweet and Slack messaging) schedule.

Twote listens for tweets associated with your particular event by monitoring hashtags like `#pyconopenspaces` or `#pycon2017` and twitter accounts like `@pycon` and `@pyconopenspaces` for schedule announcement requests. And it tries to learn to recognize these tweets about your event by monitoring other related hashtags and topics, like `#python` or `#django` and finding tweets that are semantically similar to tweets that contained the targeted hashtags. It also learns to recognize spam and trolling tweets by monitoring unrelated hashtags to build sentiment analyzers for things like "spaminess", "anger", "sarcasm", and "positivity."  So if you need a bot to just pull down training sets of tweets for your problem, you can configure twote to build a training set and train a model to predict the sentiment you are interested in. 

## Installation

pip install twote

## Contributors

We're extremely grateful to the supportive [python community in Portland](https://pdxpython.org/) for the many fun hours of brainstorming to build this bot. And special thanks to the [core developers](AUTHORS.md) that turned an idea into reality without compensation or prodding or even any organization or project management. If you'd like to follow our plans or contribute yourself, checkout or plans and progress list on the [CHANGES page](CHANGES.md)