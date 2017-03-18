# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0007_tweet_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='bounding_box_coordinates',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='country',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='country_code',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='full_name',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='id_str',
            field=models.CharField(default='', max_length=256, db_index=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='place_type',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='url',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='id_str',
            field=models.CharField(default='', max_length=256, db_index=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='in_reply_to_id_str',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='location',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='source',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='tags',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='text',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='id_str',
            field=models.CharField(default='', max_length=256, db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='lang',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='location',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='screen_name',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='time_zone',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
