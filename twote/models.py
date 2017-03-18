from __future__ import division, print_function, unicode_literals

import datetime
from collections import Mapping
from .model_utils import representation

from django.contrib.gis.db import models
from django.forms.models import model_to_dict  # this will miss out on ManyToMany fields since they aren't actually database fields


def dict_to_model(d, cls):
    return cls(**d)


class Place(models.Model):
    id = models.AutoField(primary_key=True)
    id_str = models.CharField(max_length=256, db_index=True, default='')
    place_type = models.CharField(max_length=256, blank=True, null=True)
    country_code = models.CharField(max_length=256, blank=True, null=True)
    country = models.CharField(max_length=256, blank=True, null=True)
    name = models.CharField(max_length=256, blank=True, null=True)
    full_name = models.CharField(max_length=256, blank=True, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    bounding_box_coordinates = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'twote_place'


class Tweet(models.Model):
    id = models.AutoField(primary_key=True)
    id_str = models.CharField(max_length=256, db_index=True, default='')

    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(null=True)

    in_reply_to_id_str = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    in_reply_to = models.ForeignKey('self', blank=True, null=True)
    user = models.ForeignKey('User', blank=True, null=True)
    source = models.CharField(max_length=256, blank=True, null=True)
    text = models.CharField(max_length=256, blank=True, null=True)
    tags = models.CharField(max_length=256, blank=True, null=True)
    location = models.CharField(max_length=256, blank=True, null=True)
    place = models.ForeignKey(Place, blank=True, null=True)
    favorite_count = models.IntegerField(default=-1, null=True)

    def __str__(self):
        return representation(self)

    class Meta:
        db_table = 'twote_tweet'


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

    def __str__(self):
        return str(self.screen_name)

    class Meta:
        db_table = 'twote_user'


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
            eta = datetime.datetime.utcnow() + datetime.timedelta(minutes=wait_time)
            self.scheduled_time = eta
        super(OutgoingTweet, self).save(*args, **kwargs)

    class Meta:
        db_table = 'twote_outgoingtweet'


class OutgoingConfig(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    auto_send = models.BooleanField()
    default_send_interval = models.IntegerField(default=15)

    class Meta:
        db_table = 'twote_outgoingconfig'


class Serializer(object):
    """Callable serializer. An instance of this class can be passed to the `default` arg in json.dump

    >>> json.dumps(model.Tweet(), default=Serializer(), indent=2)
    {...}
    """
    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_format = ' '.join([date_format, time_format])

    def convert_value(self, value):
        if isinstance(value, datetime.datetime):
            return value.strftime(self.datetime_format)
        elif isinstance(value, datetime.date):
            return value.strftime(self.date_format)
        elif isinstance(value, datetime.time):
            return value.strftime(self.time_format)
        elif isinstance(value, models.Model):
            return value.get_id()
        else:
            return value

    def clean_data(self, data):
        # flask doesn't bother with this condition check, why?
        if isinstance(data, Mapping):
            for key, value in data.items():
                if isinstance(value, dict):
                    self.clean_data(value)
                elif isinstance(value, (list, tuple)):
                    data[key] = map(self.clean_data, value)
                else:
                    data[key] = self.convert_value(value)
        return data

    def serialize_object(self, obj, **kwargs):
        data = model_to_dict(obj, **kwargs)
        return self.clean_data(data)

    def __call__(self, obj, **kwargs):
        return self.serialize_object(obj, **kwargs)


class Deserializer(object):
    def deserialize_object(self, model, data, **kwargs):
        return dict_to_model(data, cls=model)
