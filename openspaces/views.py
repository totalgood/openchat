from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser

import json

from openspaces.models import OutgoingTweet, OutgoingConfig
from openspaces.serializers import OutgoingTweetSerializer, OutgoingConfigSerializer
from openspaces.tweet_filters import OutgoingTweetFilter


class ListOutgoingTweets(generics.ListCreateAPIView):
    """
    Endpoint to display tweet info used by front end.

    Two filter options are available through the use of querystring params.

    Option one: "approved" - lets user filter on current level of tweet approval
    Tweet approval choices:
        0 - needs_approval
        1 - approved
        2 - denied

    Option two: "pending" - T/F flag filters if tweet is still waiting to be sent

    Ex.
    /twitter/tweets/?approved=1 --> returns all tweets that are approved

    /twitter/tweets/?pending=True --> returns all tweets still waiting to be sent

    /twitter/tweets/?approved=0&pending=True --> you can combine these query params in any order
    """
    serializer_class = OutgoingTweetSerializer
    filter_class = OutgoingTweetFilter

    def get_queryset(self):
        queryset = OutgoingTweet.objects.all()
        pending = self.request.query_params.get('pending', None)

        if pending is not None:
            pend = True if pending == 'True' else False
            queryset = queryset.filter(sent_time__isnull=pend)
        return queryset


class ListCreateOutgoingConfig(generics.ListCreateAPIView):
    """
    Endpoint to update current config settings by adding a config object to table
    """
    queryset = OutgoingConfig.objects.all()
    serializer_class = OutgoingConfigSerializer


class RetriveUpdateOutgoingTweets(generics.RetrieveUpdateAPIView):
    """
    Endpoint that lets a user send PUT or PATCH request to updat a tweet object
    """
    queryset = OutgoingTweet.objects.all()
    serializer_class = OutgoingTweetSerializer


def message_update_func(original_msg, action, tweet_id):
    """
    Take the original message and update the default in the
    selected button with the one selected. If user clicks approve/deny
    use current default text values for each button as values and update
    tweet model
    """

    # lookup dict to convert text options in slack buttons to the db value
    db_val_lookup = {"Needs action": 0,
                     "Approved": 1,
                     "Denied": 2}

    # two types of actions in our messages "select" or "button"
    action_type = action[0]["type"]
    selected_action = action[0]["name"]

    actions_list = original_msg["attachments"][0]["actions"]

    if action_type == "select":
        # TODO look at if you need to have these values split if you're only using the text and the db lookup above you may not need this
        selected_val = action[0]["selected_options"][0]["value"]

        # change the text value for the item selected by the user
        for sub_action in actions_list:
            if selected_action == sub_action["name"]:
                sub_action["text"] = selected_val

    # make a submit button that then saves all the drop down values
    elif action_type == "button":
        # TODO add a function here that saves the values out of the text slots in the message and updates the coressponding model
        action_val = action[0]["value"]

        # TODO change button name to submit
        if action_val == "yes":
            # get all of the current text values out of the select action slots, use these values later to populate model instance
            final_vals = {}

            for sub_action in actions_list:
                if action["type"] == "select":
                    print(action)
                    final_vals[sub_action["name"]] = db_val_lookup[sub_action["text"]]

            print(selected_vals)
            # print(selected_vals["approved"])

            target_tweet = OutgoingTweet.objects.get(tweet_id=tweet_id)
            target_tweet.approved = int(final_vals["approved"])
            target_tweet.save()

    else:
        # TODO add error handling
        raise ValueError("missing action value in message")


    # things that still need to be added:
    # 1. need to link tweet id and meta info to link the slack message to the tweet it wants to change
    # 2. change buttons to actual values you'll be using and correct number of buttons
    # 3. ^^ start with adding buttons with actual values, and the ability to change the tweet with the correct id
    # worry about pre populating with correct vaules as final step

    return original_msg


@api_view(['GET', 'POST'])
@parser_classes((FormParser,))
def slack_interactive_endpoint(request):
    if request.method == 'POST':

        # gets json in payload
        json_text = request.POST.get("payload")

        # turns json into python dict
        json_data = json.loads(json_text)
        print(json.dumps(json_data, indent=4))

        original_message = json_data["original_message"]
        action = json_data["actions"]

        tweet_type, tweet_id = json_data["callback_id"].split("|")
        print(tweet_id)

        update_msg = message_update_func(original_message, action, tweet_id)




        ############################################
        tweet_type = json_data["callback_id"]
        # print(tweet_type)

        if tweet_type == "tweet_approval":
            # use-id|tweet-id in name field of actions
            # TODO use callback_id for meta info as opposed to the name below
            twitter_handle, tweet_id  = json_data["actions"][0]["name"].split("|")

            action_choice = json_data["actions"][0]["value"]

            in_tweet = OutgoingTweet.objects.get(tweet="test tweet")
            in_tweet.approved = 1
            in_tweet.save()

            return Response({"message": "Got some data!", "data": request.data})

        ############################################

    # sending back a message that looks like the original but has been updated will replace the message in place in slack
    return Response(update_msg)

