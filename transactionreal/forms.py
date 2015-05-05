from datetime import datetime

from django import forms

from bootstrap3_datetime.widgets import DateTimePicker

from transactionreal.models import TransactionReal
from transaction.models import Modification
from groupaccount.models import GroupAccount
from userprofile.models import UserProfile


class NewRealTransactionForm(forms.ModelForm):
    def __init__(self, groupAccountId, user, *args, **kwargs):
        super(NewRealTransactionForm, self).__init__(*args, **kwargs)

        #  self.fields['sender'] = forms.ModelChoiceField(queryset=UserProfile.objects.get(user=user),
        #  widget = forms.HiddenInput, empty_label=None, label='From')
        self.fields['sender'] = forms.ModelChoiceField(queryset=UserProfile.objects.filter(user=user),
                                                       empty_label=None, label='From', widget=forms.HiddenInput())

        self.fields['sender'].initial = UserProfile.objects.get(user=user)
        self.fields['receiver'] = forms.ModelChoiceField(queryset=UserProfile.objects.filter(group_accounts=groupAccountId),
                                                         empty_label=None, label='To')

        self.fields['comment'] = forms.CharField(required=False)

        self.fields['amount'].label = '€'

        self.fields['groupAccount'] = forms.ModelChoiceField(queryset=UserProfile.objects.get(user=user).groupAccounts, widget=forms.Select(attrs={"onChange":'form.submit()'}), empty_label=None, label='Group')
        if GroupAccount.objects.filter(id=groupAccountId).count():
            self.fields['groupAccount'].initial = GroupAccount.objects.get(id=groupAccountId)

        self.fields['modifications'] = forms.ModelMultipleChoiceField(queryset=Modification.objects.all(),
                                                                      required=False,
                                                                      widget=forms.MultipleHiddenInput())
        self.fields['date'] = forms.DateTimeField(widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}), 
                                                  initial=datetime.now)

    class Meta:
        model = TransactionReal
        fields = '__all__'


class EditRealTransactionForm(forms.ModelForm):
    def __init__(self, transaction_id, user, *args, **kwargs):
        super(EditRealTransactionForm, self).__init__(*args, **kwargs)

        transaction = TransactionReal.objects.get(id=transaction_id)

        self.fields['amount'].label = '€'
        self.fields['sender'] = forms.ModelChoiceField(
            queryset=UserProfile.objects.filter(group_accounts=transaction.group_account.id),
            empty_label=None, label='From',
            widget=forms.HiddenInput)

        self.fields['receiver'] = forms.ModelChoiceField(
            queryset=UserProfile.objects.filter(group_accounts=transaction.group_account.id),
            empty_label=None, label='To')

        self.fields['groupAccount'] = forms.ModelChoiceField(
            queryset=GroupAccount.objects.filter(id=transaction.group_account.id),
            empty_label=None,
            label='Group')

        self.fields['groupAccount'].widget.attrs['readonly'] = True
        self.fields['modifications'] = forms.ModelMultipleChoiceField(queryset=Modification.objects.all(),
                                                                      required=False,
                                                                      widget=forms.MultipleHiddenInput())

        self.fields['date'] = forms.DateTimeField(widget=DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}))

    class Meta:
        model = TransactionReal
        fields = '__all__'
