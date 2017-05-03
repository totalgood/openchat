from __future__ import division, print_function, unicode_literals

from django.dispatch import Signal, receiver
from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import datetime, timedelta


ignore_user_signal = Signal(providing_args=["id_str", "screen_name"])


class StreamedTweet(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    id_str = models.CharField(max_length=256, db_index=True, default='')
    user = models.ForeignKey('User', blank=True, null=True)
    source = models.CharField(max_length=256, blank=True, null=True)
    text = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'openchat_streamedtweet'


class User(models.Model):
    id = models.AutoField(primary_key=True)
    id_str = models.CharField(max_length=256, db_index=True, default='')
    screen_name = models.CharField(max_length=256, blank=True, null=True)
    verified = models.IntegerField(blank=True, null=True)
    time_zone = models.CharField(max_length=256, blank=True, null=True)
    utc_offset = models.IntegerField(blank=True, null=True)
    protected = models.IntegerField(blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    lang = models.CharField(max_length=256, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    created_date = models.DateTimeField(null=True)
    statuses_count = models.IntegerField(blank=True, null=True)
    friends_count = models.IntegerField(blank=True, null=True)
    favourites_count = models.IntegerField(default=-1, null=True)
    should_ignore = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        Send out a signal if a user is saved that should be ignored this
        signal is used to update the ignore list in the conifg model 
        """
        if self.should_ignore == True:
            ignore_user_signal.send(sender=self.__class__, 
                                    id_str=self.id_str, 
                                    screen_name=self.screen_name)
        else:
            pass
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.screen_name)

    class Meta:
        db_table = 'openchat_user'


@receiver(ignore_user_signal, sender=User)
def ignore_handler(sender, **kwargs):
    """Add the user's id to the ignore list bot checks when receiving tweets"""
    config_obj = OutgoingConfig.objects.latest("id")
    config_obj.ignore_users.append(int(kwargs['id_str']))
    config_obj.save(update_fields=['ignore_users'])
    

# used in OutgoingTweet model
APPROVAL_CHOICES = (
    (0, 'Needs_action'),
    (1, 'Approved'),
    (2, 'Denied'),
)


class OutgoingTweet(models.Model):
    # still need to add original tweet id from Tweet table foriegn key relation
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    tweet = models.CharField(max_length=255)
    approved = models.IntegerField(choices=APPROVAL_CHOICES, default=0)
    time_interval = models.IntegerField(null=True, blank=True)
    scheduled_time = models.DateTimeField(default=None, null=True, blank=True)
    task_scheduled = models.BooleanField(default=False)
    sent_time = models.DateTimeField(default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Will calc and write tweet scheduled time when a tweet is approved
        """
        if self.approved == 1 and self.scheduled_time is None:
            if self.time_interval is None:
                try:
                    # if the OutgoingConfig table is empty this will throw DoesNotExist
                    wait_time = OutgoingConfig.objects.latest("id").default_send_interval
                except:
                    # if no wait_time in AppConfig default to 15 mins
                    wait_time = 15
            else:
                wait_time = self.time_interval
            eta = datetime.utcnow() + timedelta(minutes=wait_time)
            self.scheduled_time = eta
        super(OutgoingTweet, self).save(*args, **kwargs)

    class Meta:
        db_table = 'openchat_outgoingtweet'


class RetweetEvent(models.Model):
    """Used to keep a record of rooms and times that have already been retweeted"""
    description = models.TextField()
    start = models.DateTimeField()
    location = models.CharField(max_length=100)
    creator = models.CharField(max_length=100, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'openchat_retweetevent'


class OutgoingConfig(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    auto_send = models.BooleanField()
    default_send_interval = models.IntegerField(default=15)
    ignore_users = ArrayField(models.BigIntegerField())

    class Meta:
        db_table = 'openchat_outgoingconfig'
