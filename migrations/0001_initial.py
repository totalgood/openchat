# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('id_str', models.CharField(max_length=255)),
                ('place_type', models.CharField(max_length=255, null=True, blank=True)),
                ('country_code', models.CharField(max_length=255, null=True, blank=True)),
                ('country', models.CharField(max_length=255, null=True, blank=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('full_name', models.CharField(max_length=255, null=True, blank=True)),
                ('url', models.CharField(max_length=255, null=True, blank=True)),
                ('bounding_box_coordinates', models.CharField(max_length=255, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('id_str', models.CharField(max_length=255, null=True, blank=True)),
                ('in_reply_to_id_str', models.CharField(max_length=255, null=True, blank=True)),
                ('source', models.CharField(max_length=255, null=True, blank=True)),
                ('text', models.CharField(max_length=255, null=True, blank=True)),
                ('tags', models.CharField(max_length=255, null=True, blank=True)),
                ('created_date', models.DateTimeField()),
                ('location', models.CharField(max_length=255, null=True, blank=True)),
                ('favorite_count', models.IntegerField()),
                ('in_reply_to', models.ForeignKey(blank=True, to='twote.Tweet', null=True)),
                ('place', models.ForeignKey(blank=True, to='twote.Place', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('id_str', models.CharField(max_length=255, null=True, blank=True)),
                ('screen_name', models.CharField(max_length=255, null=True, blank=True)),
                ('verified', models.IntegerField(null=True, blank=True)),
                ('time_zone', models.CharField(max_length=255, null=True, blank=True)),
                ('utc_offset', models.IntegerField(null=True, blank=True)),
                ('protected', models.IntegerField(null=True, blank=True)),
                ('location', models.CharField(max_length=255, null=True, blank=True)),
                ('lang', models.CharField(max_length=255, null=True, blank=True)),
                ('followers_count', models.IntegerField(null=True, blank=True)),
                ('created_date', models.DateTimeField()),
                ('statuses_count', models.IntegerField(null=True, blank=True)),
                ('friends_count', models.IntegerField(null=True, blank=True)),
                ('favourites_count', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='user',
            field=models.ForeignKey(blank=True, to='twote.User', null=True),
        ),
    ]
