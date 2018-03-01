from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^tweets/$', views.ListOutgoingTweets.as_view()),
    url(r'^update/(?P<pk>[0-9]+)$', views.RetriveUpdateOutgoingTweets.as_view()),
    url(r'^config/$', views.ListCreateOutgoingConfig.as_view()),
    url(r'^slack/', views.slack_interactive_endpoint),
]
