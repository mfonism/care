from django.db import models

from groupaccount.models import GroupAccount
from userprofile.models import UserProfile

from itertools import chain
from datetime import datetime

class TransactionReal(models.Model):
  amount = models.DecimalField(max_digits=6, decimal_places=2)
  sender = models.ForeignKey(UserProfile, related_name='sender')
  receiver = models.ForeignKey(UserProfile, related_name='receiver')
  comment = models.CharField(max_length=200)
  groupAccount = models.ForeignKey(GroupAccount)
  date = models.DateTimeField(default=datetime.now, editable=True, blank=True)
  
  @staticmethod
  def getSentTransactionsReal(senderId):
    transactions = TransactionReal.objects.filter(sender__id=senderId).order_by("date")
    for transaction in transactions:
      transaction.amountPerPerson = '%.2f' % transaction.amount
      transaction.amountPerPersonFloat = float(transaction.amount)
    return transactions
  
  @staticmethod  
  def getReceivedTransactionsReal(receiverId):
    transactions = TransactionReal.objects.filter(receiver__id=receiverId).order_by("date")
    for transaction in transactions:
      transaction.amountPerPerson = '%.2f' % transaction.amount
      transaction.amountPerPersonFloat = float(transaction.amount)
    return transactions
  
  @staticmethod
  def getTransactionsRealAllSortedByDate(userProfileId):
    sentTransactions = TransactionReal.getSentTransactionsReal(userProfileId)
    receivedTransactions = TransactionReal.getReceivedTransactionsReal(userProfileId)
    transactionsRealAll = list(chain(sentTransactions, receivedTransactions))
    return sorted(transactionsRealAll, key=lambda instance: instance.date, reverse=True)
    
  def __str__(self):
    return self.comment