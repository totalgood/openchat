import copy
import django
import os
from slackclient import SlackClient

# TODO double check that you need this setup step when sending tweets from inside streambot.py
os.environ["DJANGO_SETTINGS_MODULE"] = "openchat.settings"
django.setup()

import openspaces.secrets as s
from openspaces.bot_utils import slack_utils
from openspaces.models import OutgoingTweet

slack_client = SlackClient(s.BOT_TOKEN)

attachments_json_drop_down = {
    "text": "Tweet body here",
    "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
    "color": "#3AA3E3",
    "attachment_type": "default",
    "title": "User name here: fake-user",
    "callback_id": "message_type|12345",
    "actions": [
        {
            "name": "slack_date",
            "text": "Choose date",
            "type": "select",
            "option_groups": [
                {
                    "text": "Event date",
                    "options": [
                        {
                            "text": "5/11",
                            "value": "5/11"
                        },
                        {
                            "text": "5/12",
                            "value": "5/12"
                        },
                        {
                            "text": "5/13",
                            "value": "5/13"
                        }
                    ]
                }
            ]
        },
        {
            "name": "slack_time",
            "text": "Choose event time",
            "type": "select",
            "option_groups": [
                {
                    "text": "Time of event",
                    "options": [
                        {
                            "text": "08:00",
                            "value": "08:00"
                        },
                        {
                            "text": "09:00",
                            "value": "09:00"
                        },
                        {
                            "text": "10:00",
                            "value": "10:00"
                        },
                        {
                            "text": "11:00",
                            "value": "11:00"
                        },
                        {
                            "text": "12:00",
                            "value": "12:00"
                        },
                        {
                            "text": "13:00",
                            "value": "13:00"
                        },
                        {
                            "text": "14:00",
                            "value": "14:00"
                        },
                        {
                            "text": "15:00",
                            "value": "15:00"
                        },
                        {
                            "text": "16:00",
                            "value": "16:00"
                        },
                        {
                            "text": "17:00",
                            "value": "17:00"
                        },
                        {
                            "text": "18:00",
                            "value": "18:00"
                        }
                    ]
                }
            ]
        },
        {
            "name": "slack_room",
            "text": "Choose room",
            "type": "select",
            "option_groups": [
                {
                    "text": "Event room",
                    "options": [
                        {
                            "text": "Room 09",
                            "value": "09"
                        },
                        {
                            "text": "Room 10",
                            "value": "10"
                        },
                        {
                            "text": "Room 14",
                            "value": "14"
                        },
                        {
                            "text": "Room 15",
                            "value": "15"
                        },
                        {
                            "text": "Room 16",
                            "value": "16"
                        },
                        {
                            "text": "Room 19",
                            "value": "19"
                        },
                        {
                            "text": "Room 20",
                            "value": "20"
                        },
                        {
                            "text": "Room 21",
                            "value": "21"
                        },
                        {
                            "text": "Room 22",
                            "value": "22"
                        }
                    ]
                }
            ]
        },
        {
            "name": "slack_approved",
            "text": "Needs approval",
            "type": "select",
            "option_groups": [
                {
                    "text": "Approve/deny tweet",
                    "options": [
                        {
                            "text": "Approve",
                            "value": "Approve"
                        },
                        {
                            "text": "Deny",
                            "value": "Deny"
                        }
                    ]
                }
            ]
        },
        {
            "name": "slack_submit",
            "text": "Submit",
            "type": "button",
            "style": "primary",
            "value": "submit"
        }
    ]
}

def send_slack_message(**kwargs):
    """
    Take a tweet record and set the default values in message to
    those in the tweet and send message to slack
    """

    # make a copy of the default body
    message_body = copy.deepcopy(attachments_json_drop_down)

    if kwargs["tweet_created"]:
        # lookup dict to change values from model to text representation
        approved_lookup = {0: "Needs approval",
                           1: "Approved",
                           2: "Denied"}

        tweet_instance = OutgoingTweet.objects.get(tweet_id=kwargs["tweet_id"])

        event_time = tweet_instance.event_obj.start
        date_val, time_val = slack_utils.utc_datetime_to_button_format(event_time)
        room_val = tweet_instance.event_obj.location
        approved_val = approved_lookup[tweet_instance.approved]


    else:
        date_val = None
        time_val = None
        room_val = None
        approved_val = None

    # set action message and icon in slack message
    if approved_val is not None:
        if approved_val == approved_lookup[1]:
            message_body["footer"] = "auto approved by OpenSpacesBot"
            message_body["footer_icon"] = "https://emojipedia-us.s3.amazonaws.com/thumbs/120/microsoft/106/heavy-check-mark_2714.png"
        elif approved_val == approved_lookup[0]:
            message_body["footer"] = "Tweet needs approval"
            message_body["footer_icon"] = "https://d1nhio0ox7pgb.cloudfront.net/_img/g_collection_png/standard/256x256/eyeglasses.png"
        else:
            print("missing valid value for approval")
    else:
        message_body["footer"] = "Tweet needs information in order to be approved"
        message_body["footer_icon"] = "https://d1nhio0ox7pgb.cloudfront.net/_img/g_collection_png/standard/256x256/eyeglasses.png"

    screen_name = kwargs["screen_name"]
    user_id = kwargs["user_id"]
    message_body["title"] = f"tweet from: {screen_name}, twitter id: {user_id}"

    message_body["text"] = kwargs["tweet"]
    message_body["callback_id"] = "incoming_tweet|{}|{}".format(kwargs["tweet_id"], kwargs["screen_name"])
    message_body["actions"][0]["text"] = date_val if date_val is not None else "Choose date"
    message_body["actions"][1]["text"] = time_val if time_val is not None else "Choose time"
    message_body["actions"][2]["text"] = room_val if room_val is not None else "Choose room"
    message_body["actions"][3]["text"] = approved_val if approved_val is not None else "Needs approval"

    try:
        channel = kwargs["channel"]
    except KeyError:
        # defaults to outgoing-tweets channel if not conflict
        channel = "outgoing-tweets"

    if channel == "conflict":
        channel_id = "CAKSUH0RG"
    else:
        # id for outgoing-tweets channel
        channel_id = "CAKSJ1PLG"

    slack_client.api_call("chat.postMessage",
                          channel=channel_id,
                          text=kwargs["slack_msg"],
                          attachments=[message_body])
    return


if __name__ == '__main__':
    import pytz
    import datetime
    from openspaces.bot_utils import db_utils
    from random import randint

    user_name = "user 1"
    user_id="123456789"
    tweet_id = str(randint(0, 1000000))
    screen_name = "screen_name1"
    tweet = "April 1st tweet room C123"


    def create_sample_tweet(tweet, tweet_id, screen_name):
        """helper func to create a tweet instance in db for manual testing"""
        event_obj = db_utils.create_event(description="fake event description",
                                          start=datetime.datetime(2018, 5, 10, 1, tzinfo=pytz.utc),
                                          location="A123",
                                          creator="5/29 tweeter")
        tweet_instance = db_utils.save_outgoing_tweet(tweet_id=tweet_id,
                                                      tweet=tweet, # for testing this is ok, in reality it will be the embeded tweet
                                                      original_tweet=tweet,
                                                      screen_name=screen_name,
                                                      approved=1,
                                                      event_obj=event_obj)

    tweet_created = False

    if tweet_created:
        create_sample_tweet(tweet, tweet_id, screen_name)

    send_slack_message(user_id=user_id,
                       tweet_id=tweet_id,
                       screen_name=screen_name,
                       tweet_created=tweet_created,
                       tweet=tweet,
                       slack_msg=tweet)
