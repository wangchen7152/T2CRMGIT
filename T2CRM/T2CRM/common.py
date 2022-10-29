# _*_ encoding:utf-8 _*_
from django.shortcuts import redirect

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


