#coding:utf-8
from  socket import *
from django.db.models import Q
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core import serializers
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
import json
import datetime
import wmi,pythoncom,win32com
from system.forms import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from funMoudle.views import if_not_zby
#sql server
import pyodbc
import random
import os


import httplib
mediaHost = "localhost"
# mediaHost = "10.25.12.18"

# Create your views here.

@login_required
def homeView(request):
	# localip = request.META['REMOTE_ADDR']
	# print localip
	now = datetime.datetime.now()
	pythoncom.CoInitialize()
	nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)
	if len(nic_configs)<1:
		print u"找不到网卡"
		networkAdapter = networkAdapterForm()
		return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail','msgContent':u'找不到网卡'})
	interface = nic_configs[0]
	localIP = interface.IPAddress[0]


	useSimpleHome = False
	cf = ConfigParser.ConfigParser()
	# if no setting, all letter will be maked lower case
	cf.optionxform = str
	try:
		cf.read(u"webParams.ini")
		srcDict = {}
		for section in cf.sections():
			for item in cf.items(section):
				if item[0] == "homestyle" and item[1]=="0":
					useSimpleHome = True
					# return render(request,'system/simplehome.html',{"time":now,"localIP":localIP,"userip":localip})

	except error as e:
		print e
	try:
		httpClient=httplib.HTTPConnection(mediaHost,8090,timeout=5)
		# httpClient.request('GET',r'/{"msg_type":"server_status"}')
		httpClient.request('GET',r'/{"msg_type":"real_play_status","msg_id":"1"}')
		response=httpClient.getresponse()
		data = response.read()


		httpClient.request('GET',r'/{"msg_type":"download_status","msg_id":"1"}')
		dlresponse=httpClient.getresponse()
		downloaddata = dlresponse.read()

		httpClient.request('GET',r'/{"msg_type":"play_back_status","msg_id":"1"}')
		pbresponse=httpClient.getresponse()
		playbackdata = pbresponse.read()		


		js = json.loads(data)
		dljs = json.loads(downloaddata)
		pbjs = json.loads(playbackdata)
		
		objectList = []
		dlobjects = []
		pbobjects = []
		
		if js['ret_body'] is not None:
			print "js:",js
			for channel in js['ret_body']:
				dvrip =  channel['nvr_ip']
				devicechannelindex = channel['channel_index']
				print dvrip,"----",devicechannelindex
				result = XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) & Q(devicechannelindex=devicechannelindex))
				if result.count() == 0:
					print "no"
				else:
					print result.first().channelname,result.first().groupname,result.first().ename,result.first().deptname
					if channel['remote_ip']!=localip:
						objectList.append([result.first(),channel['remote_ip'],channel['remote_port']])
				# print XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) | Q(devicechannelindex=devicechannelindex)).count()
		
		if dljs['ret_body'] is not None:
			print "dljs:",dljs
			for channel in dljs['ret_body']:
				dvrip =  channel['nvr_ip']
				devicechannelindex = channel['channel_index']
				result = XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) & Q(devicechannelindex=devicechannelindex))
				if result.count() != 0:
					dlobjects.append([result.first(),channel['remote_ip'],channel['remote_port']])
		if pbjs['ret_body'] is not None:
			print "pbjs:",pbjs
			for channel in pbjs['ret_body']:
				dvrip =  channel['nvr_ip']
				devicechannelindex = channel['channel_index']
				result = XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) & Q(devicechannelindex=devicechannelindex))
				if result.count() != 0:
					pbobjects.append([result.first(),channel['remote_ip'],channel['remote_port']])					
		if useSimpleHome:
			return render(request,'system/simplehome.html',{"time":now,"localIP":localIP,"objectList":objectList,"dlobjects":dlobjects,"pbobjects":pbobjects})
		return render(request,'system/home1.html',{"time":now,"localIP":localIP,"objectList":objectList,"dlobjects":dlobjects,"pbobjects":pbobjects})

	except error as e:
		print u"无法连接媒体服务"
		return render(request,'system/simplehome.html',{"time":now,"localIP":localIP})
	except TypeError as e:
		print u"解析失败",e
	except Exception as e:
		print u"其他错误",e

	if useSimpleHome:
		return render(request,'system/simplehome.html',{"time":now,"localIP":localIP})

	return render(request,'system/home1.html',{"time":now,"localIP":localIP,"userip":localip})

@login_required
def closeChannelView(request,remoteip,remoteport):
	print remoteip,remoteport
	print str(remoteip),remoteport
	try:
		httpClient=httplib.HTTPConnection(mediaHost,8090,timeout=5)
		msgtosend = '/{"msg_type":"close_channel","remote_ip":"%s","remote_port":"%d"}' % (remoteip,int(remoteport))
		print "msg is : ",msgtosend
		httpClient.request('GET',msgtosend)
		response=httpClient.getresponse()
		data = response.read()

		print data

	except error as e:
		print u"无法连接媒体服务"
	except TypeError as e:
		print u"解析失败"
	except Exception as e:
		print u"其他错误"
	return HttpResponseRedirect("/home")

@login_required
def configNETView(request):
	if request.POST:
		networkAdapter = networkAdapterForm(request.POST)
		print networkAdapter
		if networkAdapter.is_valid():
			print "form is valid"
			pythoncom.CoInitialize()
			nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)
			if len(nic_configs)<1:
				return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail','msgContent':u'找不到可用网卡'})
			interface = nic_configs[0]
			arrIPAddress = [networkAdapter.cleaned_data['IP']]
			arrIPSubnet = [networkAdapter.cleaned_data['IPSubnet']]
			arrDefaultGateway = [networkAdapter.cleaned_data['DefaultIPGateway']]
			arrGatewayCostMetrics = [1]
			print arrIPAddress,arrIPSubnet,arrDefaultGateway
			intReboot = 0
			returnvalue = interface.EnableStatic(IPAddress=arrIPAddress,SubnetMask=arrIPSubnet)
			if returnvalue[0] == 0:
				print u"修改IP和掩码成功！"
			elif returnvalue[0] == 1:
				print "需要重启+1"
				intReboot+=1
			else:
				print "设置IP和掩码失败"
				return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail','msgContent':u'设置IP和掩码失败'})
			returnvalue = interface.SetGateways(DefaultIPGateway = arrDefaultGateway,GatewayCostMetric = arrGatewayCostMetrics)
			if returnvalue[0] == 0:
				print u"修改网关成功！"
			elif returnvalue[0] == 1:
				print "需要重启+1"
				intReboot+=1
			else:
				print "设置网关失败"
				return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail','msgContent':u'设置网关失败'})
			if intReboot > 0:	
				ActionlogInstance = Actionlog(userid=119,logevent=u"配置网卡",loglevel="0")
				ActionlogInstance.save()				
				return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'success','msgContent':u'设置成功，重启后生效'})
			else:
				ActionlogInstance = Actionlog(userid=119,logevent=u"配置网卡",loglevel="0")
				ActionlogInstance.save()				
				return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'success','msgContent':u'设置成功'})
		else:
			return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail'})
	pythoncom.CoInitialize()
	nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)
	if len(nic_configs)<1:
		print u"找不到网卡"
		networkAdapter = networkAdapterForm()
		return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail','msgContent':u'找不到网卡'})
	interface = nic_configs[0]
	netinfoDict = {}

	if interface.IPAddress is not None:
		netinfoDict["IP"] = interface.IPAddress[0]
	else:
		netinfoDict["IP"] = ""

	if interface.IPSubnet is not None:
		netinfoDict["IPSubnet"] = interface.IPSubnet[0]
	else:
		netinfoDict["IPSubnet"] = ""

	if interface.DefaultIPGateway is not None:
		netinfoDict["DefaultIPGateway"] = interface.DefaultIPGateway[0]
	else:
		netinfoDict["DefaultIPGateway"] = ""
		
	print netinfoDict
	networkAdapter = networkAdapterForm(data=netinfoDict)
	print networkAdapter
	return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter})

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def configRemoteDatabaseView(request):
	if IcbcDb.objects.count()<1:
		IcbcDbInstance = IcbcDb(pk=1,dbip="192.168.1.1",username='postgres',password='root')
		IcbcDbInstance.save()
	if request.POST:
		IcbcDbInstance = IcbcDb.objects.get(pk=1)
		form = remoteDatabaseParamsModelForm(instance=IcbcDbInstance,data=request.POST)
		if form.is_valid():
			instance = form.save(commit=True)
			ActionlogInstance = Actionlog(userid=119,logevent=u"配置远程数据库为："+IcbcDbInstance.dbip,loglevel="0")
			ActionlogInstance.save()			
			return render(request,'system/configRemoteDatabase.html',{'remoteDatabaseParamsForm':form,'msg':'success','msgContent':u"修改成功"})
		else:
			print "form is not valid"
			return render(request,'system/configRemoteDatabase.html',{'remoteDatabaseParamsForm':form,'msg':'fail','msgContent':u"发生错误"})
	IcbcDbInstance = IcbcDb.objects.get(pk=1)
	form = remoteDatabaseParamsModelForm(instance=IcbcDbInstance)
	return render(request,'system/configRemoteDatabase.html',{'remoteDatabaseParamsForm':form})

import copy

