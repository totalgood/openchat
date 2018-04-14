import json
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from rest_framework.decorators import parser_classes
from rest_framework.parsers import FormParser

from openspaces.bot_utils import db_utils, tweet_utils, slack_utils
from openspaces.models import OutgoingTweet, OutgoingConfig, OpenspacesEvent
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

@api_view(['POST'])
@parser_classes((FormParser,))
def slack_interactive_endpoint(request):
    if request.method == 'POST':
        # turn payload into dict
        json_text = request.POST.get("payload")
        json_data = json.loads(json_text)
        update_msg = slack_utils.message_update_func(json_data)

        print(json.dumps(json_data, indent=4))

    # send back an updated message to slack when a user takes action
    return Response(update_msg)

