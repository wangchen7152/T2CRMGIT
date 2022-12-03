# _*_ encoding:utf-8 _*_
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import xframe_options_exempt

from system.models import User, Role, UserRole, RolePermission, Module

__author__ = 'wang'
from django.utils.deprecation import MiddlewareMixin


class URLMiddleware(MiddlewareMixin):
    """
    定时中间键，处理url
    """

    def process_request(self, request):

        # 定义允许访问的子hi
        url_list = ['registry', 'login', 'CheckName', 'GenerateCaptcha']
        url = request.path.split('/')[1]
        if url not in url_list:
            user = request.session.get('user')
            if not user:
                return redirect('system:login')
            # 查询用户权限
            try:
                del request.session['user_permission']
            except Exception as e:
                pass
            # 根据用户获取id
            u = User.objects.get(id=user['id'])
            # 获取用户关联的所有角色
            roles = UserRole.objects.values_list('RoleId', flat=True).filter(
                UserId=u.id)
            # 根据角色id拿到moduleid
            moduleid = RolePermission.objects.values_list \
                ('ModuleId', flat=True).filter(RoleId__in=roles)
            opt_value = list(Module.objects.values_list('optValue', flat=True)
                             .filter(pk__in=moduleid))
            # 将全限值添加至session
            request.session['user_permission'] = opt_value


class CustomSystemException(Exception):
    """自定义异常类型"""

    def __init__(self, status_code=400, msg='系统错误请联系管理员'):
        self.status_code = status_code,
        self.msg = msg,

    @staticmethod
    def error(msg):
        c = CustomSystemException(msg=msg)
        return c


class Message(object):
    '''返回公共对象'''

    def __init__(self, status_code=200, msg='success', obj=None):
        self.status_code = status_code,
        self.msg = msg,
        self.obj = obj

    def result(self):
        result = {'status_code': self.status_code[0], 'msg': self.msg[0]}
        if self.obj:
            result['obj'] = self.obj[0]
        return result


class ExceptionMiddleware(MiddlewareMixin):
    @xframe_options_exempt
    def process_exception(self, request, execption):
        if isinstance(execption, CustomSystemException):
            result = Message(status_code=execption.status_code[0],
                             msg=execption.msg[0]).result()
        elif isinstance(execption, Exception) or isinstance(execption,
                                                            BaseException):
            result = Message(status_code=400, msg='服务器异常，请联系管理员').result()
        if request.is_ajax():
            return JsonResponse(result)
        else:
            return render(request, 'system/404.html', result)


def PermissionCheck(permission):
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            user_permissin = request.request.session._session['user_permission']
            if not user_permissin:
                raise CustomSystemException.error('没有权限')
            for p in permission:
                if p not in user_permissin:
                    raise CustomSystemException.error('没有权限')
            else:
                return func(request, *args, **kwargs)

        return wrapper

    return decorator
