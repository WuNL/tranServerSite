#coding:utf-8
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Actionlog(models.Model):
    operatetime = models.DateTimeField(db_column='operateTime', blank=True, null=True,auto_now=True)  # Field name made lowercase.
    logevent = models.CharField(max_length=100, blank=True, null=True)
    userid = models.IntegerField(db_column='userID', blank=True, null=True)  # Field name made lowercase.
    loglevel = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'actionlog'

class ploicelog(models.Model):
    # operatetype 0:查看 1：回看 2：下载
    operatetype = models.IntegerField(blank=True, null=True) 
    videotime = models.DateTimeField(verbose_name=u'视频时间', blank=True, null=True,auto_now=True)  # Field name made lowercase.
    calltime = models.DateTimeField(verbose_name=u'调阅时间', blank=True, null=True,auto_now=True)
    deptname = models.CharField(max_length=45, blank=True, null=True)
    groupname = models.CharField(max_length=45, blank=True, null=True)
    ename = models.CharField(max_length=45, blank=True, null=True)
    channelname = models.CharField(max_length=45, blank=True, null=True)

    logevent = models.CharField(max_length=100, blank=True, null=True)
    userid = models.IntegerField(db_column='userID', blank=True, null=True)  # Field name made lowercase.
    loglevel = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'policelog'

class AddressMapping(models.Model):
    outerip = models.CharField(verbose_name=u"外网IP",db_column='outerIP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    outerport = models.IntegerField(db_column='outerPort', blank=True, null=True)  # Field name made lowercase.
    innerip = models.CharField(verbose_name=u"内网IP",db_column='innerIP', max_length=50, blank=True, null=True)  # Field name made lowercase.
    innerport = models.IntegerField(db_column='innerPort', blank=True, null=True)  # Field name made lowercase.
    class Meta:
        unique_together = ('outerip','innerip')
        db_table = 'address_mapping'



class Clientterminal(models.Model):
    registerid = models.CharField(db_column='RegisterID', max_length=45)  # Field name made lowercase.
    username = models.CharField(max_length=45, blank=True, null=True)
    password = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=45, blank=True, null=True,unique=True)
    clienttype = models.IntegerField(db_column='clientType', blank=True, null=True)  # Field name made lowercase.
    expires = models.DateTimeField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'clientterminal'

class IcbcDb(models.Model):
    dbip = models.CharField(max_length=45, blank=True, null=True)
    username = models.CharField(max_length=45, blank=True, null=True)
    password = models.CharField(max_length=45, blank=True, null=True)
    dbname = models.CharField(max_length=45, blank=True, null=True)
    districtcode = models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        db_table = 'icbcdb'

#unused
class Monitoring(models.Model):
    sipid = models.CharField(db_column='sipID', max_length=45, blank=True, null=True)  # Field name made lowercase.
    remoteip = models.CharField(db_column='remoteIP', max_length=45, blank=True, null=True)  # Field name made lowercase.
    remoteport = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'monitoring'

class Server(models.Model):
    serverid = models.AutoField(primary_key=True)

    chairman = models.IntegerField(verbose_name=u"是否主机",default=0,blank=True, null=True)

    servername = models.CharField(max_length=45, blank=True, null=True)
    serverip = models.CharField(max_length=45, blank=True, null=True)
    serverport = models.IntegerField(blank=True, null=True)
    sipport = models.IntegerField(db_column='sipPort', blank=True, null=True)  # Field name made lowercase.
    devicelimitecode = models.CharField(max_length=50, blank=True, null=True)
    devicelimite = models.IntegerField(blank=True, null=True)
    servermask = models.CharField(max_length=45, blank=True, null=True)
    gateway = models.CharField(max_length=45, blank=True, null=True)

    mediaserverip = models.CharField(max_length=45, blank=True, null=True)
    mediaserverport = models.IntegerField(blank=True, null=True)    

    playbackauthority = models.IntegerField(verbose_name=u"回放权限",blank=True, null=True,default=0)
    downloadauthority = models.IntegerField(verbose_name=u"下载权限",blank=True, null=True,default=0)

    class Meta:
        db_table = 'server'

class MediaServer(models.Model):
    mediaserverip = models.CharField(max_length=45, blank=True, null=True)
    mediaserverport = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'mediaserver'

class Users(models.Model):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=45, blank=True, null=True, unique=True)
    password = models.CharField(max_length=45, blank=True, null=True)
    usertype = models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        db_table = 'users'

class XtWatvediochannelinfo(models.Model):
    sipid = models.CharField(db_column='sipID', max_length=45)  # Field name made lowercase.
    devicename = models.CharField(max_length=45, blank=True, null=True)
    deviceip = models.CharField(max_length=45, blank=True, null=True)
    tcpport = models.IntegerField(blank=True, null=True)
    devicetype = models.IntegerField(blank=True, null=True)
    streamtransmode = models.IntegerField(blank=True, null=True)
    rasuser = models.CharField(max_length=45, blank=True, null=True)
    raspassword = models.CharField(max_length=45, blank=True, null=True)
    groupid = models.IntegerField(blank=True, null=True)
    channelid = models.IntegerField(blank=True, null=True,unique=True)
    devicechannelindex = models.IntegerField(blank=True, null=True)
    streamserverip = models.CharField(max_length=45, blank=True, null=True)
    streamtcpport = models.IntegerField(blank=True, null=True)
    nlcserverport = models.IntegerField(blank=True, null=True)
    nlcclientport = models.IntegerField(blank=True, null=True)
    streamusername = models.CharField(max_length=45, blank=True, null=True)
    streamuserpws = models.CharField(max_length=45, blank=True, null=True)
    deptname = models.CharField(max_length=45, blank=True, null=True)
    groupname = models.CharField(max_length=45, blank=True, null=True)
    ename = models.CharField(max_length=45, blank=True, null=True)
    channelname = models.CharField(max_length=45, blank=True, null=True)
    
    civilcode = models.CharField(max_length=20,default="11111111111111111111", blank=True, null=True)

    usemediaserver = models.IntegerField(blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    terminalid = models.IntegerField(blank=True, null=True)
    districtcode = models.IntegerField(blank=True, null=True)

    playbackauthority = models.IntegerField(verbose_name=u"回放权限",blank=True, null=True,default=0)
    downloadauthority = models.IntegerField(verbose_name=u"下载权限",blank=True, null=True,default=0)   
    starttime = models.DateTimeField(verbose_name=u'开始时间', blank=True, null=True,auto_now=True)
    endtime =  models.DateTimeField(verbose_name=u'结束时间', blank=True, null=True,auto_now=True)
    class Meta:
        db_table = 'xt_watvediochannelinfo'

class sipInfo(models.Model):
    centerCode = models.CharField(verbose_name=u"中心编码",max_length=8, blank=False, null=False)
    industryCode = models.CharField(verbose_name=u"行业编码",max_length=2, blank=False, null=False)
    typeCode = models.CharField(verbose_name=u"类型编码",default="131",max_length=3, blank=False, null=False)
    class Meta:
        db_table = 'sipInfo'
