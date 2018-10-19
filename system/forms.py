#coding:utf-8
from django import forms
from django.forms import TextInput,PasswordInput,ModelForm,Select
from models import *
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.validators import MaxValueValidator,MinValueValidator

class networkAdapterForm(forms.Form):
	IP = forms.GenericIPAddressField(label = u"IP地址",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_ip'}))
	IPSubnet = forms.GenericIPAddressField(label = u"子网掩码",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_IPSubnet'}))
	DefaultIPGateway = forms.GenericIPAddressField(label = u"网关",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_DefaultIPGateway'}))

class remoteDatabaseParamsForm(forms.Form):
	IP = forms.GenericIPAddressField(label = u"远端数据库IP地址*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_ip'}))
	Port = forms.IntegerField(label= u"远端数据库的端口*",required=True,initial=5432,min_value=2000,max_value=99999,widget=forms.TextInput(attrs={'class':'form-control','for':'id_port'}))
	username = forms.CharField(label = u"远端数据库用户名*",required=True,initial='postgres',widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))
	password = forms.CharField(label= u"远端数据库密码*",required=True,initial='root',widget = forms.PasswordInput(attrs={'class':'form-control','for':'id_password'}))

class remoteDatabaseParamsModelForm(ModelForm):
	TYPE_CHOICE=[('-1',u'不使用汇总库'),('1','使用汇总库')]
	dbip = forms.GenericIPAddressField(label = u"远端数据库IP地址*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_ip'}))
	username = forms.CharField(label = u"远端数据库用户名*",required=True,initial='postgres',widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))
	password = forms.CharField(label= u"远端数据库密码*",required=True,initial='root',widget = forms.PasswordInput(attrs={'class':'form-control','for':'id_password'}))
	districtcode = forms.ChoiceField(label= u"是否使用汇总库*",required=False,choices=TYPE_CHOICE,widget=Select(attrs={'class':'form-control','for':'id_clienttype'}))
	class Meta:
		model = IcbcDb
		fields=['dbip','username','password','districtcode']

class addUserModelForm(ModelForm):
	def __init__(self,*args,**kwargs):
		super(addUserModelForm,self).__init__(*args,**kwargs)
		TYPE_CHOICE=[('','请选择用户类型'),('0','内网用户'),('1','外网用户')]
		self.fields['usertype'] = forms.ChoiceField(label=u"用户类型*",choices=TYPE_CHOICE,required=True,widget=Select(attrs={'class':'form-control','for':'id_usertype'}))	
	username = forms.CharField(label = u"用户名*",required=True,\
		error_messages={'unique':u"用户名重复"},\
		widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))
	password = forms.CharField(label= u"密码*",required=True,widget = forms.PasswordInput(attrs={'class':'form-control','for':'id_password'}))
	class Meta:
		model = Users
		fields=['username','password','usertype']

class addTerminalModelForm(ModelForm):
	def __init__(self,*args,**kwargs):
		super(addTerminalModelForm,self).__init__(*args,**kwargs)
		userDict = {'0':u"内网用户",'1':u"外网用户"}
		TYPE_CHOICE=[('','请选择终端类型'),('0','内网终端'),('1','外网终端'),('2','policom')]
		USER_CHOICE=[('','请选择终端用户'),]+[(c.userid,c.username+'-'+userDict[c.usertype]) for c in Users.objects.all()]
		self.fields['clienttype'] = forms.ChoiceField(label=u"终端类型*",choices=TYPE_CHOICE,required=True,widget=Select(attrs={'class':'form-control','for':'id_clienttype'}))	
		self.fields['userid'] = forms.ChoiceField(label=u"终端用户*",choices=USER_CHOICE,required=True,widget=Select(attrs={'class':'form-control','for':'id_userid'}))	
	registerid = forms.CharField(label = u"终端注册号*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_registerid'}))	
	username = forms.CharField(label = u"终端名称*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))	
	password = forms.CharField(label= u"密码*",required=True,initial='root',widget = forms.PasswordInput(attrs={'class':'form-control','for':'id_password'}))
	location = forms.CharField(label = u"终端地址*",required=True,error_messages={'unique':u"终端地址重复"},widget=forms.TextInput(attrs={'class':'form-control','for':'id_location'}))	
	class Meta:
		model = Clientterminal
		exclude = ['expires']

class addressMappingModelForm(ModelForm):
	outerip = forms.GenericIPAddressField(label = u"外网IP地址",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_ip'}))
	outerport = forms.IntegerField(label= u"外网端口*",min_value=2000,max_value=99999,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_port'}))
	innerip = forms.GenericIPAddressField(label = u"内网IP地址",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_ip'}))
	innerport = forms.IntegerField(label= u"内网端口*",min_value=2000,max_value=99999,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_port'}))
	class Meta:
		model = AddressMapping
		fields = '__all__'
		error_messages = {
		NON_FIELD_ERRORS:{
		'unique_together':u" %(field_labels)s 不能同时重复 ",
		}
		}

class sipInfoForm(ModelForm):
	centerCode = forms.CharField(label = u"中心编码*",min_length=8,max_length=8,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))
	industryCode = forms.CharField(label = u"行业编码*",min_length=2,max_length=2,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))
	typeCode = forms.CharField(label = u"类型编码*",min_length=3,max_length=3,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_username'}))
	class Meta:
		model = sipInfo
		fields = '__all__'

class serverForm(ModelForm):
	SERVER_CHOICE=[('0','主机'),('1','从机')]
	TYPE_CHOICE=[('0','无权限'),('1','拥有权限')]
	chairman = forms.ChoiceField(label= u"机器类型*",required=False,choices=SERVER_CHOICE,widget=Select(attrs={'class':'form-control','for':'id_clienttype'}))
	servername = forms.CharField(label = u"服务器名称*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	serverip = forms.GenericIPAddressField(label = u"服务器IP地址*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	serverport = forms.IntegerField(label= u"服务器端口*",min_value=2000,max_value=99999,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_serverport'}))
	sipport = forms.IntegerField(label= u"SIP端口*",min_value=2000,max_value=99999,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_sipport'}))
	devicelimitecode = forms.CharField(label = u"限制码*",max_length=50,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	devicelimite = forms.IntegerField(label= u"限制*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimite'}))
	servermask = forms.GenericIPAddressField(label = u"服务器MASK地址*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_mask'}))
	gateway = forms.GenericIPAddressField(label = u"gateway地址*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_gateway'}))
	mediaserverip = forms.GenericIPAddressField(label = u"媒体服务地址*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_gateway'}))
	mediaserverport = forms.IntegerField(label= u"媒体服务端口*",min_value=2000,max_value=99999,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_serverport'}))

	playbackauthority = forms.ChoiceField(label= u"录像回放权限*",required=False,choices=TYPE_CHOICE,widget=Select(attrs={'class':'form-control','for':'id_clienttype'}))
	downloadauthority = forms.ChoiceField(label= u"录像下载权限*",required=False,choices=TYPE_CHOICE,widget=Select(attrs={'class':'form-control','for':'id_clienttype'}))
	class Meta:
		model = Server
		exclude = ['serverid']

class uploadFileForm(forms.Form):
	file = forms.FileField(label="请选择上传文件：update.zip")

class configparamsForm(forms.Form):
	port = forms.IntegerField(label= u"端口*",required=True,validators=[MaxValueValidator(20000),MinValueValidator(80)],widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	heartbeatPort = forms.IntegerField(label= u"心跳端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))

	max_capability = forms.IntegerField(label= u"最大能力*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))

	QCIF = forms.IntegerField(label= u"QCIF*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	CIF = forms.IntegerField(label= u"max_capability*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	FCIF = forms.IntegerField(label= u"4CIF*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	D1 = forms.IntegerField(label= u"D1*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	WD1 = forms.IntegerField(label= u"WD1*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	P720 = forms.IntegerField(label= u"720P*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	P1080 = forms.IntegerField(label= u"1080P*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))

	DefaultFrameRate = forms.IntegerField(label= u"默认帧率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	MaxKeyFramePeriod = forms.IntegerField(label= u"MaxKeyFramePeriod*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	PayloadType = forms.IntegerField(label= u"负载类型*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	# isShowFrameRate = forms.CharField(label= u"是否显示帧率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	BOOLCHOICE=[('TRUE',u"是"),('FALSE',u"否")]
	isShowFrameRate = forms.ChoiceField(label= u"是否显示帧率*",required=False,choices=BOOLCHOICE,widget=Select(attrs={'class':'form-control','for':'id_clienttype'}))
	
	QCIF_BR = forms.IntegerField(label= u"QCIF比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	CIF_BR = forms.IntegerField(label= u"CIF比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	FCIF_BR = forms.IntegerField(label= u"FCIF比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	D1_BR = forms.IntegerField(label= u"D1比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	WD1_BR = forms.IntegerField(label= u"WD1比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	P720_BR = forms.IntegerField(label= u"720P比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	P1080_BR = forms.IntegerField(label= u"1080P比特率*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))


class mediaMonitorParamsForm(forms.Form):
	ip = forms.GenericIPAddressField(label = u"数据库IP*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	port = forms.IntegerField(label= u"数据库端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	dbname = forms.CharField(label = u"数据库名称*",max_length=50,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	username = forms.CharField(label = u"数据库用户名*",max_length=50,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	password = forms.CharField(label = u"数据库密码*",max_length=50,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))

	apppath = forms.CharField(label = u"路径*",max_length=300,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	interval = forms.IntegerField(label= u"媒体程序interval*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	vts_ip = forms.GenericIPAddressField(label = u"媒体程序IP*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	vts_port = forms.IntegerField(label= u"媒体程序端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	vts_heartbeatPort = forms.IntegerField(label= u"媒体程序心跳端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))

class groupParamsForm(forms.Form):
	title = forms.CharField(max_length=150,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	code = forms.CharField(max_length=20,min_length=20,required=False,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))

class serverParamsForm(forms.Form):
	# event = forms.CharField(label = u"event*",max_length=100,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	webserverip = forms.GenericIPAddressField(label = u"媒体服务器ip*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	webserveripport = forms.IntegerField(label= u"媒体服务器端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	address = forms.GenericIPAddressField(label = u"信令服务器ip*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	tcpport = forms.IntegerField(label= u"信令服务器tcp端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	sipport = forms.IntegerField(label= u"信令服务器sip端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	uasaddress = forms.GenericIPAddressField(label = u"注册服务器ip*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	uasport = forms.IntegerField(label= u"注册服务器端口*",validators=[MaxValueValidator(20000),MinValueValidator(80)],required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	uascode = forms.CharField(label = u"注册服务器编码uascode*",max_length=30,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	uaccode = forms.CharField(label = u"信令服务器编码uaccode*",max_length=30,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	uacpwd = forms.CharField(label = u"信令服务器密码uacpwd*",max_length=30,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	icbcclientprefix = forms.CharField(label = u"前缀编码*",max_length=300,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	keepAliveSpan = forms.IntegerField(label= u"心跳间隔/秒*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	multisetting = forms.IntegerField(label= u"堆叠设置*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	remoteIP = forms.GenericIPAddressField(label = u"媒体接收ip*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	recordinter = forms.IntegerField(label= u"录像调阅间隔/小时*",required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_servername'}))
	gonganaddress = forms.GenericIPAddressField(label = u"公安服务ip*",required = True,widget = forms.TextInput(attrs={'class':'form-control','for':'id_serverip'}))
	# [datasource]
	# name=forms.CharField(label = u"数据库名称*",max_length=30,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	# UID = forms.CharField(label = u"UID*",max_length=30,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))
	# PWD = forms.CharField(label = u"PWD*",max_length=30,required=True,widget=forms.TextInput(attrs={'class':'form-control','for':'id_devicelimitecode'}))