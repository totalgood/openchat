# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twote', '0004_auto_20161227_0243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(serialize=False, primary_key=True),
        ),
    ]
