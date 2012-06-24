from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from groupaccountinvite.views import MyGroupAccountInvitesView, AcceptInviteView, DeclineInviteView

urlpatterns = patterns('',
  url(r'^$', login_required(MyGroupAccountInvitesView.as_view())),
  url(r'^new/$', 'groupaccountinvite.views.newInvite'), 
  url(r'^accept/(?P<inviteId>\d+)/$', login_required(AcceptInviteView.as_view())),
  url(r'^decline/(?P<inviteId>\d+)/$', login_required(DeclineInviteView.as_view())),
)