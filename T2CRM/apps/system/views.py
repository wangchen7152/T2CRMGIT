# _*_encoding:utf8 _*_
import re
import string
import random
from hashlib import md5
from datetime import datetime

from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
# Create your views here.
from django.views import View
from django.views.decorators.clickjacking import xframe_options_sameorigin, \
    xframe_options_exempt
from django.views.decorators.http import require_GET, require_POST
from captcha.image import ImageCaptcha

from .models import User
from .forms import UserForm


class Registry(View):
    def get(self, request):
        return render(request, 'system/registry.html', {

        })

    def post(self, request):
        user_form = UserForm(request.POST)
        try:
            if user_form.is_valid():
                _username = request.POST.get('username', "")
                password = request.POST.get('password', "")
                re_password = request.POST.get('repassword', "")
                captcha = request.POST.get('captcha', "")
                session_code = request.session.get('code')
                if password != re_password:
                    return JsonResponse({"code": 301, 'msg': '两次密码输入不一致'})
                if not session_code:
                    return JsonResponse({"code": 400, 'msg': '验证码失效，请重新回去！'})
                if captcha.upper() != session_code.upper():
                    return JsonResponse({"code": 400, 'msg': '验证码输入错误'})

                # 准备盐MD5加密
                # hexdigest()返回16进制字符串
                _salt = GenerateCode(4)
                md5_password = md5((password + _salt).encode(
                    encoding='utf-8')).hexdigest()
                if not User.objects.filter(username=_username):
                    try:
                        user = User(username=_username, password=md5_password,
                                    salt=_salt)
                        user.save()
                    except Exception as e:
                        print(e)
                else:
                    return JsonResponse({"code": 401, 'msg': "用户名已经存在"})

                return JsonResponse(
                    {"code": 200, 'msg': "注册成功，请联系管理员审核!,稍后为您跳转至登录页面！"})

        except Exception as e:
            print(e)
            return JsonResponse({"code": 400, 'msg': "注册失败"})


class Login(View):
    def get(self, request):
        # 从session获取账号信息
        user = request.session.get('user')
        if not user:
            return render(request, 'system/login.html', {

            })
        else:
            return redirect('system:index')

    def post(self, request):
        try:
            _username = request.POST.get('username')
            _password = request.POST.get('password')
            captcha = request.POST.get('captcha', "")
            session_code = request.session.get('code')
            if not session_code:
                return JsonResponse({"code": 400, 'msg': '验证码失效，请滚！！！！'})
            if captcha.upper() != session_code.upper():
                return JsonResponse({"code": 400, 'msg': '验证码输入错误'})
            user = User.objects.values().filter(username=_username, isValid=1)
            if len(user) == 1:
                state = user[0].get('state')
                if int(state) == int(0) or int(state) == int(-1):
                    return JsonResponse(
                        {"code": 400, 'msg': '用户未审核或已被拉入黑名单,请联系管理员处理'})
                else:
                    _salt = user[0].get('salt')
                    md5_password = md5(
                        (_password + _salt).encode(
                            encoding='utf-8')).hexdigest()
                    if md5_password == user[0].get('password'):
                        # 登录成功，将用户信息存储到session
                        session_user = {'id': user[0].get('id'),
                                        'username': user[0].get('username')}
                        request.session['user'] = session_user
                        remember_me = request.POST.get('remember_me', '')
                        if remember_me == 1:
                            request.session.set_expiry(60 * 60 * 24 * 7)
                        else:
                            request.session.set_expiry(0)
                        return JsonResponse({'code': 200, 'msg': '登录成功'})

                    else:
                        return JsonResponse(
                            {"code": 200, 'msg': "用户名或密码有误，请重新输入！！"})
            elif len(user) > 1:
                return JsonResponse({"code": 400, 'msg': "该账户存在异常，请联系管理员！"})
            else:
                return JsonResponse({"code": 400, 'msg': "用户不存在"})
        except Exception as e:
            print(e)


@method_decorator(require_GET, name='dispatch')
class CheckUsername(View):
    """
    验证账号是否唯一
    """

    def get(self, request):
        try:
            _username = request.GET.get('username', '')
            User.objects.get(username=_username)
            return JsonResponse({"code": 200, 'msg': '用户存在'})
        except User.DoesNotExist as e:
            print(e)
            return JsonResponse({"code": 200, 'msg': '可以注册'})


def GenerateCode(value=4):
    """
    生成字母加数字组合验证码字符串方法
    """
    # 获取所有的大小写字母
    letters = string.ascii_letters
    # 获取所有数字
    digits = string.digits
    return ''.join(random.choice(letters + digits) for i in range(value))


class GenerateCaptcha(View):
    """
    生成图像验证码
    """

    def get(self, request):
        code = GenerateCode()
        # 生成图形验证码
        captcha = ImageCaptcha().generate(code)
        # 将验证码放入session中
        request.session['code'] = code
        # 设置过期时间
        request.session.set_expiry(120)
        return HttpResponse(captcha.getvalue())


