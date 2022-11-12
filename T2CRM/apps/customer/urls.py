# _*_ encoding:utf:8 _*_

__author__ = 'wang'

from django.conf.urls import url
from django.urls import path
from customer.views import CustomerIndex, CustomerList, AddCuster, \
    DeleteCustomer, CustomerLoseIndex, CustomerLoseList, CusterLossDetail, \
    GetReprieve, ReprieveAddOrUpdate, LossConfirm, ReprieveDelete, GetUserAdd, \
    AddOrEditUser, DelUser, CustomerUserList, CityList

from django.views.decorators.csrf import csrf_exempt
from customer import views

app_name = 'customer'

urlpatterns = [
    # 进入客户管理页面的url
    url(r'CustomerIndex/$', CustomerIndex.as_view(), name='CustomerIndex'),
    # 获取客户列表的url
    url(r'customerList/$', CustomerList.as_view(), name='customerList'),
    # 添加客户的url
    url(r'AddCuster/$', AddCuster.as_view(), name='AddCuster'),
    # 订单查看url
    path('Order/Index/', views.OrderIndex, name='OrderIndex'),
    # 订单列表的url
    path('OrderList/', views.GetOrderList, name='GetOrderList'),
    # 订单详情的url
    path('OrderDetail/', views.OrderDetail, name='OrderDetail'),
    # 订单详情列表数据的url
    path('OrderDetailList/', views.OrderDetailList, name='OrderDetailList'),
    url(r'DeleteCustomer/$', csrf_exempt(DeleteCustomer.as_view()),
        name='DeleteCustomer'),
    # 进去流失客户管理页面url
    url(r'CustomerLoseIndex/$', CustomerLoseIndex.as_view(),
        name='CustomerLoseIndex'),
    # 查询流失客户管理用户列表url
    url(r'CustomerLoseList/$', CustomerLoseList.as_view(),
        name='CustomerLoseList'),
    # 获取添加暂缓页面的url
    url(r'CusterLossDetail/', CusterLossDetail.as_view(),
        name='CusterLossDetail'),
    # 查询流失措施接口url
    url(r'GetReprieve/', GetReprieve.as_view(),
        name='GetReprieve'),
    # 查询创建或编辑流失措施接口url
    url(r'ReprieveAddOrUpdate/', csrf_exempt(ReprieveAddOrUpdate.as_view()),
        name='ReprieveAddOrUpdate'),
    # 确认流失url
    url(r'LossConfirm/', csrf_exempt(LossConfirm.as_view()),
        name='LossConfirm'),
    # 删除流失措施url
    url(r'ReprieveDelete/', csrf_exempt(ReprieveDelete.as_view()),
        name='ReprieveDelete'),
    # 进入客户联系人页面
    url(r'GetUserAdd/', csrf_exempt(GetUserAdd.as_view()), name='GetUserAdd'),
    # 编辑客户联系人
    url(r'AddOrEditUser/', csrf_exempt(AddOrEditUser.as_view()), name='AddOrEditUser'),
    # 删除客户联系人
    url(r'DelUser/', csrf_exempt(DelUser.as_view()), name='DelUser'),
    # 删除客户联系人
    url(r'CustomerUserList/', csrf_exempt(CustomerUserList.as_view()),
        name='CustomerUserList'),
    # 获取城市列表
    url(r'CityList/', csrf_exempt(CityList.as_view()), name='CityList'),
]
