# _*_ encoding:utf-8 _*_
from django.views.decorators.csrf import csrf_exempt

__author__ = 'wang'

from django.conf.urls import url
from report.views import ReportIndex, ReportCustomerSalePrice, \
    CompositionCustomer, CustomerLossPage, CustomerContribute, \
    SelectCustomerLevel, SelectCustomerServer, GetCustomerLossList

app_name = 'report'
urlpatterns = [
    # 获取客户额度数据
    url(r'ReportIndex/$', csrf_exempt(ReportIndex.as_view()),
        name='ReportIndex'),
    # 进去客户销售页面
    url(r'ReportCustomerSalePrice/$',
        csrf_exempt(ReportCustomerSalePrice.as_view()),
        name='ReportCustomerSalePrice'),
    # 进去客户构成分析页面
    url(r'CompositionCustomer/$', csrf_exempt(CompositionCustomer.as_view()),
        name='CompositionCustomer'),
    # 进去客户流失页面
    url(r'CustomerLossPage/$', csrf_exempt(CustomerLossPage.as_view()),
        name='CustomerLossPage'),
    # 进去客户贡献页面
    url(r'CustomerContribute/$', csrf_exempt(CustomerContribute.as_view()),
        name='CustomerContribute'),
    # 获取客户构成分许图
    url(r'SelectCustomerLevel/$', csrf_exempt(SelectCustomerLevel.as_view()),
        name='SelectCustomerLevel'),
    # 进去客户服务图
    url(r'SelectCustomerServer/$', csrf_exempt(SelectCustomerServer.as_view()),
        name='SelectCustomerServer'),
    # 进去客户服务图
    url(r'GetCustomerLossList/$', csrf_exempt(GetCustomerLossList.as_view()),
        name='GetCustomerLossList'),

]