@method_decorator(require_GET, name='dispatch')
class Index(View):
    def get(self, request):
        return render(request, 'system/index.html', {

        })


@xframe_options_exempt
@require_GET
def Welcome(request):
    return render(request, 'system/welcome.html', {

    })


class AuditAccount(View):
    def get(self, request):
        user_list = User.objects.all()
        return render(request, 'system/audit_account.html', {
            "user_list": user_list,
        })

    def post(self, request):
        try:
            id_list = request.POST.getlist('ids')
            state = request.POST.get('state')
            User.objects.filter(id__in=id_list).update(state=state,
                                                       updateDate=datetime.now())
            return JsonResponse({'state': 200, 'msg': '修改成功'})

        except Exception as e:
            return JsonResponse({'state': 400, 'msg': '修改失败'})


class AccountUserList(View):
    def get(self, request):
        try:
            # 获取第几页
            page_num = request.GET.get('page')
            # 获取每页几条
            limit = request.GET.get('limit')
            # 搜索名称
            username = request.GET.get('username')
            # 审核状态
            state = request.GET.get('state')
            # 查询所有账号信息
            user_list = None
            if username and state:
                # 添加values(),返回的为QuerySet，不加为对象
                user_list = User.objects.values().filter \
                    (~Q(username='admin'), isValid=1,
                     username__icontains=username,
                     state=state).all().order_by('-id')
            elif username:
                user_list = User.objects.values().filter \
                    (~Q(username='admin'), isValid=1,
                     username__icontains=username).all().order_by('-id')
            elif state:
                user_list = User.objects.values().filter(
                    ~Q(username='admin'), isValid=1, state=state).all(). \
                    order_by('-id')
            else:
                user_list = User.objects.values().filter(
                    ~Q(username='admin'), isValid=1).all().order_by('-id')
            # 为保障用户数据安全，移除密码返回
            for user in user_list:
                user.pop('password')
            p = Paginator(user_list, limit)
            data = p.page(page_num).object_list
            count = p.count
            context = {
                'code': 0,
                'msg': '加载成功',
                'count': count,
                'data': list(data)
            }
            return JsonResponse(context)
        except Exception as e:
            print(e)
            return HttpResponse(
                {'state': 401, 'msg': '审核用户列表异常，请重新刷新页面'})


class UserSetting(View):
    def get(self, request):
        user_id = request.session['user']['id']
        if user_id:
            user = User.objects.values('id', 'username', 'truename', 'phone',
                                       'email') \
                .filter(id=user_id, isValid=1)
            return render(request, 'system/settings.html', user[0])

        else:
            redirect('system:login')

    def post(self, request):
        try:
            user_id = request.session['user']['id']
            user = User.objects.filter(id=user_id)
            username = request.POST.get('username')
            real_name = request.POST.get('truename')
            email = request.POST.get('email')
            if User.objects.filter(~Q(id=user_id), email=email):
                return JsonResponse({'code': 400, 'msg': "您输入的邮箱已存在"})
            phone = request.POST.get('phone')
            if re.match(r'1[3,4,5,6,7,8]\d{9}', phone) and len(phone) == 11:

                user.update(username=username, truename=real_name, email=email,
                            phone=phone)
                return JsonResponse({'code': 200, 'msg': "修改成功"})
            else:
                return JsonResponse({'code': 400, 'msg': "手机号码输入格式不正确"})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': "修改失败"})


class LogOut(View):
    def get(self, request):
        logout(request=request)
        # request.session.flush()
        return redirect('system:login')


class ChangePassword(View):
    def get(self, request):
        return render(request, 'system/password.html')

    def post(self, request):
        try:
            new_password = request.POST.get('new_password')
            old_password = request.POST.get('old_password')
            again_password = request.POST.get('again_password')
            user_id = request.session['user']['id']
            user = User.objects.values().filter(id=user_id, isValid=1)
            _salt = user[0].get('salt')
            md5_password = md5((old_password + _salt).encode(
                    encoding='utf-8')).hexdigest()
            if user[0].get('password') == md5_password:
                if old_password != new_password or old_password != again_password:
                    if new_password == again_password:
                        password = md5((new_password + _salt).
                                       encode(encoding='utf-8')).hexdigest()
                        user.update(password=password)
                        # 清除session信息，使用新密码登录
                        request.session.flush()
                        return JsonResponse({'code': 200, 'msg': "密码修改成功"})
                    else:
                        return JsonResponse({'code': 400, 'msg': "两次密码输入不一致"})
                else:
                    return JsonResponse({'code': 400, 'msg': "新密码和旧密码一致"})
            else:
                return JsonResponse({'code': 400, 'msg': "原密码输入有误"})

        except Exception as e:
            return JsonResponse({'code': 400, 'msg': "修改用户信息失败"})
