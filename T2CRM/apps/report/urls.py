# _*_ encoding:utf-8 _*_
from django.views.decorators.csrf import csrf_exempt

__author__ = 'wang'

from django.conf.urls import url
from report.views import ReportIndex,ReportCustomerSalePrice

app_name = 'report'
urlpatterns = [
    # 获取客户额度数据
    url(r'ReportIndex/$', csrf_exempt(ReportIndex.as_view()),
        name='ReportIndex'),
    # 进去客户销售页面
    url(r'ReportCustomerSalePrice/$', csrf_exempt(ReportCustomerSalePrice.as_view()),
        name='ReportCustomerSalePrice'),
]
