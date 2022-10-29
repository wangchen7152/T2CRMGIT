# _*_ encoding:utf8 _*_

__author__ = 'wang'

from django import forms
from .models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password',]
