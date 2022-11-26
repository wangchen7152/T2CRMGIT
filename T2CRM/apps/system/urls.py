# _*_ encoding:utf:8 _*_
from django.views.decorators.csrf import csrf_exempt

__author__ = 'wang'

from django.conf.urls import url
from django.urls import path
from .views import Registry, Login, CheckUsername, GenerateCaptcha, Index, \
    Welcome, AuditAccount, AccountUserList, UserSetting, LogOut, ChangePassword, \
    CustomerManager, ModulePage, ModuleList, AddUpdateModule, DeleteModule
from . import views

# 设置命名空间名称
app_name = 'system'

urlpatterns = [
    url(r'^registry/$', Registry.as_view(), name='registry'),
    url(r'^login/$', Login.as_view(), name='login'),
    # 验证用户唯一性
    url(r'^CheckName/$', CheckUsername.as_view(), name='check_name'),
    # 生成验证码
    url(r'^GenerateCaptcha/$', GenerateCaptcha.as_view(), name='Captcha'),
    url(r'^index$', Index.as_view(), name='index'),
    # url(r'^welcome$', Welcome.as_view(), name='welcome'),
    # # 首页
    # path('', views.Index, name='index'),
    # # 首页欢迎
    path('welcome/', views.Welcome, name='welcome'),
    # 用户审核
    url(r'^audit_account/$', AuditAccount.as_view(), name='audit_account'),
    url(r'^audit_account/$', AuditAccount.as_view(), name='audit_account'),
    # 加载账号列表
    url(r'^AccountUserList/$', AccountUserList.as_view(),
        name='AccountUserList'),
    # 用户个人信息展示
    url(r'^UserSetting/$', UserSetting.as_view(),
        name='UserSetting'),
    # 退出登录
    url(r'^LogOut/$', LogOut.as_view(), name='LogOut'),
    # 修改密码
    url(r'^ChangePassword/$', ChangePassword.as_view(), name='ChangePassword'),

    # path('AccountUserList/', views.AccountUserList, name='AccountUserList'),
    # 删除流失措施url
    url(r'CustomerManager/', csrf_exempt(CustomerManager.as_view()),
        name='CustomerManager'),
    # 删除流失措施url
    url(r'ModulePage/', ModulePage.as_view(), name='ModulePage'),
    # 获取权限菜单
    url(r'ModuleList/$', ModuleList.as_view(), name='ModuleList'),
    # 编辑或创建权限菜单
    url(r'AddUpdateModule/$', csrf_exempt(AddUpdateModule.as_view()),
        name='AddUpdateModule'),
    # 删除权限菜单
    url(r'DeleteModule/$', csrf_exempt(DeleteModule.as_view()),
        name='DeleteModule'),
]
