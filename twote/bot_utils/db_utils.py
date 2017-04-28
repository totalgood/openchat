from twote import models

def get_ignored_users():
    """
    Check app config table to get list of ignored twitter ids
    """
    config_obj = models.OutgoingConfig.objects.latest("id")
    ignore_list = [tw_id for tw_id in config_obj.ignore_users]
    return ignore_list

def get_or_create_user_and_tweet(status):
    """
    Take a status from twitter and either create or update info for tweet & user
    """
    user, created = models.User.objects.get_or_create(id_str=str(status.user.id))
    user.verified = status.user.verified  # v4
    user.time_zone = status.user.time_zone  # v4
    user.utc_offset = status.user.utc_offset  # -28800 (v4)
    user.protected = status.user.protected  # v4
    user.location = status.user.location  # Houston, TX  (v4)
    user.lang = status.user.lang  # en  (v4)
    user.screen_name = status.user.screen_name
    user.followers_count = status.user.followers_count
    user.statuses_count = status.user.statuses_count
    user.friends_count = status.user.friends_count
    user.favourites_count = status.user.favourites_count
    user.save()

    # save tweet record to StreamedTestTweet model
    tweet_record, created = models.StreamedTestTweet.objects.get_or_create(id_str=status.id_str)
    tweet_record.id_str = status.id_str
    tweet_record.user = user
    tweet_record.favorite_count = status.favorite_count
    tweet_record.text = status.text
    tweet_record.source = status.source
    tweet_record.save() 

def check_for_auto_send():
    """
    Check config table and return auto send value
    """
    config_obj = models.OutgoingConfig.objects.latest("id")
    approved = 1 if config_obj.auto_send else 0
    return approved

def save_outgoing_tweet(tweet_obj):
    """
    Save a tweet object to the outgoing tweet table triggering celery stuff
    """
    tweet_obj = models.OutgoingTweet(tweet=tweet_obj["message"], 
                                     approved=tweet_obj["approved"], 
                                     scheduled_time=tweet_obj["remind_time"])
    tweet_obj.save()

def check_time_room_conflict(a_time, a_room):
    """
    Check to see if there is already a tweet scheduled to go out about 
    an event in the same time and room. Helps avoid duplicate retweets
    about the same event sent by multiple users. Currently the retweets
    from bot are first come first serve for a unqiue room and time stamp. 
    """
    event_conflict = models.RetweetEvent.objects.filter(location=a_room, start=a_time)
    return True if event_conflict else False

def create_event(**kwargs):
    """
    Create event record with a description, creator, time, and room
    """
    models.RetweetEvent.objects.create(**kwargs)
