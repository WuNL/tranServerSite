# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-01-25 03:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_auto_20171220_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mediaserverip', models.CharField(blank=True, max_length=45, null=True)),
                ('mediaserverport', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
