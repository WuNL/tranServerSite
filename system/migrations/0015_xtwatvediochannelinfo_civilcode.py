# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-29 07:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0014_auto_20180125_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='xtwatvediochannelinfo',
            name='civilcode',
            field=models.CharField(blank=True, default='11111111111111111111', max_length=20, null=True),
        ),
    ]
