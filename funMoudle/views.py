#coding:utf-8
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
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,SetPasswordForm,AdminPasswordChangeForm
from django.contrib.auth.models import User as sysUser
from django.contrib.auth.decorators import user_passes_test
import httplib
mediaHost = "localhost"
# mediaHost = "10.25.12.18"

# Create your views here.

# is admin account
def if_not_zby(user):
	print "if_not_zby:",user
	new_group,created = Group.objects.get_or_create(name="zby")
	return new_group not in user.groups.all()


@login_required
@csrf_exempt
def viewVideoView(request):
	remote_ip = request.META['REMOTE_ADDR']
	remote_port = "6000"
	dvrip = request.POST.get("dvrip")
	devicechannelindex = request.POST.get("devicechannelindex")
	result = XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) & Q(devicechannelindex=devicechannelindex))
	if result.count() == 0:
		print "no XtWatvediochannelinfo"
		return HttpResponse("error!")
	try:
		httpClient=httplib.HTTPConnection(mediaHost,8090,timeout=5)
		msgtosend = '/{"msg_type":"close_channel","remote_ip":"%s","remote_port":"%d"}' % (remote_ip,int(remote_port))

		httpClient.request('GET',msgtosend)
		response=httpClient.getresponse()



		httpClient=httplib.HTTPConnection(mediaHost,8090,timeout=5)
		# httpClient.request('GET',r'/{"msg_type":"server_status"}')
		requestmsg = '/{"msg_type":"open_channel","msg_id":"110","nvr_ip":"%s","nvr_port":"%s","user_name":"%s","password":"%s","channel_index":"%s","device_type":"%s","stream_mode":"%s","remote_ip":"%s","remote_port":"%s","stream_server_ip":"%s","stream_server_port":"%s","dept_id":"%s","term_id":"%s","channel_id":"%s","is_from_stream_server":"%s"}' % (result.first().deviceip,result.first().tcpport,\
			result.first().rasuser,result.first().raspassword,result.first().devicechannelindex,result.first().devicetype,result.first().streamtransmode,\
			remote_ip,remote_port,result.first().streamserverip,result.first().streamtcpport,result.first().groupid,result.first().terminalid,result.first().channelid,result.first().usemediaserver)
		print requestmsg
		httpClient.request('GET',requestmsg)
		response=httpClient.getresponse()
		data = response.read()
		print data
		js = json.loads(data)
		return HttpResponse(remote_ip)
	except BaseException as e:
		print u"无法连接媒体服务",e
	except TypeError as e:
		print u"解析失败"
	except Exception as e:
		print u"其他错误"
	return HttpResponse("error!")

@login_required
@csrf_exempt
def viewVideoWithRefreshView(request,remoteip,remoteport):
	pass
	dvrip = remoteip
	devicechannelindex = remoteport
	result = XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) & Q(devicechannelindex=devicechannelindex))
	if result.count() == 0:
		print "no XtWatvediochannelinfo"
		return HttpResponseRedirect("/home/")



	localip = request.META['REMOTE_ADDR']
	print localip
	now = datetime.datetime.now()
	pythoncom.CoInitialize()
	nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)
	if len(nic_configs)<1:
		print u"找不到网卡"
		networkAdapter = networkAdapterForm()
		return render(request,'system/configNET.html',{'networkAdapterForm':networkAdapter,'msg':'fail','msgContent':u'找不到网卡'})
	interface = nic_configs[0]
	localIP = interface.IPAddress[0]

	# try:
	# 	httpClient=httplib.HTTPConnection(mediaHost,8090,timeout=5)
	# 	# httpClient.request('GET',r'/{"msg_type":"server_status"}')
	# 	httpClient.request('GET',r'/{"msg_type":"server_status"}')
	# 	response=httpClient.getresponse()
	# 	data = response.read()

	# 	js = json.loads(data)

	# 	if js['ret_body'] is None:
	# 		print "-----------nothing--------------"
	# 	else:
	# 		print js['ret_body']
	# 		objectList = []
	# 		for channel in js['ret_body']:
	# 			dvrip =  channel['nvr_ip']
	# 			devicechannelindex = channel['channel_index']
	# 			print dvrip,"----",devicechannelindex
	# 			result = XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) & Q(devicechannelindex=devicechannelindex))
	# 			if result.count() == 0:
	# 				print "no"
	# 			else:
	# 				print result.first().channelname,result.first().groupname,result.first().ename,result.first().deptname
	# 				if channel['remote_ip']!=localip:
	# 					objectList.append([result.first(),channel['remote_ip'],channel['remote_port']])
	# 			# print XtWatvediochannelinfo.objects.filter(Q(deviceip=dvrip) | Q(devicechannelindex=devicechannelindex)).count()
	# 		return render(request,'system/base1.html',{"time":now,"localIP":localIP,"objectList":objectList,"dvrip":dvrip,"devicechannelindex":devicechannelindex})

	# except error as e:
	# 	print u"无法连接媒体服务"
	# except TypeError as e:
	# 	print u"解析失败"
	# except Exception as e:
	# 	print u"其他错误"

	# return render(request,'system/base1.html',{"time":now,"localIP":localIP,"userip":localip})	


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
		return render(request,'system/base1.html',{"time":now,"localIP":localIP,"objectList":objectList,"dvrip":dvrip,"devicechannelindex":devicechannelindex,"dlobjects":dlobjects,"pbobjects":pbobjects})

	except error as e:
		print u"无法连接媒体服务"
	except TypeError as e:
		print u"解析失败",e
	except Exception as e:
		print u"其他错误",e

	return render(request,'system/base1.html',{"time":now,"localIP":localIP,"userip":localip})