@login_required
def testView(request):
	sqlServer = IcbcDb.objects.get(pk=1)
	ip = sqlServer.dbip
	un = sqlServer.username
	password = sqlServer.password
	command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
	try:
		cn=pyodbc.connect(command)
		cn.timeout=1
		cursor=cn.cursor()
		cursor.execute("select * from(select distinct s.ID as TerminalID, s.DomainName as DeviceName,s.ServerIP as DeviceIP,\
 s.TCPPort,c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
 'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,c.UseMediaServer\
  from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
 on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
 on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd\
 on c.ID=gd.DeviceID left outer join\
 (select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g, [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d\
 where g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join\
 (select e1.ID,e1.EName ChName,e2.EName DvrName\
 from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e1,[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2\
 where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join\
 (select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,(case c2.code when 0 then '0' \
 else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort\
 from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
 from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] .[iSOS_Admin30].[VideoEqMediaServer] s1\
 on c2.code=s1.ID) s2 on c.ID=s2.ID) tb  where DeviceType = 0 or DeviceType =1 ")
		data = cursor.fetchall()
		cursor.connection.close()	
		for row in data[0:10]:
			print "-------------------------"
			print row.GroupName,repr(row.GroupName.decode("gbk"))
			print row.DeptName,repr(row.DeptName)
			print row.EName,repr(row.EName.decode("gbk"))
			print row.ChannelName,repr(row.ChannelName.decode("gbk"))
			print "*************************"
	except Exception, e:
		print "odbc error:",e				
	return HttpResponseRedirect("/home")


def getJsonFromISOS():
	sqlServer = IcbcDb.objects.get(pk=1)
	ip = sqlServer.dbip
	un = sqlServer.username
	password = sqlServer.password
	command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
	try:
		cn=pyodbc.connect(command)
		cn.timeout=1
		cursor=cn.cursor()
		rawsqlcmd = "select * from(\
			select distinct s.ID as TerminalID, s.DomainName as DeviceName,s.ServerIP as DeviceIP,s.TCPPort,\
			c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,\
			s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
			'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,\
			g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,e4.PosName,c.UseMediaServer from \
			[iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
			on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
			 on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd \
			 on c.ID=gd.DeviceID left outer join \
			(select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g,\
			 [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d where \
			 g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join \
			 (select e1.ID,e1.EName ChName,e2.EName DvrName, e1.PosName\
			from (select tmp1.*,tmp2.DictText as PosName from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] tmp1,\
			iSOSDB_30.iSOS_Admin30.iSosDictionary20009 tmp2 where tmp1.Position=tmp2.DictValue) e1,\
			[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2 where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join \
			(select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,\
			(case c2.code when 0 then '0' else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) \
			as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort \
			from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
			from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] \
			.[iSOS_Admin30].[VideoEqMediaServer] s1\
			on c2.code=s1.ID) s2 on c.ID=s2.ID) tb"
		cursor.execute(rawsqlcmd+" where DeviceType = 0 or DeviceType =1 ")
		data = cursor.fetchall()
		cursor.connection.close()
		mylist = []
		# 存放每个支行数据的结构 {"XX支行":1,"..."}
		deptNameDict = {}
		# {"XX支行 XX网点":1,}
		groupNameDict = {}
		enameDict = {}
		# 存放真正数据的结构{"text":"XX支行","nodes":[...]}
		deptRootDict = {}

		for row in data:
			# 部门已经存在
			if row.DeptName in deptNameDict:
				pass
			# 新部门，需要在json中添加部门	
			else:
				deptNameDict[row.DeptName] = 1
				deptRootDict[row.DeptName] = {}
				deptRootDict[row.DeptName]["text"] = row.DeptName
			# 支行已存在
			if row.GroupName.decode("gbk")+row.DeptName in groupNameDict:
				pass
			# 新支行，需要在json中添加支行nodes
			else:
				pass

				groupNameDict[row.GroupName.decode("gbk")+row.DeptName] = 1
				if "nodes" not in deptRootDict[row.DeptName]:
					deptRootDict[row.DeptName]["nodes"] = []
				tmpGroupDict = {}
				tmpGroupDict["text"] = row.GroupName
				deptRootDict[row.DeptName]["nodes"].append(tmpGroupDict)
			# 老主机
			if row.EName.decode("gbk")+row.GroupName.decode("gbk")+row.DeptName in enameDict:
				# item当前支行，是个dict
				for item in deptRootDict[row.DeptName]["nodes"]:
					if "text" in item and item["text"] != row.GroupName:
						continue
					# item["nodes"] 主机
					# 遍历支行下面的所有主机
					for item1 in item["nodes"]:
						if "text" in item1 and item1["text"] != row.EName:
							continue
						item1["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
			# 新主机，需要在网点的nodes列表中添加主机
			else:
				# print row.EName," ",row.GroupName," ",row.DeptName
				enameDict[row.EName.decode("gbk")+row.GroupName.decode("gbk")+row.DeptName] = 1
				if "nodes" not in deptRootDict[row.DeptName]:
					pass
					# deptRootDict[row.DeptName]["nodes"] = []
				# item当前支行，是个dict
				for item in deptRootDict[row.DeptName]["nodes"]:
					if "text" in item and item["text"] != row.GroupName:
						continue
					# 如果主机在支行dict中
					if row.EName in item.values():
						pass
						# item["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
					# 该主机不在支行dict中，则需要添加
					else:
						tmpEDict = {}
						tmpEDict["text"] = row.EName
						tmpEDict["nodes"] = []
						tmpEDict["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
						if "nodes" not in item:
							item["nodes"] = []
						item["nodes"].append(tmpEDict)
		for key in deptRootDict:
			mylist.append(deptRootDict[key])
		json_reply = json.dumps(mylist,encoding="gbk")
	except Exception, e:
		print "odbc error:",e	
		return "error"
	return json_reply

@login_required
def configJQ(request):
	if request.is_ajax():
		if IcbcDb.objects.count() == 0:
			return HttpResponse(u"请先配置远端数据库地址！")

		needfilter = False
		filterCMD = ""

		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str
		try:
			cf.read(u"webParams.ini")
			srcDict = {}
			for section in cf.sections():
				for item in cf.items(section):
					if "filter_" in item[0]:
						needfilter = True
						if filterCMD!="":
							filterCMD += " or "
							filterCMD += ("DeviceType = %s" % item[1])
						else:
							filterCMD = (" DeviceType = %s" % item[1] )
			if needfilter:
				filterCMD = " where "+filterCMD
			else:
				filterCMD = ""


		except error as e:
			print e


		sqlServer = IcbcDb.objects.get(pk=1)
		ip = sqlServer.dbip
		un = sqlServer.username
		password = sqlServer.password
		command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
		try:
			cn=pyodbc.connect(command)
			cn.timeout=1
			cursor=cn.cursor()
			rawsqlcmd = "select * from(\
				select distinct s.DomainName as DeviceName,s.ServerIP as DeviceIP,s.TCPPort,\
				c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,\
				s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
				'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,\
				g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,e4.PosName,c.UseMediaServer from \
				[iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
				on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
				 on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd \
				 on c.ID=gd.DeviceID left outer join \
				(select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g,\
				 [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d where \
				 g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join \
				 (select e1.ID,e1.EName ChName,e2.EName DvrName, e1.PosName\
				from (select tmp1.*,tmp2.DictText as PosName from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] tmp1,\
				iSOSDB_30.iSOS_Admin30.iSosDictionary20009 tmp2 where tmp1.Position=tmp2.DictValue) e1,\
				[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2 where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join \
				(select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,\
				(case c2.code when 0 then '0' else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) \
				as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort \
				from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
				from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] \
				.[iSOS_Admin30].[VideoEqMediaServer] s1\
				on c2.code=s1.ID) s2 on c.ID=s2.ID) tb"
			if needfilter:
				rawsqlcmd += filterCMD
	
			cursor.execute(rawsqlcmd)
			data = cursor.fetchall()
			# for row in data:
			# 	pass
			# 	print '--',row.DeptName,row.GroupName,row.EName,row.ChannelName,row.ChannelID
			# for row in data:
			# 	for i,value in enumerate(row):
			# 		print cursor.description[i][0],"---",value

			# r=[dict((cursor.description[i][0],value)\
			# 	for i,value in enumerate(row)) for row in data]
			cursor.connection.close()
			print len(data)
			mylist = []

			# 存放每个支行数据的结构 {"XX支行":1,"..."}
			deptNameDict = {}
			# {"XX支行 XX网点":1,}
			groupNameDict = {}
			enameDict = {}
			# 存放真正数据的结构{"text":"XX支行","nodes":[...]}
			deptRootDict = {}

			print len(data)

			for row in data:
				if type(row.GroupName) is not unicode:
					gn = row.GroupName.decode("gbk")
				else:
					gn = row.GroupName
				if type(row.DeptName) is not unicode:
					dn = row.DeptName.decode("gbk")
				else:
					dn = row.DeptName

				if type(row.EName) is not unicode:
					en = row.EName.decode("gbk")
				else:
					en = row.EName
				if type(row.ChannelName) is not unicode:
					cn = row.ChannelName.decode("gbk")
				else:
					cn = row.ChannelName															
				try:

					# print '--',row.DeptName,row.GroupName,row.EName,row.ChannelName,row.ChannelID
					# 部门已经存在
					if dn in deptNameDict:
						pass
					# 新部门，需要在json中添加部门	
					else:
						deptNameDict[dn] = 1
						deptRootDict[dn] = {}
						deptRootDict[dn]["text"] = dn

					# 支行已存在
					# print "-------------))"
					if gn+dn in groupNameDict:
						# print "-------------"
						# print type(gn)
						# print gn
						# print type(dn)
						# print dn
						pass
					# 新支行，需要在json中添加支行nodes
					else:
						pass

						groupNameDict[gn+dn] = 1
						if "nodes" not in deptRootDict[dn]:
							deptRootDict[dn]["nodes"] = []
						tmpGroupDict = {}
						tmpGroupDict["text"] = gn
						deptRootDict[dn]["nodes"].append(tmpGroupDict)
					# 老主机
					if en+gn+dn in enameDict:
						# item当前支行，是个dict
						for item in deptRootDict[dn]["nodes"]:
							if "text" in item and item["text"] != gn:
								continue
							# item["nodes"] 主机
							# 遍历支行下面的所有主机
							if "nodes" not in item:
								item["nodes"] = []
							for item1 in item["nodes"]:
								if "text" in item1 and item1["text"] != en:
									continue
								item1["nodes"].append({"text":cn,"tags":[row.ChannelID]})
							# item["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
					# 新主机，需要在网点的nodes列表中添加主机
					else:
						# print row.EName," ",row.GroupName," ",dn
						enameDict[en+gn+dn] = 1
						if "nodes" not in deptRootDict[dn]:
							deptRootDict[dn]["nodes"] = []
							# deptRootDict[dn]["nodes"] = []
						# item当前支行，是个dict
						for item in deptRootDict[dn]["nodes"]:
							if "text" in item and item["text"] != gn:
								continue
							# 如果主机在支行dict中
							if en in item.values():
								pass
								# item["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
							# 该主机不在支行dict中，则需要添加
							else:

								tmpEDict = {}
								tmpEDict["text"] = en
								tmpEDict["nodes"] = []
								tmpEDict["nodes"].append({"text":cn,"tags":[row.ChannelID]})
								if "nodes" not in item:
									item["nodes"] = []
								item["nodes"].append(tmpEDict)

				except Exception,e:

					print "loop error!",e
					print row.GroupName,repr(row.GroupName)	,type(row.GroupName)
					print dn,repr(dn),type(dn)	
					print row.EName,repr(row.EName)	,type(row.EName)
					print row.ChannelName,repr(row.ChannelName)	,type(row.ChannelName)		
					break
				
			# mydict = {"text":u"色粉色","tags":["4"]}

			# for key in deptRootDict:
			keys = deptRootDict.keys()
			keys.sort()
			for key in keys:
				mylist.append(deptRootDict[key])
			# for item in mylist:
			# 	print item
			json_reply = json.dumps(mylist,encoding="gbk")
			# json_reply = json.dumps(mylist,ensure_ascii=False)
			
			# print json_reply
			# json_reply = json.JSONEncoder().encode([{'text': '是否','href': '#parent1','tags': ['4']},{'text': 'Parent 2','href': '#parent2','tags': ['4']}])
			return HttpResponse(json_reply)
		except Exception, e:
			print "odbc error:",e	
			return HttpResponse(e)
	users = Users.objects.filter(usertype=1)
	if IcbcDb.objects.count()==0:
		errormsg = u"请先设置远端数据库地址"
		return render(request,'system/treeview.html',{'msg':errormsg})
	sqlServer = IcbcDb.objects.get(pk=1)
	ip = sqlServer.dbip
	un = sqlServer.username
	password = sqlServer.password
	command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
	try:
		cn=pyodbc.connect(command)
		cn.timeout=1
		cursor=cn.cursor()
		cursor.execute("select * from [iSOSDB_30].[iSOS_Admin30].[iSosDictionary20009]")
		data = cursor.fetchall()

		cursor.connection.close()
		retPosList = []
		for row in data:
			if type(row.DictText) is not unicode:
				posName = row.DictText.decode("gbk")
			else:
				posName = row.DictText
			retPosList.append(posName.encode("utf8"))			

	except Exception, e:
		print "odbc error:",(e[1])
		if type(e[1]) is not unicode:
			errormsg = e[1].decode('gbk')
		else:
			errormsg = e[1]
		return render(request,'system/treeview.html',{'msg':errormsg})
	return render(request,'system/treeview.html',{"users":users,'posList':retPosList})

@login_required
@csrf_exempt
def filterRemoteAjaxView(request):
	if request.is_ajax():
		postData = request.POST.getlist("posList[]")
		if len(postData) == 0:
			filterCmd = ""
		else:
			filterCmd = " where "
			i = 0
			for pos in postData:
				if i == 0:
					filterCmd += "PosName='%s'" % pos
				else:
					filterCmd += " or PosName='%s'" % pos
				i+=1
		

		needfilter = False
		filterCMD = ""

		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str
		try:
			cf.read(u"webParams.ini")
			srcDict = {}
			for section in cf.sections():
				for item in cf.items(section):
					if "filter_" in item[0]:
						needfilter = True
						if filterCMD!="":
							filterCMD += " or "
							filterCMD += ("DeviceType = %s" % item[1])
						else:
							filterCMD = (" DeviceType = %s" % item[1] )



		except error as e:
			print e

		if needfilter:
			pass
		else:
			filterCMD = ""	

		if len(filterCmd) != 0 and len(filterCMD) != 0:	
			filterCmd += " and ("
			filterCmd += filterCMD
			filterCmd += ")"

		if len(filterCmd) == 0 and len(filterCMD) != 0:
			filterCmd = filterCMD
			filterCmd = " where " + filterCMD


		sqlServer = IcbcDb.objects.get(pk=1)
		ip = sqlServer.dbip
		un = sqlServer.username
		password = sqlServer.password
		command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
		try:
			cn=pyodbc.connect(command)
			cn.timeout=1
			cursor=cn.cursor()
			rawsqlcmd = "select * from(\
				select distinct s.ID as TerminalID, s.DomainName as DeviceName,s.ServerIP as DeviceIP,s.TCPPort,\
				c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,\
				s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
				'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,\
				g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,e4.PosName,c.UseMediaServer from \
				[iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
				on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
				 on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd \
				 on c.ID=gd.DeviceID left outer join \
				(select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g,\
				 [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d where \
				 g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join \
				 (select e1.ID,e1.EName ChName,e2.EName DvrName, e1.PosName\
				from (select tmp1.*,tmp2.DictText as PosName from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] tmp1,\
				iSOSDB_30.iSOS_Admin30.iSosDictionary20009 tmp2 where tmp1.Position=tmp2.DictValue) e1,\
				[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2 where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join \
				(select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,\
				(case c2.code when 0 then '0' else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) \
				as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort \
				from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
				from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] \
				.[iSOS_Admin30].[VideoEqMediaServer] s1\
				on c2.code=s1.ID) s2 on c.ID=s2.ID) tb"
			
		# 	rawsqlcmd = "select * from(select distinct s.ID as TerminalID, s.DomainName as DeviceName,s.ServerIP as DeviceIP,\
	 # s.TCPPort,c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
	 # 'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,c.UseMediaServer\
	 #  from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
	 # on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
	 # on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd\
	 # on c.ID=gd.DeviceID left outer join\
	 # (select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g, [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d\
	 # where g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join\
	 # (select e1.ID,e1.EName ChName,e2.EName DvrName\
	 # from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e1,[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2\
	 # where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join\
	 # (select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,(case c2.code when 0 then '0' \
	 # else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort\
	 # from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
	 # from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] .[iSOS_Admin30].[VideoEqMediaServer] s1\
	 # on c2.code=s1.ID) s2 on c.ID=s2.ID) tb"
			rawsqlcmd += filterCmd
			cursor.execute(rawsqlcmd)
			data = cursor.fetchall()
			cursor.connection.close()
			mylist = []
			# 存放每个支行数据的结构 {"XX支行":1,"..."}
			deptNameDict = {}
			# {"XX支行 XX网点":1,}
			groupNameDict = {}
			enameDict = {}
			# 存放真正数据的结构{"text":"XX支行","nodes":[...]}
			deptRootDict = {}

			print len(data)

			for row in data:
				if type(row.GroupName) is not unicode:
					gn = row.GroupName.decode("gbk")
				else:
					gn = row.GroupName
				if type(row.DeptName) is not unicode:
					dn = row.DeptName.decode("gbk")
				else:
					dn = row.DeptName

				if type(row.EName) is not unicode:
					en = row.EName.decode("gbk")
				else:
					en = row.EName
				if type(row.ChannelName) is not unicode:
					cn = row.ChannelName.decode("gbk")
				else:
					cn = row.ChannelName															
				try:

					# print '--',row.DeptName,row.GroupName,row.EName,row.ChannelName,row.ChannelID
					# 部门已经存在
					if dn in deptNameDict:
						pass
					# 新部门，需要在json中添加部门	
					else:
						deptNameDict[dn] = 1
						deptRootDict[dn] = {}
						deptRootDict[dn]["text"] = dn

					# 支行已存在
					# print "-------------))"
					if gn+dn in groupNameDict:
						# print "-------------"
						# print type(gn)
						# print gn
						# print type(dn)
						# print dn
						pass
					# 新支行，需要在json中添加支行nodes
					else:
						pass

						groupNameDict[gn+dn] = 1
						if "nodes" not in deptRootDict[dn]:
							deptRootDict[dn]["nodes"] = []
						tmpGroupDict = {}
						tmpGroupDict["text"] = gn
						deptRootDict[dn]["nodes"].append(tmpGroupDict)
					# 老主机
					if en+gn+dn in enameDict:
						# item当前支行，是个dict
						for item in deptRootDict[dn]["nodes"]:
							if "text" in item and item["text"] != gn:
								continue
							# item["nodes"] 主机
							# 遍历支行下面的所有主机
							if "nodes" not in item:
								item["nodes"] = []
							for item1 in item["nodes"]:
								if "text" in item1 and item1["text"] != en:
									continue
								item1["nodes"].append({"text":cn,"tags":[row.ChannelID]})
							# item["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
					# 新主机，需要在网点的nodes列表中添加主机
					else:
						# print row.EName," ",row.GroupName," ",dn
						enameDict[en+gn+dn] = 1
						if "nodes" not in deptRootDict[dn]:
							deptRootDict[dn]["nodes"] = []
							# deptRootDict[dn]["nodes"] = []
						# item当前支行，是个dict
						for item in deptRootDict[dn]["nodes"]:
							if "text" in item and item["text"] != gn:
								continue
							# 如果主机在支行dict中
							if en in item.values():
								pass
								# item["nodes"].append({"text":row.ChannelName,"tags":[row.ChannelID]})
							# 该主机不在支行dict中，则需要添加
							else:

								tmpEDict = {}
								tmpEDict["text"] = en
								tmpEDict["nodes"] = []
								tmpEDict["nodes"].append({"text":cn,"tags":[row.ChannelID]})
								if "nodes" not in item:
									item["nodes"] = []
								item["nodes"].append(tmpEDict)

				except Exception,e:

					print "loop error!",e
					print row.GroupName,repr(row.GroupName)	,type(row.GroupName)
					print dn,repr(dn),type(dn)	
					print row.EName,repr(row.EName)	,type(row.EName)
					print row.ChannelName,repr(row.ChannelName)	,type(row.ChannelName)		
					break
				
			# mydict = {"text":u"色粉色","tags":["4"]}

			# for key in deptRootDict:
			keys = deptRootDict.keys()
			keys.sort()
			for key in keys:
				mylist.append(deptRootDict[key])
			# for item in mylist:
			# 	print item
			json_reply = json.dumps(mylist,encoding="gbk")
			# json_reply = json.dumps(mylist,ensure_ascii=False)
			
			# print json_reply
			# json_reply = json.JSONEncoder().encode([{'text': '是否','href': '#parent1','tags': ['4']},{'text': 'Parent 2','href': '#parent2','tags': ['4']}])
			return HttpResponse(json_reply)
		except Exception, e:
			print "odbc error:",e	
			return HttpResponse("error")

@login_required			
@csrf_exempt
def configJQAjax(request):
	if request.is_ajax():
		if sipInfo.objects.count()<1:
			sipInfoInstance = sipInfo(centerCode="00000000",industryCode="00",typeCode="000")
			sipInfoInstance.save()
		sipInfoInstance = sipInfo.objects.all().first()
		sipFirstPart = sipInfoInstance.centerCode+sipInfoInstance.industryCode+sipInfoInstance.typeCode
		postData = request.POST.getlist("newList[]")
		curUserId = request.POST.get("curUser")

		needReplaceCivcode = False
		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str
		try:
			cf.read(u"webParams.ini")
			srcDict = {}
			for section in cf.sections():
				for item in cf.items(section):
					if item[0] == "tihuanbianma" and item[1]=="1":
						needReplaceCivcode = True

		except error as e:
			print e

		groupDict = getGroupParam()
		print groupDict
		# print postData,curUserId
		if len(postData) is 0:
			return HttpResponse("no data !")
		# 得到需要添加的channelID后，按照ID遍历本地数据库：
		# 没有 去工行数据库查询相关信息后添加到本地数据库
		# 有 更新数据
		# 完毕后返回json数据更新treeview
		sqlServer = IcbcDb.objects.get(pk=1)
		ip = sqlServer.dbip
		un = sqlServer.username
		password = sqlServer.password
		command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
		try:
			cn=pyodbc.connect(command)
			cn.timeout=1
			cursor=cn.cursor()
			rawsqlcmd = "select * from(\
				select distinct s.ID as TerminalID, s.DomainName as DeviceName,s.ServerIP as DeviceIP,s.TCPPort,\
				c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,\
				s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
				'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,\
				g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,e4.PosName,c.UseMediaServer from \
				[iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
				on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
				 on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd \
				 on c.ID=gd.DeviceID left outer join \
				(select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g,\
				 [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d where \
				 g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join \
				 (select e1.ID,e1.EName ChName,e2.EName DvrName, e1.PosName\
				from (select tmp1.*,tmp2.DictText as PosName from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] tmp1,\
				iSOSDB_30.iSOS_Admin30.iSosDictionary20009 tmp2 where tmp1.Position=tmp2.DictValue) e1,\
				[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2 where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join \
				(select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,\
				(case c2.code when 0 then '0' else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) \
				as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort \
				from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
				from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] \
				.[iSOS_Admin30].[VideoEqMediaServer] s1\
				on c2.code=s1.ID) s2 on c.ID=s2.ID) tb"
	 		
	 		for cid in postData:
				cursor.execute(rawsqlcmd + " where tb.ChannelId=%s" % cid)
				data = cursor.fetchall()
				# 对每条数据，去本地数据库查找channelId
				# 若找到 更新本地数据
				# 没找到 添加到本地
				allVCBeforeInsert = XtWatvediochannelinfo.objects.all()
				for row in data:

					if type(row.GroupName) is not unicode:
						gn = row.GroupName.decode("gbk")
					else:
						gn = row.GroupName
					if type(row.DeptName) is not unicode:
						dn = row.DeptName.decode("gbk")
					else:
						dn = row.DeptName

					if type(row.EName) is not unicode:
						en = row.EName.decode("gbk")
					else:
						en = row.EName
					if type(row.ChannelName) is not unicode:
						cn = row.ChannelName.decode("gbk")
					else:
						cn = row.ChannelName

					isInLocalDB = (allVCBeforeInsert.filter(channelid=row.ChannelID).count()!=0)
					seed = str(cid)
					random.seed(seed)
					sipid = sipFirstPart + str(random.randint(1000000,9999999))


					# 0130: 大连需求
					# 根据返回的字典添加支行的civilcode
					civcode = u"11111111111111111111" if (groupDict is None or dn not in groupDict.keys()) else groupDict[dn]
					if civcode is u'':
						civcode = u"11111111111111111111"

					# 0629：洛阳需求
					# 用地市行civcode替代行业编码


					if needReplaceCivcode:
						hycode0=civcode[8]
						hycode1=civcode[9]
						sipidList=list(sipid)
						sipidList[8] = hycode0
						sipidList[9] = hycode1
						sipid = u''.join(sipidList)

					# 不在本地数据库中，需要添加到本地数据库
					if isInLocalDB is False:
						instanceToSave = XtWatvediochannelinfo(sipid=str(sipid),deviceip=row.DeviceIP,tcpport=row.TCPPort,\
							devicetype=row.DeviceType,streamtransmode=row.StreamTransMode,rasuser=row.RasUser,\
							raspassword=row.RasPassword,groupid=row.GroupID,channelid=row.ChannelID,\
							devicechannelindex=row.DeviceChannelIndex,streamserverip=row.StreamServerIP,\
							streamtcpport=row.StreamTCPPort,nlcserverport=row.NLCServerPort,nlcclientport=row.NLCClientPort,\
							streamusername=row.StreamUserName,streamuserpws=row.StreamUserPWS,deptname=dn,\
							groupname=gn,\
							ename=en,\
							channelname=cn,civilcode=civcode,\
							userid=curUserId,terminalid=row.TerminalID,usemediaserver=row.UseMediaServer)
						instanceToSave.save()
					# 在本地数据库中，更新该信息
					# 用户不同时，直接覆盖。换成新用户
					else:
						needUpdateVideoChannel = XtWatvediochannelinfo.objects.filter(channelid=row.ChannelID)
						needUpdateVideoChannel.update(sipid=str(sipid),deviceip=row.DeviceIP,tcpport=row.TCPPort,\
							devicetype=row.DeviceType,streamtransmode=row.StreamTransMode,rasuser=row.RasUser,\
							raspassword=row.RasPassword,groupid=row.GroupID,channelid=row.ChannelID,\
							devicechannelindex=row.DeviceChannelIndex,streamserverip=row.StreamServerIP,\
							streamtcpport=row.StreamTCPPort,nlcserverport=row.NLCServerPort,nlcclientport=row.NLCClientPort,\
							streamusername=row.StreamUserName,streamuserpws=row.StreamUserPWS,deptname=dn,\
							groupname=gn,\
							ename=en,\
							channelname=cn,civilcode=civcode,\
							userid=curUserId,terminalid=row.TerminalID,usemediaserver=row.UseMediaServer)
							# print '--',row.GroupName,row.EName,row.ChannelName,row.DeviceType,row.DeviceIP
			cursor.connection.close()
			ActionlogInstance = Actionlog(userid=119,logevent=u"修改通道数据",loglevel="0")
			ActionlogInstance.save()			
		except Exception, e:
			print "odbc error:",type(e),e
		print "finished!!!"
		json_reply = getLocalFromModel(curUserId)
		if json_reply!= "error":
			return HttpResponse(json_reply)
		else:
			return HttpResponse(json_reply)


def getLocalFromModel(ajaxuserid):
	if ajaxuserid:
		# userInstance = get_object_or_404(Users,pk=int(ajaxuserid))
		videoChannels = reversed(XtWatvediochannelinfo.objects.filter(userid=ajaxuserid))
		# print videoChannels,videoChannels.count()
		mylist = []

		# 存放每个支行数据的结构 {"XX支行":1,"..."}
		deptNameDict = {}
		# {"XX支行 XX网点":1,}
		groupNameDict = {}
		enameDict = {}
		# 存放真正数据的结构{"text":"XX支行","nodes":[...]}
		deptRootDict = {}			
		for vc in videoChannels:
			# print '--',row.DeptName,row.GroupName,row.EName,row.ChannelName,row.ChannelID
			# 部门已经存在
			if vc.deptname in deptNameDict:
				pass
			# 新部门，需要在json中添加部门	
			else:
				deptNameDict[vc.deptname] = 1
				deptRootDict[vc.deptname] = {}
				deptRootDict[vc.deptname]["text"] = vc.deptname

			# 支行已存在
			# print "-------------))"
			if vc.groupname+vc.deptname in groupNameDict:
				# print "-------------"
				# print type(vc.groupname.decode("gbk"))
				# print vc.groupname.decode("gbk")
				# print type(vc.DeptName)
				# print vc.DeptName
				pass
			# 新支行，需要在json中添加支行nodes
			else:
				pass

				groupNameDict[vc.groupname+vc.deptname] = 1
				if "nodes" not in deptRootDict[vc.deptname]:
					deptRootDict[vc.deptname]["nodes"] = []
				tmpGroupDict = {}
				tmpGroupDict["text"] = vc.groupname
				deptRootDict[vc.deptname]["nodes"].append(tmpGroupDict)
			# 老主机
			if vc.ename+vc.groupname+vc.deptname in enameDict:
				# item当前支行，是个dict
				for item in deptRootDict[vc.deptname]["nodes"]:
					if "text" in item and item["text"] != vc.groupname:
						continue
					# item["nodes"] 主机
					# 遍历支行下面的所有主机
					for item1 in item["nodes"]:
						if "text" in item1 and item1["text"] != vc.ename:
							continue
						item1["nodes"].append({"text":vc.channelname,"tags":[vc.channelid]})
					# item["nodes"].append({"text":vc.channelname,"tags":[vc.ChannelID]})
			# 新主机，需要在网点的nodes列表中添加主机
			else:
				# print vc.ename," ",vc.groupname," ",vc.DeptName
				enameDict[vc.ename+vc.groupname+vc.deptname] = 1
				if "nodes" not in deptRootDict[vc.deptname]:
					pass
					# deptRootDict[vc.DeptName]["nodes"] = []
				# item当前支行，是个dict
				for item in deptRootDict[vc.deptname]["nodes"]:
					if "text" in item and item["text"] != vc.groupname:
						continue
					# 如果主机在支行dict中
					if vc.ename in item.values():
						pass
						# item["nodes"].append({"text":vc.channelname,"tags":[vc.ChannelID]})
					# 该主机不在支行dict中，则需要添加
					else:
						tmpEDict = {}
						tmpEDict["text"] = vc.ename
						tmpEDict["nodes"] = []
						tmpEDict["nodes"].append({"text":vc.channelname,"tags":[vc.channelid]})
						if "nodes" not in item:
							item["nodes"] = []
						item["nodes"].append(tmpEDict)



		keys = deptRootDict.keys()
		keys.sort()
		for key in keys:
			mylist.append(deptRootDict[key])
		# for item in mylist:
		# 	print item
		json_reply = json.dumps(mylist,encoding="utf8")
		return json_reply


@login_required
@csrf_exempt
def configLocalAjax(request):
	if request.is_ajax():
		ajaxuserid = request.POST.get("curUser")
		sip=request.POST.get("sip")
		if ajaxuserid:
			# userInstance = get_object_or_404(Users,pk=int(ajaxuserid))
			videoChannels = XtWatvediochannelinfo.objects.filter(userid=ajaxuserid)
			if sip:
				print sip
				videoChannels = videoChannels.filter(sipid__contains=sip)
			videoChannels = reversed(videoChannels)
			# print videoChannels,videoChannels.count()
			mylist = []

			# 存放每个支行数据的结构 {"XX支行":1,"..."}
			deptNameDict = {}
			# {"XX支行 XX网点":1,}
			groupNameDict = {}
			enameDict = {}
			# 存放真正数据的结构{"text":"XX支行","nodes":[...]}
			deptRootDict = {}			
			for vc in videoChannels:
				# print '--',row.DeptName,row.GroupName,row.EName,row.ChannelName,row.ChannelID
				# 部门已经存在
				if vc.deptname in deptNameDict:
					pass
				# 新部门，需要在json中添加部门	
				else:
					deptNameDict[vc.deptname] = 1
					deptRootDict[vc.deptname] = {}
					deptRootDict[vc.deptname]["text"] = vc.deptname

				# 支行已存在
				# print "-------------))"
				if vc.groupname+vc.deptname in groupNameDict:
					# print "-------------"
					# print type(vc.groupname.decode("gbk"))
					# print vc.groupname.decode("gbk")
					# print type(vc.DeptName)
					# print vc.DeptName
					pass
				# 新支行，需要在json中添加支行nodes
				else:
					pass

					groupNameDict[vc.groupname+vc.deptname] = 1
					if "nodes" not in deptRootDict[vc.deptname]:
						deptRootDict[vc.deptname]["nodes"] = []
					tmpGroupDict = {}
					tmpGroupDict["text"] = vc.groupname
					deptRootDict[vc.deptname]["nodes"].append(tmpGroupDict)
				# 老主机
				if vc.ename+vc.groupname+vc.deptname in enameDict:
					# item当前支行，是个dict
					for item in deptRootDict[vc.deptname]["nodes"]:
						if "text" in item and item["text"] != vc.groupname:
							continue
						# item["nodes"] 主机
						# 遍历支行下面的所有主机
						for item1 in item["nodes"]:
							if "text" in item1 and item1["text"] != vc.ename:
								continue
							item1["nodes"].append({"text":vc.channelname,"tags":[vc.channelid]})
						# item["nodes"].append({"text":vc.channelname,"tags":[vc.ChannelID]})
				# 新主机，需要在网点的nodes列表中添加主机
				else:
					# print vc.ename," ",vc.groupname," ",vc.DeptName
					enameDict[vc.ename+vc.groupname+vc.deptname] = 1
					if "nodes" not in deptRootDict[vc.deptname]:
						pass
						# deptRootDict[vc.DeptName]["nodes"] = []
					# item当前支行，是个dict
					for item in deptRootDict[vc.deptname]["nodes"]:
						if "text" in item and item["text"] != vc.groupname:
							continue
						# 如果主机在支行dict中
						if vc.ename in item.values():
							pass
							# item["nodes"].append({"text":vc.channelname,"tags":[vc.ChannelID]})
						# 该主机不在支行dict中，则需要添加
						else:
							tmpEDict = {}
							tmpEDict["text"] = vc.ename
							tmpEDict["nodes"] = []
							tmpEDict["nodes"].append({"text":vc.channelname,"tags":[vc.channelid]})
							if "nodes" not in item:
								item["nodes"] = []
							item["nodes"].append(tmpEDict)



			keys = deptRootDict.keys()
			keys.sort()
			for key in keys:
				mylist.append(deptRootDict[key])
			# for item in mylist:
			# 	print item
			json_reply = json.dumps(mylist,encoding="gbk")
		return HttpResponse(json_reply)

@login_required
@csrf_exempt
def configJQAjaxDelete(request):
	if request.is_ajax():
		postData = request.POST.getlist("newList[]")
		curUserId = request.POST.get("curUser")
		# print postData,curUserId
		if len(postData) is 0:
			return HttpResponse("no data !")
		for cid in postData:
			XtWatvediochannelinfo.objects.filter(channelid=int(cid),userid=curUserId).delete()
		json_reply = getLocalFromModel(curUserId)
		ActionlogInstance = Actionlog(userid=119,logevent=u"删除通道数据",loglevel="0")
		ActionlogInstance.save()		
		if json_reply!= "error":
			return HttpResponse(json_reply)
		else:
			return HttpResponse(json_reply)		

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def accountsView(request):
	accounts = Users.objects.all()
	for item in accounts:
		print item.username
	return render(request,'system/accounts.html',{'accounts':accounts})


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def deleteAccountView(request,acpk):
	print "delete"
	pass
	try:
		instance = get_object_or_404(Users,pk=int(acpk))
		
		# 删除Video表中用户为这个的所有内容
		videoChannelsRelateWithUser = XtWatvediochannelinfo.objects.filter(userid=int(acpk))
		videoChannelsRelateWithUser.delete()
		# 删除终端表中和用户相关的所有内容
		ClientterminalRelateWithUser = Clientterminal.objects.filter(userid=int(acpk))
		ClientterminalRelateWithUser.delete()
		instance.delete()
		ActionlogInstance = Actionlog(userid=119,logevent=u"删除账户："+acpk,loglevel="0")
		ActionlogInstance.save()		
	except Exception, e:
		print e
		return HttpResponseRedirect("/system/accounts/")
	return HttpResponseRedirect("/system/accounts/")


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def editAccountView(request,acpk):
	if request.POST:
		print "post add user"
		instance = get_object_or_404(Users,pk=int(acpk))
		userForm = addUserModelForm(request.POST,instance=instance)
		if userForm.is_valid():
			print "form is valid"
			instance = userForm.save(commit=True)
			print instance.userid
			ActionlogInstance = Actionlog(userid=119,logevent=u"编辑账户："+instance.username,loglevel="0")
			ActionlogInstance.save()				
			return HttpResponseRedirect("/system/accounts/")
		else:
			return render(request,'system/addAccount.html',{'userForm':userForm,'fun':u"编辑"})
	try:
		instance = get_object_or_404(Users,pk=int(acpk))
		userForm = addUserModelForm(instance = instance)
		return render(request,'system/addAccount.html',{'userForm':userForm,'fun':u"编辑"})	
	except Exception, e:
		print e	


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def addAccountView(request):
	if request.POST:
		print "post add user"
		userForm = addUserModelForm(request.POST)
		if userForm.is_valid():
			print "form is valid"
			instance = userForm.save(commit=True)
			ActionlogInstance = Actionlog(userid=119,logevent=u"添加账户："+instance.username,loglevel="0")
			ActionlogInstance.save()
			return HttpResponseRedirect("/system/accounts/")
		else:
			return render(request,'system/addAccount.html',{'userForm':userForm,'fun':u"添加"})
	userForm = addUserModelForm()
	return render(request,'system/addAccount.html',{'userForm':userForm,'fun':u"添加"})



@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def serversView(request):
	accounts = Server.objects.all()
	for item in accounts:
		print item.serverid
	return render(request,'system/servers.html',{'accounts':accounts})


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def deleteServerView(request,acpk):
	print "delete"
	pass
	try:
		instance = get_object_or_404(Server,pk=int(acpk))
		
		ActionlogInstance = Actionlog(userid=119,logevent=u"删除服务器："+instance.servername,loglevel="0")
		ActionlogInstance.save()
		instance.delete()		
	except Exception, e:
		print e
		return HttpResponseRedirect("/system/servers/")
	return HttpResponseRedirect("/system/servers/")


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def editServerView(request,acpk):
	if request.POST:
		print "post add user"
		instance = get_object_or_404(Server,pk=int(acpk))
		userForm = serverForm(request.POST,instance=instance)
		if userForm.is_valid():
			print "form is valid"
			instance = userForm.save(commit=True)
			ActionlogInstance = Actionlog(userid=119,logevent=u"编辑服务器："+instance.servername,loglevel="0")
			ActionlogInstance.save()
			return HttpResponseRedirect("/system/servers/")
		else:
			return render(request,'system/addServer.html',{'userForm':userForm,'fun':u"编辑"})
	try:
		instance = get_object_or_404(Server,pk=int(acpk))
		userForm = serverForm(instance = instance)
		print userForm
		return render(request,'system/addServer.html',{'userForm':userForm,'fun':u"编辑"})	
	except Exception, e:
		print e	
		return HttpResponseRedirect("/system/servers/")

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def addServerView(request):
	if request.POST:
		print "post add server"
		userForm = serverForm(request.POST)
		if userForm.is_valid():
			print "form is valid"
			instance = userForm.save(commit=True)
			ActionlogInstance = Actionlog(userid=119,logevent=u"添加服务器"+instance.servername,loglevel="0")
			ActionlogInstance.save()			
			return HttpResponseRedirect("/system/servers/")
		else:
			return render(request,'system/addServer.html',{'userForm':userForm,'fun':u"添加"})
	userForm = serverForm()
	return render(request,'system/addServer.html',{'userForm':userForm,'fun':u"添加"})





@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def terminalsView(request):

	terminals = Clientterminal.objects.all()
	return render(request,'system/terminals.html',{'terminals':terminals})

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def addTerminalView(request):
	if request.POST:
		print "post add user"
		userForm = addTerminalModelForm(request.POST)
		if userForm.is_valid():
			print "form is valid"
			instance = userForm.save(commit=True)
			ActionlogInstance = Actionlog(userid=119,logevent=u"添加终端"+instance.registerid,loglevel="0")
			ActionlogInstance.save()	
			return HttpResponseRedirect("/system/terminals/")
		else:
			return render(request,'system/addTerminal.html',{'userForm':userForm})
	userForm = addTerminalModelForm()
	return render(request,'system/addTerminal.html',{'userForm':userForm})

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def editTerminalView(request,tmlpk):
	if request.POST:
		print "post add user"
		instance = get_object_or_404(Clientterminal,pk=int(tmlpk))
		userForm = addTerminalModelForm(request.POST,instance=instance)
		if userForm.is_valid():
			print "form is valid"
			ActionlogInstance = Actionlog(userid=119,logevent=u"编辑终端"+instance.registerid,loglevel="0")
			ActionlogInstance.save()				
			instance = userForm.save(commit=True)
			print instance.userid
			return HttpResponseRedirect("/system/terminals/")
		else:
			return render(request,'system/addTerminal.html',{'userForm':userForm})
	try:
		instance = get_object_or_404(Clientterminal,pk=int(tmlpk))
		userForm = addTerminalModelForm(instance = instance)
		return render(request,'system/addTerminal.html',{'userForm':userForm})	
	except Exception, e:
		print e	

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def deleteTerminalView(request,tmlpk):
	print "delete tml"
	pass
	try:
		instance = get_object_or_404(Clientterminal,pk=int(tmlpk))
		ActionlogInstance = Actionlog(userid=119,logevent=u"删除终端"+instance.registerid,loglevel="0")
		ActionlogInstance.save()			
		instance.delete()
	except Exception, e:
		print e
		return HttpResponseRedirect("/system/terminals/")
	return HttpResponseRedirect("/system/terminals/")


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def addressMappingView(request):
	mapping = AddressMapping.objects.all()
	return render(request,'system/addressMapping.html',{'mapping':mapping})	


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def addMappingView(request):
	if request.POST:
		print "post add user"
		userForm = addressMappingModelForm(request.POST)
		if userForm.is_valid():
			print "form is valid"
			instance = userForm.save(commit=True)
			ActionlogInstance = Actionlog(userid=119,logevent=u"添加映射outerip："+instance.outerip,loglevel="0")
			ActionlogInstance.save()				
			
			return HttpResponseRedirect("/system/addressMapping/")
		else:
			# print userForm
			return render(request,'system/addMapping.html',{'userForm':userForm})
	userForm = addressMappingModelForm()
	return render(request,'system/addMapping.html',{'userForm':userForm})


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def editAddressMappingView(request,ampk):
	if request.POST:
		print "post edit mapping"
		instance = get_object_or_404(AddressMapping,pk=int(ampk))
		userForm = addressMappingModelForm(request.POST,instance=instance)
		if userForm.is_valid():
			print "form is valid"
			ActionlogInstance = Actionlog(userid=119,logevent=u"修改映射outerip："+instance.outerip,loglevel="0")
			ActionlogInstance.save()			
			instance = userForm.save(commit=True)
			return HttpResponseRedirect("/system/addressMapping/")
		else:
			return render(request,'system/addMapping.html',{'userForm':userForm})
	try:
		instance = get_object_or_404(AddressMapping,pk=int(ampk))
		userForm = addressMappingModelForm(instance = instance)
		return render(request,'system/addMapping.html',{'userForm':userForm})	
	except Exception, e:
		print e	


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def deleteAddressMappingView(request,ampk):
	print "delete am"
	pass
	try:
		instance = get_object_or_404(AddressMapping,pk=int(ampk))
		ActionlogInstance = Actionlog(userid=119,logevent=u"删除映射outerip："+instance.outerip,loglevel="0")
		ActionlogInstance.save()		
		instance.delete()
	except Exception, e:
		print e
		return HttpResponseRedirect("/system/addressMapping/")
	return HttpResponseRedirect("/system/addressMapping/")


@login_required
@csrf_exempt
def syncDBAjax(request):
	if request.is_ajax():
		print "sync db"
		try:
			sqlServer = IcbcDb.objects.get(pk=1)
			ip = sqlServer.dbip
			un = sqlServer.username
			password = sqlServer.password
			command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
			cn=pyodbc.connect(command)
			cn.timeout=1
			cursor=cn.cursor()
			rawsqlcmd = "select * from(\
				select distinct s.ID as TerminalID, s.DomainName as DeviceName,s.ServerIP as DeviceIP,s.TCPPort,\
				c.DeviceType,c.StreamTransMode,s.RasUser,s.RasPassword,gd.GroupID,c.ID as ChannelID,c.DeviceChannelIndex,\
				s2.ServerIP as StreamServerIP,s2.TCPPort as StreamTCPPort,s2.ServerPort as NLCServerPort,s2.ClientPort as NLCClientPort,\
				'SHUser' as StreamUserName,'XKDARXDAVLVMNCHX' as StreamUserPWS,g1.Name as DeptName,\
				g1.GroupName,e4.DvrName as EName,e4.ChName as ChannelName,e4.PosName,c.UseMediaServer from \
				[iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c left outer join [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e \
				on c.ID=e.ID left outer join [iSOSDB_30].[iSOS_Admin30].[VideoEqServer] s \
				 on e.ParentID=s.ID left outer join [iSOSDB_30].[iSOS_Admin30].[iSOSGroupDevice] gd \
				 on c.ID=gd.DeviceID left outer join \
				(select g.ID,g.GroupName,d.Name from [iSOSDB_30].[iSOS_Admin30].[iSOSLogicGroup] g,\
				 [iSOSDB_30].[iSOS_Admin30].[iSosDepartment] d where \
				 g.DepartmentID=d.DepartmentID) g1 on gd.GroupID=g1.ID left outer join \
				 (select e1.ID,e1.EName ChName,e2.EName DvrName, e1.PosName\
				from (select tmp1.*,tmp2.DictText as PosName from [iSOSDB_30].[iSOS_Admin30].[iSosEquipment] tmp1,\
				iSOSDB_30.iSOS_Admin30.iSosDictionary20009 tmp2 where tmp1.Position=tmp2.DictValue) e1,\
				[iSOSDB_30].[iSOS_Admin30].[iSosEquipment] e2 where e1.ParentID=e2.ID) e4 on c.ID=e4.ID left outer join \
				(select c2.ID,(case c2.code when 0 then '' else s1.ServerIP end) as ServerIP,\
				(case c2.code when 0 then '0' else s1.TCPPort end) as TCPPort,(case c2.code when 0 then '0' else s1.ServerPort end) \
				as ServerPort,(case c2.code when 0 then '0' else s1.ClientPort end) as ClientPort \
				from (select c1.ID,c1.StreamTransMode,(case c1.StreamTransMode when 0 then c1.MediaServerID when 1 then c1.MediaServerID2 end) as code\
				from [iSOSDB_30].[iSOS_Admin30].[VideoEqChannel] c1) c2 left join [iSOSDB_30] \
				.[iSOS_Admin30].[VideoEqMediaServer] s1\
				on c2.code=s1.ID) s2 on c.ID=s2.ID) tb"
			localObjects = XtWatvediochannelinfo.objects.all()
			for item in localObjects:
				cursor.execute(rawsqlcmd + " where tb.ChannelId=%s" % item.channelid)
				data = cursor.fetchall()
				if len(data) is 1:
					row = data[0]
					if type(row.GroupName) is not unicode:
						gn = row.GroupName.decode("gbk")
					else:
						gn = row.GroupName
					if type(row.DeptName) is not unicode:
						dn = row.DeptName.decode("gbk")
					else:
						dn = row.DeptName

					if type(row.EName) is not unicode:
						en = row.EName.decode("gbk")
					else:
						en = row.EName
					if type(row.ChannelName) is not unicode:
						cn = row.ChannelName.decode("gbk")
					else:
						cn = row.ChannelName

					# 更新表
					row = data[0]
					item.deviceip=row.DeviceIP
					item.tcpport=row.TCPPort
					item.devicetype=row.DeviceType
					item.streamtransmode=row.StreamTransMode
					item.rasuser=row.RasUser
					item.raspassword=row.RasPassword
					item.groupid=row.GroupID
					item.channelid=row.ChannelID
					item.devicechannelindex=row.DeviceChannelIndex
					item.streamserverip=row.StreamServerIP
					item.streamtcpport=row.StreamTCPPort
					item.nlcserverport=row.NLCServerPort
					item.nlcclientport=row.NLCClientPort
					item.streamusername=row.StreamUserName
					item.streamuserpws=row.StreamUserPWS
					item.deptname=dn
					item.groupname=gn
					item.ename=en
					item.channelname=cn
					item.terminalid=row.TerminalID
					item.save()
				elif len(data) is 0:
					# 删除表
					item.delete()
			cursor.connection.close()
		except Exception, e:
			print "odbc error:",e
			return HttpResponse(e)		
		ActionlogInstance = Actionlog(userid=119,logevent=u"手动同步数据库",loglevel="0")
		ActionlogInstance.save()
		return HttpResponse(u"同步成功")	


@login_required
@csrf_exempt
@user_passes_test(if_not_zby,login_url="/home/" )
def sipInfoView(request):
	if sipInfo.objects.count()<1:
		sipInfoInstance = sipInfo(centerCode="00000000",industryCode="00",typeCode="000")
		sipInfoInstance.save()
	if request.POST:
		form = sipInfoForm(request.POST)
		if form.is_valid():
			print("sipInfo is valid")
			sipInfoInstance = sipInfo.objects.all().first()
			ActionlogInstance = Actionlog(userid=119,logevent=u"修改sip信息",loglevel="0")
			ActionlogInstance.save()			
			
			sipInfoInstance.centerCode = form.cleaned_data['centerCode']
			sipInfoInstance.industryCode = form.cleaned_data['industryCode']
			sipInfoInstance.typeCode = form.cleaned_data['typeCode']
			sipInfoInstance.save()
			return HttpResponseRedirect("/system/sipInfo/")			
		else:
			print("sipInfo is not valid")
			return render(request,'system/sipinfo.html',{'form':form})	
	else:
		sipInstance = sipInfo.objects.all().first()
		form = sipInfoForm(instance=sipInstance)
		return render(request,'system/sipinfo.html',{'form':form})		


@login_required
@csrf_exempt
def userLogView(request):
	print Actionlog.objects.count()
	print request.user.pk
	ulList = Actionlog.objects.order_by('-pk')[0:100]
	return render(request,'system/userLog.html',{'ulList':ulList})

# import csv
# @csrf_exempt
# def downloadUserLogView(request):
# 	pass

import csv
@login_required
@csrf_exempt
def downloadUserLogView(request):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="userLog_%s.csv"' % str(datetime.date.today())
	writer = csv.writer(response)
	writer.writerow([u'操作者'.encode('gb2312'),u'日期'.encode('gb2312'),u'动作'.encode('gb2312')])
	for log in Actionlog.objects.order_by('-pk'):
		writer.writerow(["Admin".encode('gb2312'),str(log.operatetime).encode('gb2312'),log.logevent.encode('gb2312')])
	return response

@login_required
@csrf_exempt
@user_passes_test(if_not_zby,login_url="/home/" )
def clearUserLogView(request):
	Actionlog.objects.all().delete()
	ActionlogInstance = Actionlog(userid=119,logevent=u"清空日志",loglevel="0")
	ActionlogInstance.save()
	ulList = Actionlog.objects.order_by('-pk')[0:100]
	return render(request,'system/userLog.html',{'ulList':ulList})		


@login_required
@csrf_exempt
def policeLogView(request):
	if request.is_ajax():
		if request.POST:
			keyDict = {}
			keyDict['searchtype'] = "" if request.POST.get('type') is None else request.POST.get('type')
			keyDict['callstart'] = "" if request.POST.get('callstart') is None else request.POST.get('callstart')
			keyDict['callend'] = "" if request.POST.get('callend') is None else request.POST.get('callend')
			keyDict['videostart'] = "" if request.POST.get('videostart') is None else request.POST.get('videostart')
			keyDict['videoend'] = "" if request.POST.get('videoend') is None else request.POST.get('videoend')

			keyDict['dept'] = "" if request.POST.get('dept') is None else request.POST.get('dept')
			keyDict['group'] = "" if request.POST.get('group') is None else request.POST.get('group')
			keyDict['device'] = "" if request.POST.get('device') is None else request.POST.get('device')
			keyDict['channel'] = "" if request.POST.get('channel') is None else request.POST.get('channel')
			# searchtype = request.POST.get('type')
			# callstart = request.POST.get('callstart')
			# callend = request.POST.get('callend')
			# videostart = request.POST.get('videostart')
			# videoend = request.POST.get('videoend')
			print "keyDict is :",keyDict
			logList = ploicelog.objects.all()

			for key in keyDict.keys():
				if keyDict[key] == "":
					continue;
				if key == "searchtype":
					logList = logList.filter(operatetype=int(keyDict[key]))
					continue
				if key == "callstart" and keyDict[key]!="":
					logList = logList.filter(calltime__gte=keyDict[key])
					continue
				if key == "callend" and keyDict[key]!="":
					logList = logList.filter(calltime__lte=keyDict[key])
					continue
				if key == "videostart" and keyDict[key]!="":
					logList = logList.filter(videotime__gte=keyDict[key])
					continue
				if key == "videoend" and keyDict[key]!="":
					logList = logList.filter(videotime__gte=keyDict[key])
					continue

				if key == "dept" and keyDict[key]!="":
					logList = logList.filter(deptname=keyDict[key])
					continue
				if key == "group" and keyDict[key]!="":
					logList = logList.filter(groupname=keyDict[key])
					continue
				if key == "device" and keyDict[key]!="":
					logList = logList.filter(ename=keyDict[key])
					continue
				if key == "channel" and keyDict[key]!="":
					logList = logList.filter(channelname=keyDict[key])
					continue

			ulList = logList.order_by('-pk')

			paginator = Paginator(ulList, 25)
			cache.set(request.user.username+'-paginator',paginator)

			page = request.GET.get('page')

			try:
				logs = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				logs = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				logs = paginator.page(paginator.num_pages)

			return render(request,'system/policeLog.html',{'logs':logs})



		if request.GET:

			print ploicelog.objects.count()
			print request.user.pk
			page = request.GET.get('page')
			paginator = cache.get(request.user.username+'-paginator',Paginator(ploicelog.objects.all().order_by('-pk'), 25))
			try:
				logs = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				logs = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				logs = paginator.page(paginator.num_pages)
			return render(request,'system/policeLog.html',{'logs':logs})
	ulList = ploicelog.objects.all().order_by('-pk')
	paginator = Paginator(ulList, 25)
	cache.set(request.user.username+'-paginator',paginator)
	page = request.GET.get('page')
	try:
		logs = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		logs = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		logs = paginator.page(paginator.num_pages)
	return render(request,'system/policeLog.html',{})

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def clearPoliceLogView(request):
	ploicelog.objects.all().delete()
	ActionlogInstance = Actionlog(userid=119,logevent=u"清空公安日志",loglevel="0")
	ActionlogInstance.save()
	return HttpResponseRedirect("/system/policeLog/")

@login_required
@csrf_exempt
def downloadPoliceLogView(request):
	if request.POST:
		keyDict = {}
		keyDict['searchtype'] = "" if request.POST.get('searchtype') is None else request.POST.get('searchtype')
		keyDict['callstart'] = "" if request.POST.get('callstart') is None else request.POST.get('callstart')
		keyDict['callend'] = "" if request.POST.get('callend') is None else request.POST.get('callend')
		keyDict['videostart'] = "" if request.POST.get('videostart') is None else request.POST.get('videostart')
		keyDict['videoend'] = "" if request.POST.get('videoend') is None else request.POST.get('videoend')

		keyDict['dept'] = "" if request.POST.get('searchdept') is None else request.POST.get('searchdept')
		keyDict['group'] = "" if request.POST.get('searchgroup') is None else request.POST.get('searchgroup')
		keyDict['device'] = "" if request.POST.get('searchdevice') is None else request.POST.get('searchdevice')
		keyDict['channel'] = "" if request.POST.get('searchchannel') is None else request.POST.get('searchchannel')
		logList = ploicelog.objects.all()
		for key in keyDict.keys():
			if keyDict[key] == "":
				continue;
			if key == "searchtype":
				logList = logList.filter(operatetype=int(keyDict[key]))
				continue
			if key == "callstart" and keyDict[key]!="":
				logList = logList.filter(calltime__gte=keyDict[key])
				continue
			if key == "callend" and keyDict[key]!="":
				logList = logList.filter(calltime__lte=keyDict[key])
				continue
			if key == "videostart" and keyDict[key]!="":
				logList = logList.filter(videotime__gte=keyDict[key])
				continue
			if key == "videoend" and keyDict[key]!="":
				logList = logList.filter(videotime__gte=keyDict[key])
				continue

			if key == "dept" and keyDict[key]!="":
				logList = logList.filter(deptname=keyDict[key])
				continue
			if key == "group" and keyDict[key]!="":
				logList = logList.filter(groupname=keyDict[key])
				continue
			if key == "device" and keyDict[key]!="":
				logList = logList.filter(ename=keyDict[key])
				continue
			if key == "channel" and keyDict[key]!="":
				logList = logList.filter(channelname=keyDict[key])
				continue


		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename="policeLogs_%s.csv"' % str(datetime.date.today())
		writer = csv.writer(response)
		writer.writerow([u'调阅类型'.encode('gb2312'),u'调阅时间'.encode('gb2312'),u'视频时间'.encode('gb2312'),u'部位'.encode('gb2312'),u'动作'.encode('gb2312')])
		for log in logList.order_by('-pk'):
			writer.writerow([str(log.operatetype),str(log.calltime),str(log.videotime),("%s-%s-%s-%s" % (log.deptname,log.groupname,log.ename,log.channelname)).encode('gbk'),log.logevent.encode('gbk')])
		return response


def getICBCTreeFromLogs():
	logs = ploicelog.objects.all().order_by('-pk')
	deptNameDict = {}
	for log in logs:
		if log.deptname not in deptNameDict:
			deptNameDict[log.deptname] = {}
		if log.groupname not in deptNameDict[log.deptname]:
			deptNameDict[log.deptname][log.groupname] = {}
		if log.ename not in deptNameDict[log.deptname][log.groupname]:
			deptNameDict[log.deptname][log.groupname][log.ename] = {}
		if log.channelname not in deptNameDict[log.deptname][log.groupname][log.ename]:
			deptNameDict[log.deptname][log.groupname][log.ename][log.channelname] = log.channelname


	return deptNameDict


@login_required
def getICBCTreeFromLogsAjaxView(request):
	if request.is_ajax():
		tree = getICBCTreeFromLogs()
		tree = json.dumps(tree,encoding="gbk")
		return HttpResponse(tree)


@login_required
@csrf_exempt
@user_passes_test(if_not_zby,login_url="/home/" )
def shutdownView(request):
	os.system("shutdown -s -t 5")
	return HttpResponseRedirect("/home/")	


@login_required
@csrf_exempt
@user_passes_test(if_not_zby,login_url="/home/" )
def restartView(request):
	os.system("shutdown -r -t 5")
	return HttpResponseRedirect("/home/")	

from socket import *
@login_required
@csrf_exempt
def notifyUserAjax(request):
	if request.is_ajax():
		curUserId = request.POST.get("curUser")
		if not Users.objects.filter(pk=curUserId).exists():
			return HttpResponse(u"error:该用户不存在")
		userName = Users.objects.get(pk=curUserId).username

		PORT = 7000
		HOST="localhost"
		ADDR=(HOST,PORT)
		msg = "REFRESH:"+userName
		print msg
		try:
			tcpCliSock = socket(AF_INET,SOCK_STREAM)
			tcpCliSock.connect(ADDR)

			tcpCliSock.send(msg)
			tcpCliSock.close()
		except Exception as e:
			print "send main C++ error",e
			return HttpResponse(u"error:网络错误")

		return HttpResponse(u"通知用户成功")

import zipfile

def handle_upload_file(f):
	updateDir="../"
	if f.name != "update.zip":
		return u"请输入update.zip升级包"
	else:
		if zipfile.is_zipfile(f):
			try:
				os.system('taskkill /f /im "VideoTransServerMonitor.exe"')	
				os.system('taskkill /f /im "SDTVideoSwitchMonitor.exe"')					
				os.system('taskkill /f /im "VideoTransServer.exe"')	
				os.system('taskkill /f /im "SDTVideoSwitch.exe"')	

				zp = zipfile.ZipFile(f,'r')
				zp.extractall(updateDir)

				zp.close()
				os.system("shutdown -r -t 5")
				return True
			except BaseException as e:
				print e
				os.system("shutdown -r -t 5")
				return e
		else:
			return u"请输入update.zip升级包"
	return True


@login_required
@csrf_exempt
@user_passes_test(if_not_zby,login_url="/home/" )
def updateView(request):
	if request.POST:
		print request.FILES
		form = uploadFileForm(request.POST,request.FILES)
		if form.is_valid():
			print("file form is valid")
			handleFileResult = handle_upload_file(request.FILES['file'])
			if handleFileResult != True:
				form = uploadFileForm()
				return render(request,'system/update.html',{'form':form,'msg':"error",'msgContent':handleFileResult})
			form = uploadFileForm()
			return render(request,'system/update.html',{'form':form,'msg':'success','msgContent':u"上传成功"})
		else:
			print form
			return render(request,'system/update.html',{'form':form})
	else:
		form = uploadFileForm()
		return render(request,'system/update.html',{'form':form})

keysDict={"FCIF":"4CIF","P720":"720P","P1080":"1080P","QCIF_BR":"QCIF","CIF_BR":"CIF","FCIF_BR":"4CIF","D1_BR":"D1","WD1_BR":"WD1","P720_BR":"720P","P1080_BR":"1080P"}
WebServerInfoList = ["port","heartbeatPort"]
ServerCapabilityInfoList = ["max_capability"]
CapabilityUseList = ["QCIF","CIF","4CIF","D1","WD1","720P","1080P"]
VideoEncodeParamList = ["DefaultFrameRate","MaxKeyFramePeriod","PayloadType","isShowFrameRate"]


import ConfigParser
@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def configparamsettingView(request):
	if request.POST:
		print "post"
		form = configparamsForm(request.POST)
		if form.is_valid():
			cf = ConfigParser.ConfigParser()
			cf.optionxform = str
			cf.read("../VideoTransServer/ConfigInfo/ConfigInfo.ini")
			print "configform is valid!"
			print form.cleaned_data
			print type(form.cleaned_data)
			srcDict = form.cleaned_data
			for key in form.cleaned_data.keys():
				if '_BR' not in key:
					if key in keysDict.keys():
						tmpkey = keysDict[key]
					else:
						tmpkey = key
					print tmpkey
					if tmpkey in WebServerInfoList:
						cf.set("WebServerInfo",tmpkey,srcDict[key])
					if tmpkey in ServerCapabilityInfoList:
						cf.set("ServerCapabilityInfo",tmpkey,srcDict[key])
					if tmpkey in CapabilityUseList:
						cf.set("CapabilityUse",tmpkey,srcDict[key])
					if tmpkey in VideoEncodeParamList:
						cf.set("VideoEncodeParam",tmpkey,srcDict[key])							
				else:
					cf.set("H264BitRate",keysDict[key],srcDict[key])
			cf.write(open("../VideoTransServer/ConfigInfo/ConfigInfo.ini","w"))
			return render(request,'system/configparams.html',{'form':form,"msg":"success","msgContent":"修改成功","info":u"媒体程序参数","url":"system/configparams/"})	
		else:
			return render(request,'system/configparams.html',{'form':form,"msg":"error","msgContent":"请检查输入","info":u"媒体程序参数","url":"system/configparams/"})	


	cf = ConfigParser.ConfigParser()
	# if no setting, all letter will be maked lower case
	cf.optionxform = str

	try:
		cf.read("../VideoTransServer/ConfigInfo/ConfigInfo.ini")

		# print cf.sections()
		srcDict = {}
		for section in cf.sections():
			if section == "H264BitRate":
				for item in cf.items(section):
					# print item
					if len(item)!=2:
						continue
					if item[0] == '4CIF':
						srcDict['FCIF_BR'] = item[1]
					elif item[0] == '720P':
						srcDict['P720_BR'] = item[1]
					elif item[0] == '1080P':
						srcDict['P1080_BR'] = item[1]
					else:
						srcDict[item[0]+'_BR'] = item[1]
			else:
				for item in cf.items(section):
					# print item
					if len(item)!=2:
						continue
					if item[0] == '4CIF':
						srcDict['FCIF'] = item[1]
					elif item[0] == '720P':
						srcDict['P720'] = item[1]
					elif item[0] == '1080P':
						srcDict['P1080'] = item[1]
					else:
						srcDict[item[0]] = item[1]
		# print srcDict
		form = configparamsForm(initial = srcDict)

	except BaseException as e:
		print e
		return render(request,'system/configparams.html')
	return render(request,'system/configparams.html',{'form':form,"info":u"媒体程序参数","url":"system/configparams/"})


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def configMediaMonitorParamsView(request):
	keysDict_db={"ip":"ip","port":"port","dbname":"dbname","username":"username","password":"password"}
	keysDict_vts = {"apppath":"AppPath","interval":"Interval","vts_ip":"ip","vts_port":"port","vts_heartbeatPort":"heartbeatPort"}
	if request.POST:
		form = mediaMonitorParamsForm(request.POST)
		if form.is_valid():
			cf = ConfigParser.ConfigParser()
			# if no setting, all letter will be maked lower case
			cf.optionxform = str
			cf.read(u"../VideoTransServerMonitor/ConfigInfo/ConfigInfo.ini")
			srcDict = form.cleaned_data
			print srcDict
			for key in form.cleaned_data.keys():
				if key == "apppath":
					cf.set("VideoTransServerInfo",keysDict_vts[key],srcDict[key])
				elif key == "interval":
					cf.set("VideoTransServerInfo",keysDict_vts[key],srcDict[key])
				elif key == "vts_ip":
					cf.set("VideoTransServerInfo",keysDict_vts[key],srcDict[key])
				elif key == "vts_port":
					cf.set("VideoTransServerInfo",keysDict_vts[key],srcDict[key])
				elif key == "vts_heartbeatPort":
					cf.set("VideoTransServerInfo",keysDict_vts[key],srcDict[key])
				else:
					cf.set("DatabaseInfo",key,srcDict[key])	
			cf.write(open(u"../VideoTransServerMonitor/ConfigInfo/ConfigInfo.ini","w"))
			return render(request,'system/configparams.html',{"msg":"success","msgContent":"修改成功",'form':form,"info":u"媒体监控程序参数","url":"system/configmediamonitorparams/"})			
		else:
			print "form unvalid"
			return render(request,'system/configparams.html',{"msg":"error","msgContent":"请检查输入",'form':form,"info":u"媒体监控程序参数","url":"system/configmediamonitorparams/"})


	else:
		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str
		try:
			cf.read(u"../VideoTransServerMonitor/ConfigInfo/ConfigInfo.ini")
			srcDict = {}
			for section in cf.sections():
				for item in cf.items(section):
					if len(item)!=2:
						continue
					if section == "DatabaseInfo":
						srcDict[item[0]] = item[1]
					elif section == "VideoTransServerInfo":
						if item[0] == "AppPath":
							srcDict['apppath'] = item[1]
						if item[0] == "Interval":
							srcDict['interval'] = item[1]
						if item[0] == "ip":
							srcDict['vts_ip'] = item[1]
						if item[0] == "port":
							srcDict['vts_port'] = item[1]
						if item[0] == "heartbeatPort":
							srcDict['vts_heartbeatPort'] = item[1]							
			form = mediaMonitorParamsForm(initial = srcDict)
			return render(request,'system/configparams.html',{'form':form,"info":u"媒体监控程序参数","url":"system/configmediamonitorparams/"})
		except BaseException as e:
			print e
		return render(request,'system/configparams.html',{'form':form})


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def configGroupParamsView(request):
	if request.POST:
		groupParamsFormset = formset_factory(groupParamsForm,extra=0)
		formset = groupParamsFormset(request.POST)
		if formset.is_valid():
			print "valid!"
			print formset.cleaned_data
			cf = ConfigParser.ConfigParser()
			# if no setting, all letter will be maked lower case
			cf.optionxform = str
			cf.read("../tranServerSite/group.ini")	
			if not cf.has_section("departinfo"):
				cf.add_section("departinfo")	
			for param in formset.cleaned_data:
				cf.set("departinfo",param["title"].encode("gbk"),param["code"].encode("gbk"))

			cf.write(open("../tranServerSite/group.ini","w"))
			return HttpResponseRedirect("/system/configgroupparams/")			

		else:
			print "unvalid!"
			return render(request,'system/groupparams.html',{"formset":formset,"info":u"地市行参数","url":"system/configgroupparams/"})

		
	else:
		sqlServer = IcbcDb.objects.get(pk=1)
		ip = sqlServer.dbip
		un = sqlServer.username
		password = sqlServer.password
		command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
		groupList = []
		try:
			cn=pyodbc.connect(command)
			cn.timeout=1
			cursor=cn.cursor()
			rawsqlcmd = "select * from [iSOSDB_30].[iSOS_Admin30].iSosDepartment where ParentID is not NULL"
			cursor.execute(rawsqlcmd)
			data = cursor.fetchall() 
			for row in data:
				if type(row.Name) is not unicode:
					# print row.Name.decode("gbk")
					groupList.append(row.Name.decode("gbk"))
				else:
					# print row.Name
					groupList.append(row.Name)
			# print groupList
		except Exception, e:
			print "odbc error:",e
		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str
		srcDict = {}
		initialList = []
		try:
			cf.read("../tranServerSite/group.ini")
			
			changed = False
			if not cf.has_section("departinfo"):
				cf.add_section("departinfo")
				changed = True
			for item in cf.items("departinfo"):
				if item[0].decode("gbk") not in groupList:
					cf.remove_option("departinfo",item[0])
					changed = True
			for item in groupList:
				if not cf.has_option("departinfo",item.encode("gbk")):
					cf.set("departinfo",item.encode("gbk"),"")
					changed = True
			for item in cf.items("departinfo"):
				# print "---",item
				tmp = "" if len(item) < 2 else item[1].decode("gbk")
				initialList.append({"title":item[0].decode("gbk"),"code":tmp})
			if changed:
				cf.write(open("../tranServerSite/group.ini","w"))

		except BaseException as e:
			print e
		print (initialList)
		for item in initialList:
			print item
		groupParamsFormset = formset_factory(groupParamsForm,extra=0)
		formset = groupParamsFormset(initial=initialList)

		return render(request,'system/groupparams.html',{"formset":formset,"info":u"地市行参数","url":"system/configgroupparams/"})

# 应该是departname，此处有误
def getGroupParam():
	sqlServer = IcbcDb.objects.get(pk=1)
	ip = sqlServer.dbip
	un = sqlServer.username
	password = sqlServer.password
	command = 'DRIVER={SQL Server};SERVER=%s;DATABASE=ISOSDB_30;UID=%s;PWD=%s' % (ip,un,password)
	groupList = []
	try:
		cn=pyodbc.connect(command)
		cn.timeout=1
		cursor=cn.cursor()
		rawsqlcmd = "select * from [iSOSDB_30].[iSOS_Admin30].iSosDepartment where ParentID is not NULL"
		cursor.execute(rawsqlcmd)
		data = cursor.fetchall()
		for row in data:
			if type(row.Name) is not unicode:
				# print row.Name.decode("gbk")
				groupList.append(row.Name.decode("gbk"))
			else:
				# print row.Name
				groupList.append(row.Name)
		# print groupList
	except Exception, e:
		print "odbc error:",e
	cf = ConfigParser.ConfigParser()
	# if no setting, all letter will be maked lower case
	cf.optionxform = str
	srcDict = {}
	try:
		cf.read("../tranServerSite/group.ini")
		
		changed = False
		if not cf.has_section("departinfo"):
			cf.add_section("departinfo")
			changed = True
		for item in cf.items("departinfo"):
			if item[0].decode("gbk") not in groupList:
				cf.remove_option("departinfo",item[0].decode("gbk"))
				changed = True
		for item in groupList:
			if not cf.has_option("departinfo",item.encode("gbk")):
				cf.set("departinfo",item.encode("gbk"),"")
				changed = True
		for item in cf.items("departinfo"):
			# print "---",item
			tmp = "" if len(item) < 2 else item[1].decode("gbk")
			srcDict[item[0].decode("gbk")] = tmp
		if changed:
			cf.write(open("../tranServerSite/group.ini","w"))
		return srcDict
	except BaseException as e:
		print e
		return None


@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def configServerParamsView(request):
	if request.POST:
		form = serverParamsForm(request.POST)
		if form.is_valid():
			cf = ConfigParser.ConfigParser()
			# if no setting, all letter will be maked lower case
			cf.optionxform = str
			cf.read(u"../SDTVideoSwitch/control.ini")
			srcDict = form.cleaned_data
			print srcDict
			for key in form.cleaned_data.keys():
				if key == "name":
					cf.set("datasource",key,srcDict[key])
				elif key == "UID":
					cf.set("datasource",key,srcDict[key])
				elif key == "PWD":
					cf.set("datasource",key,srcDict[key])
				else:
					cf.set("serverinfo",key,srcDict[key])	
			cf.write(open(u"../SDTVideoSwitch/control.ini","w"))
			return render(request,'system/configparams.html',{"msg":"success","msgContent":"修改成功",'form':form,"info":u"协议程序参数","url":"system/configserverparams/"})		
		else:
			print "form unvalid"
			return render(request,'system/configparams.html',{"msg":"error","msgContent":"请检查输入",'form':form,"info":u"协议程序参数","url":"system/configserverparams/"})


	else:
		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str
		try:
			cf.read(u"../SDTVideoSwitch/control.ini")
			srcDict = {}
			for section in cf.sections():
				for item in cf.items(section):
					if len(item)!=2:
						continue
					if section == "serverinfo" or section == "datasource":
						srcDict[item[0]] = item[1]						
			form = serverParamsForm(initial = srcDict)
			return render(request,'system/configparams.html',{'form':form,"info":u"协议程序参数","url":"system/configserverparams/"})
		except BaseException as e:
			print e
		return render(request,'system/configparams.html',{'form':form})


@login_required
def aboutView(request):
	version = ""
	copyright = ""	
	# return render(request,'system/about.html',{"version":version,"copyright":copyright})
	


	try:
		cf = ConfigParser.ConfigParser()
		# if no setting, all letter will be maked lower case
		cf.optionxform = str

		cf.read(u"version.ini")

		srcDict = {}
		for section in cf.sections():
			for item in cf.items(section):
				if item[0] == "version" and item[1]:
					version = item[1]
				if item[0] == "copyright" and item[1]:
					copyright = item[1].decode("gbk")

		return render(request,'system/about.html',{"version":version,"copyright":copyright})

	except error as e:
		print e
		version = ""
		copyright = ""
		return render(request,'system/about.html',{"version":version,"copyright":copyright})