# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0005_auto_20161227_0245'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='modified_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='favorite_count',
            field=models.IntegerField(default=-1, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='favourites_count',
            field=models.IntegerField(default=-1, null=True),
        ),
    ]
