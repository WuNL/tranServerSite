from django.conf.urls import url,include
from funMoudle import views as fun_views

urlpatterns = [
	url(r'^function/viewVideo/$',fun_views.viewVideoView),
	url(r'^function/viewVideoWithRefresh/(?P<remoteip>.+)/(?P<remoteport>\d+)/$',fun_views.viewVideoWithRefreshView),

	url(r'^function/closeView/$',fun_views.closeViewVideoView),

	url(r'^function/restartServices/$',fun_views.restartServicesView),

	url(r'^zbyAccounts/$',fun_views.zbyAccountsView),
	url(r'^addZbyAccount/$',fun_views.addZbyAccountsView),
	url(r'^editZbyAccount/(?P<acpk>\d+)/$',fun_views.editZbyAccountView),
	url(r'^deleteZbyAccount/(?P<acpk>\d+)/$',fun_views.deleteZbyAccountView),	

	url(r'^system/downloadSystemLog/$',fun_views.downloadSystemLogView),
]