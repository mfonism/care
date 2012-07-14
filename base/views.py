from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.views.generic.edit import UpdateView
from itertools import chain
from base.forms import LoginForm, UserCreateForm
from userprofile.models import UserProfile
from transaction.models import Transaction
from groupaccount.forms import NewGroupAccountForm
from groupaccountinvite.models import GroupAccountInvite
import logging

class BaseView(TemplateView):
  template_name = "base/base.html"
  context_object_name = "base"
  
  logger = logging.getLogger(__name__)
  logger.addHandler(logging.StreamHandler())
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(BaseView, self).get_context_data(**kwargs)
    if self.request.user.is_authenticated():
      userProfile = UserProfile.objects.get(user=self.request.user)
      invites = GroupAccountInvite.objects.filter(invitee=userProfile, isAccepted=False, isDeclined=False)
      context['user'] = self.request.user
      context['hasInvites'] = invites.exists()
      context['nInvites'] = invites.count()
      context['displayname'] = userProfile.displayname
      context['isLoggedin'] = True
    return context


class BaseUpdateView(UpdateView):
  template_name = "base/base.html"
  context_object_name = "base"
  
  logger = logging.getLogger(__name__)
  logger.addHandler(logging.StreamHandler())
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(BaseUpdateView, self).get_context_data(**kwargs)
    if self.request.user.is_authenticated():
      userProfile = UserProfile.objects.get(user=self.request.user)
      invites = GroupAccountInvite.objects.filter(invitee=userProfile, isAccepted=False, isDeclined=False)
      context['user'] = self.request.user
      context['hasInvites'] = invites.exists()
      context['nInvites'] = invites.count()
      context['displayname'] = userProfile.displayname
      context['isLoggedin'] = True
    return context


class HomeView(BaseView):
  template_name = "base/index.html"
  context_object_name = "homepage"

  def getTransactions(self, buyerId):
    transactions = Transaction.objects.filter(buyer__id=buyerId)
    return transactions
  
  def get_context_data(self, **kwargs):
    from groupaccount.views import MyTransactionView
    # Call the base implementation first to get a context
    context = super(HomeView, self).get_context_data(**kwargs)
    user = self.request.user

    userProfile = UserProfile.objects.get(user=user)
    groupAccounts = userProfile.groupAccounts.all()
    
    transactionView = MyTransactionView()
    buyerTransactions = transactionView.getBuyerTransactions(userProfile.id)
    consumerTransactions = transactionView.getConsumerTransactions(userProfile.id)
    transactionsAll = list(chain(buyerTransactions, consumerTransactions))
    for transaction in transactionsAll:
      print transaction.date
    transactionsAllSorted = sorted(transactionsAll, key=lambda instance: instance.date, reverse=True)
    
    sentTransactions = transactionView.getSentTransactionsReal(userProfile.id)
    receivedTransactions = transactionView.getReceivedTransactionsReal(userProfile.id)
    transactionsRealAll = list(chain(sentTransactions, receivedTransactions))
    transactionsRealAllSorted = sorted(transactionsRealAll, key=lambda instance: instance.date, reverse=True)
    
    myTotalBalanceFloat = 0.0
    
    for groupAccount in groupAccounts:
      groupAccount.myBalanceFloat = MyTransactionView.getBalance(transactionView, groupAccount.id, userProfile.id)
      groupAccount.myBalance = '%.2f' % groupAccount.myBalanceFloat
      myTotalBalanceFloat += groupAccount.myBalanceFloat
      myTotalBalance = '%.2f' % myTotalBalanceFloat
      context['myTotalBalance'] = myTotalBalance
      context['myTotalBalanceFloat'] = myTotalBalanceFloat
      
    context['transactionsAll'] = transactionsAllSorted[0:5]
    context['transactionsRealAll'] = transactionsRealAllSorted[0:5]
    context['groups'] = groupAccounts
    context['homesection'] = True
    return context
  
  
class AboutView(BaseView):
  template_name = "base/about.html"
  context_object_name = "about"
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(AboutView, self).get_context_data(**kwargs)
    context['aboutsection'] = True
    return context


class HelpView(BaseView):
  template_name = "base/help.html"
  context_object_name = "help"
  
  def get_context_data(self, **kwargs):
    # Call the base implementation first to get a context
    context = super(HelpView, self).get_context_data(**kwargs)
    context['helpsection'] = True
    return context
          
        
def register(request):
  def errorHandle(error):
    form = UserCreateForm()
    context = RequestContext(request)
    context['error'] = error
    context['form'] = form
    return render_to_response('base/register.html', context)
    
  if request.method == 'POST': # If the form has been submitted...
    form = UserCreateForm(request.POST) # A form bound to the POST data
    if form.is_valid():
      form.save()
      context = RequestContext(request)
      context['registered'] = True
      return render_to_response('base/register.html', context)
    else:
      error = u'form is invalid'
      return errorHandle(error)
  else:
    form = UserCreateForm() # An unbound form
    context = RequestContext(request)
    context['form'] = form
    return render_to_response('base/register.html', context)


def newGroupAccount(request):
  def errorHandle(error):
    form = NewGroupAccountForm()
    context = RequestContext(request)
    if request.user.is_authenticated():
      context['user'] = request.user
      context['isLoggedin'] = True
    context['error'] = error
    context['form'] = form
    context['groupssection'] = True
    return render_to_response('base/newgroup.html', context)
  
  if request.method == 'POST': # If the form has been submitted...
    form = NewGroupAccountForm(request.POST) # A form bound to the POST data
    if form.is_valid():
      groupAccount = form.save()
      userProfile = UserProfile.objects.get(user=request.user)
      userProfile.groupAccounts.add(groupAccount)
      userProfile.save()
      context = RequestContext(request)
      if request.user.is_authenticated():
        context['user'] = request.user
        context['isLoggedin'] = True
      context['registered'] = True
      context['groupssection'] = True
      return render_to_response('groupaccount/newsuccess.html', context)
    else:
      error = u'form is invalid'
      return errorHandle(error)
  else:
    form = NewGroupAccountForm() # An unbound form
    context = RequestContext(request)
    if request.user.is_authenticated():
      context['user'] = request.user
      context['isLoggedin'] = True
    context['form'] = form
    context['groupssection'] = True
    return render_to_response('base/newgroup.html', context)

        
def login(request):
  def errorHandle(error):
    form = LoginForm()
    context = RequestContext(request)
    context['error'] = error
    context['form'] = form
    return render_to_response('base/login.html', context)
        
  if request.method == 'POST': # If the form has been submitted...
    form = LoginForm(request.POST) # A form bound to the POST data
    if form.is_valid(): # All validation rules pass
      username = request.POST['username']
      password = request.POST['password']
      user = auth.authenticate(username=username, password=password)
      if user is not None:
        if user.is_active:
          # Redirect to a success page.
          auth.login(request, user)
          context = RequestContext(request)
          context['user'] = user
          context['isLoggedin'] = True
          return render_to_response('base/index.html', context)
        else:
          # Return a 'disabled account' error message
          error = u'account disabled'
          return errorHandle(error)
      else:
        # Return an 'invalid login' error message.
        error = u'invalid login'
        return errorHandle(error)
    else:
      error = u'form is invalid'
      return errorHandle(error)
  else:
    form = LoginForm() # An unbound form
    context = RequestContext(request)
    context['form'] = form
    return render_to_response('base/login.html', context)

    
def logout(request):
  auth.logout(request)
  context = RequestContext(request)
  return render_to_response('base/index.html', context)