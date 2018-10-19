# -*- coding: UTF-8 -*-  

import os,re,django
import pyodbc
os.chdir('C:/workspace/tranServerSite')
os.environ.setdefault("DJANGO_SETTINGS_MODULE",'tranServerSite.settings')
django.setup()
from system.models import *

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