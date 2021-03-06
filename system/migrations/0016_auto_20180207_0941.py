# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-02-07 01:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0015_xtwatvediochannelinfo_civilcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='ploicelog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operatetype', models.IntegerField(blank=True, null=True)),
                ('videotime', models.DateTimeField(auto_now=True, null=True, verbose_name='\u89c6\u9891\u65f6\u95f4')),
                ('calltime', models.DateTimeField(auto_now=True, null=True, verbose_name='\u8c03\u9605\u65f6\u95f4')),
                ('deptname', models.CharField(blank=True, max_length=45, null=True)),
                ('groupname', models.CharField(blank=True, max_length=45, null=True)),
                ('ename', models.CharField(blank=True, max_length=45, null=True)),
                ('channelname', models.CharField(blank=True, max_length=45, null=True)),
                ('logevent', models.CharField(blank=True, max_length=100, null=True)),
                ('userid', models.IntegerField(blank=True, db_column='userID', null=True)),
                ('loglevel', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'policelog',
            },
        ),
        migrations.AddField(
            model_name='server',
            name='chairman',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='\u662f\u5426\u4e3b\u673a'),
        ),
        migrations.AddField(
            model_name='server',
            name='mediaserverip',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
        migrations.AddField(
            model_name='server',
            name='mediaserverport',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='xtwatvediochannelinfo',
            name='downloadauthority',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='\u4e0b\u8f7d\u6743\u9650'),
        ),
        migrations.AddField(
            model_name='xtwatvediochannelinfo',
            name='endtime',
            field=models.DateTimeField(auto_now=True, db_column='\u7ed3\u675f\u65f6\u95f4', null=True),
        ),
        migrations.AddField(
            model_name='xtwatvediochannelinfo',
            name='playbackauthority',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='\u56de\u653e\u6743\u9650'),
        ),
        migrations.AddField(
            model_name='xtwatvediochannelinfo',
            name='starttime',
            field=models.DateTimeField(auto_now=True, db_column='\u5f00\u59cb\u65f6\u95f4', null=True),
        ),
    ]
