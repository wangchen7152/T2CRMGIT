# _*_ encoding:utf:8 _*_

__author__ = 'wang'

from django.conf.urls import url
from django.urls import path
from customer.views import CustomerIndex, CustomerList, AddCuster, \
    DeleteCustomer, OrderIndex
from django.views.decorators.csrf import csrf_exempt
from customer import views

app_name = 'customer'

urlpatterns = [
    url(r'CustomerIndex/$', CustomerIndex.as_view(), name='CustomerIndex'),
    url(r'customerList/$', CustomerList.as_view(), name='customerList'),
    url(r'AddCuster/$', AddCuster.as_view(), name='AddCuster'),
    path('Order/Index/', views.OrderIndex, name='OrderIndex'),
    url(r'DeleteCustomer/$', csrf_exempt(DeleteCustomer.as_view()),
        name='DeleteCustomer'),
]