from django.conf.urls import url,include
from system import views as main_views
from django.contrib.auth import views as auth_views

urlpatterns = [
	url('^', include('django.contrib.auth.urls')),
	url(r'^$',main_views.homeView),
	url(r'^home/$',main_views.homeView),
	url(r'^system/configNET/$',main_views.configNETView),
	url(r'^system/configRemoteDatabase/$',main_views.configRemoteDatabaseView),
	url(r'^system/configJQ/$',main_views.configJQ),
	url(r'^system/configJQAjax/$',main_views.configJQAjax),
	url(r'^system/configJQAjaxDelete/$',main_views.configJQAjaxDelete),
	url(r'^system/configLocalAjax/$',main_views.configLocalAjax),

	url(r'^system/notifyUserAjax/$',main_views.notifyUserAjax),

	url(r'^system/filterRemote/$',main_views.filterRemoteAjaxView),

	url(r'^system/accounts/$',main_views.accountsView),
	url(r'^system/editAccount/(?P<acpk>\d+)/$',main_views.editAccountView),
	url(r'^system/deleteAccount/(?P<acpk>\d+)/$',main_views.deleteAccountView),
	url(r'^system/addAccount/$',main_views.addAccountView),

	url(r'^system/servers/$',main_views.serversView),
	url(r'^system/editServer/(?P<acpk>\d+)/$',main_views.editServerView),
	url(r'^system/deleteServer/(?P<acpk>\d+)/$',main_views.deleteServerView),
	url(r'^system/addServer/$',main_views.addServerView),

	url(r'^system/terminals/$',main_views.terminalsView),
	url(r'^system/addTerminal/$',main_views.addTerminalView),
	url(r'^system/editTerminal/(?P<tmlpk>\d+)/$',main_views.editTerminalView),
	url(r'^system/deleteTerminal/(?P<tmlpk>\d+)/$',main_views.deleteTerminalView),

	url(r'^system/sipInfo/$',main_views.sipInfoView),


	url(r'^system/addressMapping/$',main_views.addressMappingView),
	url(r'^system/addAddressMapping/$',main_views.addMappingView),
	url(r'^system/editAddressMapping/(?P<ampk>\d+)/$',main_views.editAddressMappingView),
	url(r'^system/deleteAddressMapping/(?P<ampk>\d+)/$',main_views.deleteAddressMappingView),	

	url(r'^system/syncDB/$',main_views.syncDBAjax),

	url(r'^system/userLog/$',main_views.userLogView),
	url(r'^system/downloadUserLog/$',main_views.downloadUserLogView),
	url(r'^system/clearUserLog/$',main_views.clearUserLogView),

	url(r'^system/policeLog/$',main_views.policeLogView),
	url(r'^system/downloadPoliceLog/$',main_views.downloadPoliceLogView),
	url(r'^system/clearPoliceLog/$',main_views.clearPoliceLogView),	

	url(r'^system/test/$',main_views.testView),

	url(r'^system/shutdown/$',main_views.shutdownView),
	url(r'^system/restart/$',main_views.restartView),

	url(r'^system/update/$',main_views.updateView),
	url(r'^system/configparams/$',main_views.configparamsettingView),
	url(r'^system/configmediamonitorparams/$',main_views.configMediaMonitorParamsView),
	url(r'^system/configserverparams/$',main_views.configServerParamsView),

	url(r'^system/closechannel/(?P<remoteip>.+)/(?P<remoteport>\d+)/$',main_views.closeChannelView),


	url(r'^system/configgroupparams/$',main_views.configGroupParamsView),

	url(r'^system/getICBCTreeFromLogs/$',main_views.getICBCTreeFromLogsAjaxView),

	url(r'^about/$',main_views.aboutView),
	]