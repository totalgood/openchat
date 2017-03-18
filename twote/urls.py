from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.api_root, name='root'),
    url(r'^tags/$', views.HashtagList.as_view(), name='hashtag-list'),
    url(r'^usertweets/$', views.UserTweetsList.as_view(), name='user-tweet-list'),
    url(r'^strict/$', views.StrictHashtagList.as_view(), name='hashtag-strict'),
    url(r'^tweets/$', views.ListOutgoingTweets.as_view()),
    url(r'^update/(?P<pk>[0-9]+)$', views.RetriveUpdateOutgoingTweets.as_view()),
    url(r'^config/$', views.ListCreateOutgoingConfig.as_view()),
]
