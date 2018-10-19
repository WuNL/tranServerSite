# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-10 02:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_auto_20170719_0853'),
    ]

    operations = [
        migrations.CreateModel(
            name='sipInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('centerCode', models.CharField(max_length=8, verbose_name='\u4e2d\u5fc3\u7f16\u7801')),
                ('industryCode', models.CharField(default='131', max_length=3, verbose_name='\u7c7b\u578b\u7f16\u7801')),
            ],
            options={
                'db_table': 'sipInfo',
            },
        ),
    ]