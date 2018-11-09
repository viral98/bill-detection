from django import forms
from django.contrib.auth.models import User
from .models import Receipt


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password' ]


class ReceiptForm(forms.ModelForm):

    class Meta:
        model = Receipt
        fields = ['CompanyName', 'receipt_picture']        