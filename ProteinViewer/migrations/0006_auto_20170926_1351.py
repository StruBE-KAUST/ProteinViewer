# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-26 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ProteinViewer', '0005_auto_20170926_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='viewingsession',
            name='asset_string',
            field=models.CharField(default=b'', max_length=1000000),
        ),
        migrations.AddField(
            model_name='viewingsession',
            name='entity_string',
            field=models.CharField(default=b'', max_length=1000000),
        ),
    ]
