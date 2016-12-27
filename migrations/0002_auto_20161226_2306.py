# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='place',
            table='place',
        ),
        migrations.AlterModelTable(
            name='tweet',
            table='tweet',
        ),
        migrations.AlterModelTable(
            name='user',
            table='user',
        ),
    ]
