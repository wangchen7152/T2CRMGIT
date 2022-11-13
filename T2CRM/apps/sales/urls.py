# _*_ encoding:utf-8 _*_
from django.views.decorators.csrf import csrf_exempt

__author__ = 'wang'

from .views import *
from django.conf.urls import url
from sales.views import SalesIndex, SalesList, CustomerCompany, \
    CreateSaleChance, DelSaleChance, SaleDevPlanIndex, SaleDevPlanDetail, \
    DeleteSaleChance

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
    url(r'DelSaleChance/', csrf_exempt(DelSaleChance.as_view()),
        name='DelSaleChance'),
    # 进入客户开发计划页面
    url(r'SaleDevPlanIndex/', csrf_exempt(SaleDevPlanIndex.as_view()),
        name='SaleDevPlanIndex'),
    # 点击开发进入开发页面下详情
    url(r'SaleDevPlanDetail/', csrf_exempt(SaleDevPlanDetail.as_view()),
        name='SaleDevPlanDetail'),
    # 查询计划项目
    url(r'CusDevPlanList/', csrf_exempt(CusDevPlanList.as_view()),
        name='CusDevPlanList'),
    # 添加或编辑开发计划
    url(r'AddOrUpdateSaleChance/', csrf_exempt(AddOrUpdateSaleChance.as_view()),
        name='AddOrUpdateSaleChance'),
    # 删除开发计划
    url(r'DeleteSaleChance/', csrf_exempt(DeleteSaleChance.as_view()),
        name='DeleteSaleChance'),
]
