from rest_framework import serializers
from openspaces.models import OutgoingTweet, OutgoingConfig 


class OutgoingTweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutgoingTweet
        fields = '__all__'
        

class OutgoingConfigSerializer(serializers.ModelSerializer):
    class Meta: 
        model = OutgoingConfig
        fields = '__all__'