@login_required
@csrf_exempt
def closeViewVideoView(request):
	remote_ip = request.META['REMOTE_ADDR']
	remote_port = "6000"
	try:
		httpClient=httplib.HTTPConnection(mediaHost,8090,timeout=5)
		msgtosend = '/{"msg_type":"close_channel","remote_ip":"%s","remote_port":"%d"}' % (remote_ip,int(remote_port))

		httpClient.request('GET',msgtosend)
		response=httpClient.getresponse()	
		return HttpResponse("success")
	except BaseException as e:
		print u"无法连接媒体服务",e
	except TypeError as e:
		print u"解析失败"
	except Exception as e:
		print u"其他错误"
	return HttpResponse("error!")		


import os
@login_required
@csrf_exempt
@user_passes_test(if_not_zby,login_url="/home/" )
def restartServicesView(request):
	ret1 = os.system('taskkill /f /im "VideoTransServer.exe"')	
	ret2 = os.system('taskkill /f /im "SDTVideoSwitch.exe"')	
	if(ret1==0 and ret2 ==0):
		return HttpResponse("success")
	else:
		return HttpResponse("error")

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def zbyAccountsView(request):
	new_group,created = Group.objects.get_or_create(name="zby")

	zbyList = new_group.user_set.all()
	return render(request,'system/zbys.html',{"zbyList":zbyList})	

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def addZbyAccountsView(request):
	if request.POST:
		form = UserCreationForm(request.POST)
		if form.is_valid():
			print "user valid!"
			user = form.save()
			new_group,created = Group.objects.get_or_create(name="zby")
			new_group.user_set.add(user)
			return HttpResponseRedirect("/zbyAccounts/")
		else:
			return render(request,'system/addZbyAccount.html',{"form":form})	
	form = UserCreationForm()
	return render(request,'system/addZbyAccount.html',{"form":form})	

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def editZbyAccountView(request,acpk):
	if request.POST:
		print "post edit user"
		instance = get_object_or_404(sysUser,pk=int(acpk))
		userForm = AdminPasswordChangeForm(request.POST,instance=instance)
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
		instance = get_object_or_404(sysUser,pk=int(acpk))
		userForm = AdminPasswordChangeForm(instance = instance)
		return render(request,'system/addAccount.html',{'userForm':userForm,'fun':u"编辑"})	
	except Exception, e:
		print e	

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def deleteZbyAccountView(request,acpk):
	instance = get_object_or_404(sysUser,pk=int(acpk))
	instance.delete()
	return HttpResponseRedirect("/zbyAccounts/")


import zipfile
import StringIO
import datetime

@login_required
@user_passes_test(if_not_zby,login_url="/home/" )
def downloadSystemLogView(request):
	s = StringIO.StringIO()
	zf = zipfile.ZipFile(s, "w")
	# os.chdir("C:\workspace\VideoTransServer")
	for dirname,subdirs,files in os.walk("..\logs"):
		print "dirname:",dirname
		zf.write(dirname)
		for filename in files:
			print "filename:",dirname,filename
			zf.write(os.path.join(dirname,filename))
	zf.close()
	zip_subdir = str(datetime.date.today()) # name of the zip file to be 
	zip_filename = "systemLog_%s.zip" % zip_subdir
	resp = HttpResponse(s.getvalue(),content_type = "application/x-zip-compressed")
	resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
	return resp	