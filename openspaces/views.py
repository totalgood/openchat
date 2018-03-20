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


def message_update_func(original_msg, user_action, tweet_id):
    """
    Take the original message and update the default in the
    selected button with the one selected. If user clicks approve/deny
    use current default text values for each button as values and update
    tweet model
    """

    # lookup dict to convert text options in slack buttons to the db value
    db_val_lookup = {"Needs approval": 0,
                     "Approve": 1,
                     "Deny": 2}

    # two types of actions in our messages "select" or "button"
    action_type = user_action[0]["type"]
    selected_action = user_action[0]["name"]

    actions_list = original_msg["attachments"][0]["actions"]

    if action_type == "select":
        selected_val = user_action[0]["selected_options"][0]["value"]

        # change the text value for the item selected by the user
        for sub_action in actions_list:
            if selected_action == sub_action["name"]:
                sub_action["text"] = selected_val

    # make a submit button that then saves all the drop down values
    elif action_type == "button":
        action_val = user_action[0]["value"]

        if action_val == "submit":
            # get all of the current text values out of the select action slots, use these values later to populate model instance
            final_vals = {}

            for sub_action in actions_list:
                if sub_action["type"] == "select":
                    final_vals[sub_action["name"]] = db_val_lookup[sub_action["text"]]

            target_tweet = OutgoingTweet.objects.get(tweet_id=tweet_id)
            target_tweet.approved = int(final_vals["approved"])
            target_tweet.save()

    else:
        # TODO add error handling
        raise ValueError("missing action value in message")

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

        update_msg = message_update_func(original_message, user_action, tweet_id)

    # sending back a message that looks like the original but has been updated will replace the message in place in slack
    return Response(update_msg)

