# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0008_auto_20170205_2123'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutgoingConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('auto_send', models.BooleanField()),
                ('default_send_interval', models.IntegerField(default=15)),
            ],
            options={
                'db_table': 'twote_outgoingconfig',
            },
        ),
        migrations.CreateModel(
            name='OutgoingTweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('tweet', models.CharField(max_length=255)),
                ('approved', models.IntegerField(default=0, choices=[(0, 'Needs_action'), (1, 'Approved'), (2, 'Denied')])),
                ('time_interval', models.IntegerField(null=True, blank=True)),
                ('scheduled_time', models.DateTimeField(default=None, null=True, blank=True)),
                ('task_scheduled', models.BooleanField(default=False)),
                ('sent_time', models.DateTimeField(default=None, null=True, blank=True)),
            ],
            options={
                'db_table': 'twote_outgoingtweet',
            },
        ),
    ]
