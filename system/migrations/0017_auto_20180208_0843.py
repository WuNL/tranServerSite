# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-08 00:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0016_auto_20180207_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xtwatvediochannelinfo',
            name='endtime',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='\u7ed3\u675f\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='xtwatvediochannelinfo',
            name='starttime',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='\u5f00\u59cb\u65f6\u95f4'),
        ),
    ]
