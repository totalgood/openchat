import pytz
import datetime
import re

from openspaces.models import OutgoingTweet, OpenspacesEvent
from openspaces.bot_utils import tweet_utils, db_utils

def utc_datetime_to_button_format(utc_dt):
    """
    Convert a UTC datetime obj to the the date and time
    format we need for slack buttons in Eastern time.
    """
    eastern = pytz.timezone('US/Eastern')
    east_conv = utc_dt.astimezone(eastern)

    time_text = east_conv.strftime("%H:%M")
    date_text = east_conv.strftime("%m/%d")

    return date_text, time_text

def button_format_to_utc_datetime(date_text, time_text):
    """
    Convert button time back into a utc datetime object
    """
    month, day = date_text.split("/")
    month = int(month.lstrip("0"))
    day = int(day.lstrip("0"))

    hour, minute = time_text.split(":")

    if hour == "00":
        hour = 0
    else:
        hour = int(hour.lstrip("0"))

    if minute == "00":
        minute = 0
    else:
        minute = int(minute.lstrip("0"))

    local_tz = pytz.timezone("US/Eastern")
    button_time = datetime.datetime(2018, month, day, hour, minute)
    tz_aware_button_time = local_tz.normalize(local_tz.localize(button_time))
    return tz_aware_button_time.astimezone(pytz.utc)

def footer_creator(original_msg, slack_user, time_stamp, footer_type):
    """
    Take orignal message and add a footer with correct
    message and icon based on type
    """
    footer_img_urls = {
        "0": "",
        "1": "https://emojipedia-us.s3.amazonaws.com/thumbs/120/microsoft/106/heavy-check-mark_2714.png",
        "2": "http://www.sig-p3x1.sedesol.gob.mx/sedesol_3x1/imagenes/icon/error_256.png",
        "missing_info": "http://icdn.pro/images/fr/a/l/alerte-icone-6076-128.png"
    }

    footer_msgs = {
        "0": "Needs approval!!!",
        "1": "Approved by @{}".format(slack_user),
        "2": "Denied by @{}".format(slack_user),
        "missing_info": "All fields must be filled out!!!"
    }

    original_msg["attachments"][-1]["footer"] = footer_msgs[footer_type]
    original_msg["attachments"][-1]["footer_icon"] = footer_img_urls[footer_type]
    original_msg["attachments"][-1]["ts"] = time_stamp
    return original_msg

def message_update_func(json_data):
    """
    Take the original message and update the default in the
    selected button with the one selected. If user clicks approve/deny
    use current default text values for each button as values and update
    tweet model
    """
    # extract information from Slack payload into vars
    tweet_type, tweet_id, screen_name = json_data["callback_id"].split("|")
    original_msg = json_data["original_message"]
    user_action = json_data["actions"]
    slack_user = json_data["user"]["name"]
    action_ts = json_data["action_ts"]

    # two types of actions in our messages "select" or "button"
    action_type = user_action[0]["type"]
    actions_list = original_msg["attachments"][0]["actions"]

    if action_type == "select":
        # modify the original message and update with a user's drop down selection
        selected_val = user_action[0]["selected_options"][0]["value"]
        selected_action = user_action[0]["name"]

        for sub_action in actions_list:
            if selected_action == sub_action["name"]:
                sub_action["text"] = selected_val

    elif action_type == "button":
        action_val = user_action[0]["value"]

        if action_val == "submit":
            # lookup dict to convert text options in slack buttons to db value
            db_val_lookup = {"Needs approval": "0",
                             "Approve": "1",
                             "Deny": "2"}

            # build up a dict of all choices made by slack user
            final_vals = {}
            for sub_action in actions_list:
                if sub_action["type"] == "select":
                    try:
                        choosen_val = db_val_lookup[sub_action["text"]]
                    except KeyError:
                        choosen_val = sub_action["text"]
                    final_vals[sub_action["name"]] = choosen_val

            # check to make sure there are values filled out for each field
            for choice in final_vals.values():
                if bool(re.search("Choose", choice)):
                    return footer_creator(original_msg, slack_user, action_ts, "missing_info")


            # vars pulled out of slack message that are needed to save the model obj
            event_datetime = button_format_to_utc_datetime(final_vals["slack_date"], final_vals["slack_time"])
            event_location = final_vals["slack_room"]
            tweet = original_msg["attachments"][0]["text"]
            approval_val = final_vals["slack_approved"]

            original_msg = footer_creator(original_msg, slack_user, action_ts, approval_val)

            # check if the tweet already exists, then update/or create
            try:
                # update the exsisting tweet instance
                target_tweet = OutgoingTweet.objects.get(tweet_id=tweet_id)
                target_tweet.approved = approval_val
                target_tweet.scheduled_time = event_datetime - datetime.timedelta(minutes=15) # calc the new remind time if update in slack
                target_tweet.save()

                # update the coresponding event
                event_id = target_tweet.event_obj.id
                event_instance = OpenspacesEvent.objects.get(id=event_id)
                event_instance.start = event_datetime
                event_instance.location = event_location
                event_instance.save()

            except OutgoingTweet.DoesNotExist:
                # need to create a new outgoing tweet instance and the event that goes with it
                event_obj = db_utils.create_event(description=tweet,
                                                  start=event_datetime,
                                                  location=event_location,
                                                  creator=screen_name)

                tweet_utils.schedule_slack_tweets(tweet_id=tweet_id,
                                                  screen_name=screen_name,
                                                  tweet=tweet,
                                                  approved=int(approval_val),
                                                  event_time=event_datetime,
                                                  event_obj=event_obj)

    else:
        # this shouldn't ever happen
        raise ValueError("missing action value in message")

    return original_msg
