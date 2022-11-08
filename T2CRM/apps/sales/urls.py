# _*_ encoding:utf-8 _*_
from django.views.decorators.csrf import csrf_exempt

__author__ = 'wang'

from .views import *
from django.conf.urls import url
from sales.views import SalesIndex, SalesList, CustomerCompany, CreateSaleChance

app_name = 'sales'
urlpatterns = [
    url(r'index/$', SalesIndex.as_view(), name='index'),
    url(r'SalesList/$', SalesList.as_view(), name='SalesList'),
    url(r'CustomerCompany/$', CustomerCompany.as_view(),
        name='CustomerCompany'),
    url(r'CreateUpdate_Sales/', CreateUpdateSales.as_view(),
        name='CreateUpdateSales'),
    url(r'CreateSaleChance/', csrf_exempt(CreateSaleChance.as_view()),
        name='CreateSaleChance'),
]
