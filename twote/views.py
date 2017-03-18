from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from twote.models import Tweet, User, OutgoingTweet, OutgoingConfig
from twote.serializers import TweetSerializer, OutgoingTweetSerializer, OutgoingConfigSerializer
from twote.tweet_filters import OutgoingTweetFilter



@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'Returns tweets based on their hashtags': reverse('twote:hashtag-list', request=request, format=format),
        'Returns all tweets made by a given user': reverse('twote:user-tweet-list', request=request, format=format),
        'Returns tweets with exactly one hashtag and no URL links': reverse('twote:hashtag-strict', request=request, format=format),
    })


class HashtagList(generics.ListAPIView):
  """Matches any hashtag that is present in the tags field of a tweet.

     To format a request use a querystring as seen below:

     Ex.
     twote/tags/?hashtag=TargetHashtagHere
     twote/tags/?hashtag=Frog --> will return all tweets with Frog as a hashtag

     Passing in a request with no value attached to hashtag will return all tweets that have
     at least one hash tag present in their tags field.

     Ex.
     twote/tags/?hashtag --> will return all tweets with 1+ hashtags

     Currently the matching is case sensitive but can be changed as needed. You're also only able
           to search for one hashtag at the moment, could work on adding multiple hashtags in the future.
  """

  serializer_class = TweetSerializer

  def get_queryset(self):
    queryset = Tweet.objects.all()
    hashtag = self.request.query_params.get('hashtag', None)

    if hashtag is not None:
      queryset = queryset.filter(tags__regex=r"\y{}\y".format(hashtag))
    return queryset


class UserTweetsList(generics.ListAPIView):
    """Will return all tweets from a given user based on their screen-name.

        To format a request use a querystring as seen below:

        Ex.
        /twote/usertweets/?screen-name=pythonbot_ --> will return all tweets from pythonbot_

        Still need to add some things to this endpoint:
        - add screen name to response not just user foriegn key
        - add look up based on userfk only in case we don't care about screen-name
    """

    serializer_class = TweetSerializer

    def get_queryset(self):
        querysetTweet = Tweet.objects.all()
        querysetUser = User.objects.all()

        screen_name = self.request.query_params.get('screen-name', None)

        if screen_name is not None:
            # match the screen_name to the pk of user in User table
            userPK = querysetUser.filter(screen_name__regex=r"\y{}\y".format(screen_name))[0].id

            # use pk to grab all of users tweets out of Tweet table.
            querysetTweet = querysetTweet.filter(user=userPK)

        return querysetTweet


class StrictHashtagList(generics.ListAPIView):
    """Returns a list of tweets that only have one hashtag and no links included.

       Ex.
       twote/strict --> returns subset of tweets with 1 tag, and no links 

       You can optionally search this subset of tweets for a specific hashtag
       by entering a 'hashtag' parameter in a query string.

       Ex.
       twote/strict/?hashtag=Frog
       This query will return all tweets from the strict subset where hashtag = Frog
    """

    serializer_class = TweetSerializer

    def get_queryset(self):
        # only keep tweets with exactly one hashtag
        queryset = Tweet.objects.filter(tags__regex=r'^(\w+)$')

        # filter out tweets with linked urls, got regex from SO
        url_regex = r'((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?'
        queryset = queryset.exclude(text__regex=url_regex)

        hashtag = self.request.query_params.get('hashtag', None)

        if hashtag is not None:
            queryset = queryset.filter(tags__regex=r"\y{}\y".format(hashtag))
        return queryset


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
