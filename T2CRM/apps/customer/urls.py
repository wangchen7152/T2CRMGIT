# _*_ encoding:utf:8 _*_

__author__ = 'wang'

from django.conf.urls import url
from customer.views import CustomerIndex, CustomerList

app_name = 'customer'

urlpatterns = [
    url(r'', CustomerIndex.as_view(), name='CustomerIndex'),
    url(r'', CustomerList.as_view(), name='CustomerList'),
]
