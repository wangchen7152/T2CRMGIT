# _*_ encoding:utf:8 _*_

__author__ = 'wang'

from django.conf.urls import url
from customer.views import CustomerIndex, CustomerList, AddCuster,DeleteCustomer
from django.views.decorators.csrf import csrf_exempt

app_name = 'customer'

urlpatterns = [
    url(r'CustomerIndex/$', CustomerIndex.as_view(), name='CustomerIndex'),
    url(r'customerList/$', CustomerList.as_view(), name='customerList'),
    url(r'AddCuster/$', AddCuster.as_view(), name='AddCuster'),
    url(r'DeleteCustomer/$', csrf_exempt(DeleteCustomer.as_view()), name='DeleteCustomer'),
]

