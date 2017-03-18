# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0002_auto_20161226_2306'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='place',
            table='twote_place',
        ),
        migrations.AlterModelTable(
            name='tweet',
            table='twote_tweet',
        ),
        migrations.AlterModelTable(
            name='user',
            table='twote_user',
        ),
    ]
