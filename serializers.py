from rest_framework import serializers
from twote.models import Tweet, OutgoingTweet, OutgoingConfig 


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = '__all__'


class OutgoingTweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutgoingTweet
        fields = '__all__'
        

class OutgoingConfigSerializer(serializers.ModelSerializer):
    class Meta: 
        model = OutgoingConfig
        fields = '__all__'