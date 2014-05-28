from base.views import BaseView
from groupaccount.forms import NewGroupAccountForm
from groupaccount.models import addGroupAccountInfo
from transaction.models import Transaction
from userprofile.models import UserProfile
from userprofile.models import getBalance

from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.views.generic.edit import FormView

import logging
logger = logging.getLogger(__name__)


class GroupsView(BaseView):
  template_name = "groupaccount/index.html"
  context_object_name = "groups"
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(GroupsView, self).get_context_data(**kwargs)
    groups = Group.objects.all()

    context['groups'] = groups
    context['groupssection'] = True
    return context# Create your views here.
    
    
class MyGroupAccountsView(BaseView):
  template_name = "groupaccount/myaccounts.html"
  context_object_name = "my groups"

  def getActiveMenu(self):
    return 'group'
  
  def getTransactions(self, buyerId):
    transactions = Transaction.objects.filter(buyer__id=buyerId)
    return transactions
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(MyGroupAccountsView, self).get_context_data(**kwargs)
    user = self.request.user

    userProfile = UserProfile.objects.get(user=user)
    groupAccounts = userProfile.groupAccounts.all()
    
    for groupAccount in groupAccounts:
      groupAccount = addGroupAccountInfo(groupAccount)

    context['groups'] = groupAccounts
    context['groupssection'] = True
    return context# Create your views here.


class NewGroupAccountView(FormView, BaseView):
  template_name = 'groupaccount/new.html'
  form_class = NewGroupAccountForm
  success_url = '/account/new/success/'
  
  def getActiveMenu(self):
    return 'accounts'

  def form_valid(self, form):
    context = super(NewGroupAccountView, self).form_valid(form)
    groupAccount = form.save()
    userProfile = UserProfile.objects.get(user=self.request.user)
    userProfile.groupAccounts.add(groupAccount)
    userProfile.save()
    
    return HttpResponseRedirect('/accounts/new/success/')
  
  def get_context_data(self, **kwargs):
    context = super(NewGroupAccountView, self).get_context_data(**kwargs)
    
    form = NewGroupAccountForm()
    context['form'] = form
    
    return context


class SucessNewGroupAccountView(BaseView):
  template_name = 'groupaccount/newsuccess.html'
  
  def getActiveMenu(self):
    return 'accounts'
