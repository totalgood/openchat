# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0003_auto_20161226_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='id_str',
            field=models.CharField(default='', max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='id_str',
            field=models.CharField(default='', max_length=255, db_index=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='in_reply_to_id_str',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='id_str',
            field=models.CharField(default='', max_length=255, db_index=True),
        ),
    ]
