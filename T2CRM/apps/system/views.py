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

from T2CRM.common import PermissionCheck, Message
from sales.views import connect
from .models import User, Module, Role, RolePermission, UserRole
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
    @PermissionCheck(['5010'])
    def get(self, request):
        user_list = User.objects.all()
        return render(request, 'system/audit_account.html', {
            "user_list": user_list,
        })

    @PermissionCheck(['501001', '501002'])
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


class CustomerManager(View):
    def get(self, request):
        # 创建连接
        connection = connect()
        # 建立游标
        cursor = connection.cursor()
        # 编辑sql
        sql = '''
        SELECT
            u.id id,
            u.username username
        FROM
            t2_user u
            LEFT JOIN t2_user_role r ON u.id = r.user_id
            LEFT JOIN t2_role o on o.id= r.role_id
        WHERE
            u.is_valid = 1 
            AND u.deleted =0
        '''
        # 获取需要客户权限id
        id = request.GET.get('id')
        if id:
            sql += ' AND o.id = "%s"' % (id)
        # 执行sql
        cursor.execute(sql)
        # 返回结果，类型是dict
        user_list = cursor.fetchall()  # 查询当前 SQL 执行后所有的记录
        # 关闭游标
        cursor.close()
        return JsonResponse(user_list, safe=False)


class ModulePage(View):
    @PermissionCheck(['5040'])
    @xframe_options_exempt
    def get(self, request):
        return render(request, 'system/module/module.html')


class ModuleList(View):
    def get(self, request):
        try:
            queryset = Module.objects.values('id', 'parent', 'moduleName',
                                             'moduleStyle',
                                             'optValue', 'url', 'grade',
                                             'createDate',
                                             'updateDate').order_by('id').all()
            return JsonResponse(list(queryset), safe=False)
        except Exception as e:
            pass


class AddUpdateModule(View):
    @PermissionCheck(['504001', '504002', '504003'])
    @xframe_options_exempt
    def get(self, request):
        id = request.GET.get('id')
        parentId = request.GET.get('parentId')
        grade = int(request.GET.get('grade'))
        context = {'grade': int(grade), 'parentId': parentId}
        if parentId != 'null' and int(parentId) != -1:
            parent_name = Module.objects.get(pk=parentId).moduleName
            context['parent_name'] = parent_name
        if id:
            module = Module.objects.get(pk=id)
            context['module'] = module
            if grade != 0:
                parent_name = Module.objects.get(pk=module.parent_id).moduleName
                context['parent_name'] = parent_name
            return render(request, 'system/module/add_update.html', context)
        else:
            return render(request, 'system/module/add_update.html', context)

    @PermissionCheck(['504001', '504002', '504003'])
    def post(self, request):
        try:
            data = request.POST.dict()
            # 如果有id证明为编辑
            id = data.get('id')
            # 移除前端传回的空字段，防止数据库无法更新
            new_date = {}
            try:
                for key, value in data.items():
                    if value != '':
                        new_date[key] = value
            except Exception as e:
                print(e)
            # 移除掉parent_name
            if new_date.get('parent_name'):
                new_date.pop('parent_name')
            if id:
                new_date.pop('parentId')
                new_date['updateDate'] = datetime.now()
                Module.objects.filter(pk=id).update(**new_date)
                return JsonResponse({'code': 200, 'msg': "编辑成功"})
            # 编辑操作
            else:
                # 验证权限码是否重复
                optValue = new_date.get('optValue')
                if Module.objects.filter(optValue=optValue):
                    return JsonResponse({'code': 400, 'msg': "权限码已存在！"})
                parentId = int(new_date.pop('parentId'))
                if parentId and parentId == -1:
                    pass
                else:
                    parent = Module.objects.get(pk=parentId)
                    new_date['parent'] = parent
                Module.objects.create(**new_date)
            return JsonResponse({'code': 200, 'msg': "创建成功"})
        except Exception as e:
            pass


class DeleteModule(View):
    @PermissionCheck(['504004'])
    def post(self, request):
        try:
            user_id = request.session.get('user')['id']
            if user_id == 1:
                id = request.POST.dict().get('id')
                if Module.objects.filter(parent=id):
                    return JsonResponse(
                        {'code': 400, 'msg': '请先删除子菜单'})
                else:
                    Module.objects.filter(pk=id).update(isValid=0,
                                                        updateDate=datetime.now())
                    return JsonResponse({'code': 200, 'msg': "删除成功"})
            else:
                return JsonResponse({'code': 200, 'msg': "没有删除权限，请联系管理员处理"})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': "删除失败"})


class RolePage(View):
    @PermissionCheck(['5020'])
    @xframe_options_exempt
    def get(self, request):
        return render(request, 'system/role/role.html')


class RoleList(View):
    @xframe_options_exempt
    def get(self, request):
        try:
            # 获取第几页
            page_num = request.GET.get('page')
            # 获取每页几条
            limit = request.GET.get('limit')
            RoleList = Role.objects.values('id', 'RoleRemark', 'RoleName',
                                           'CreateDate', 'UpdateDate').all()
            # roleName
            roleName = request.GET.get('roleName')
            if roleName:
                RoleList = RoleList.filter(RoleName__icontains=roleName)
            p = Paginator(RoleList, limit)
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
            return JsonResponse({'code': 400, 'msg': 'error'})


class AddUpdateRole(View):
    @PermissionCheck(['502001', '502002', '502003'])
    def get(self, request):
        id = request.GET.get('id')
        if id:
            role = Role.objects.get(pk=id)
            return render(request, 'system/role/add_update.html', {
                'role': role
            })
        else:
            return render(request, 'system/role/add_update.html')

    @PermissionCheck(['502001', '502002', '502003'])
    def post(self, request):
        try:
            # 角色名称
            RoleName = request.POST.get('roleName')
            # 角色备注
            roleRemark = request.POST.get('roleRemark')
            # 角色ID
            id = request.POST.get('id')
            if id:
                Role.objects.filter(pk=id).update(RoleName=RoleName,
                                                  RoleRemark=roleRemark,
                                                  UpdateDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': '角色编辑成功'})
            else:
                if Role.objects.filter(RoleName=RoleName):
                    return JsonResponse({'code': 400, 'msg': '角色名称已存在'})
                Role.objects.create(RoleName=RoleName, RoleRemark=roleRemark,
                                    CreateDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': '角色创建成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': '角色操作失败'})


class DeleteRole(View):
    # 删除角色
    @PermissionCheck(['502004'])
    def post(self, request):
        id = request.POST.get('id')
        Role.objects.filter(pk=id).update(isValid=0)
        # 查看是否仍有用户绑定该角色
        UserRoleS = UserRole.objects.filter(RoleId__in=id)
        if UserRoleS:
            return JsonResponse(Message(400, '已有用户关联该角色，请先解除关联').result())

        # 将角色绑定的权限清空
        RolePermission.objects.filter(RoleId__id=id).delete()

        return JsonResponse({'code': 200, 'msg': '角色删除成功'})


class RoleGrant(View):
    def get(self, request):
        id = request.GET.get('id')
        return render(request, 'system/role/grant.html', {'id': id})


class SelectRoleModule(View):
    def get(self, request):
        # 角色ID
        RoleId = request.GET.get('id')
        # 查询所有模块
        module = list(Module.objects.values('id', 'parent', 'moduleName').all())
        # 查询角色已拥有权限,values_list返回元组，flat=true只有一个值，则返回列表
        RoleModule = RolePermission.objects. \
            values_list('ModuleId', flat=True).filter(RoleId__id=RoleId).all()
        for m in module:
            if m.get('id') in RoleModule:
                m['checked'] = 'true'
        return JsonResponse(module, safe=False)

    def post(self, request):
        try:
            role_id = request.POST.get('role_id')
            ModuleIdListStr = request.POST.get('module_checked_id')
            if ModuleIdListStr == '':
                # 删除所有权限，方便重新添加
                RolePermission.objects.filter(RoleId__id=role_id).delete()
                return JsonResponse({'code': 200, 'msg': '角色删除权限成功'})
            else:
                ModuleIdListInt = [int(i) for i in ModuleIdListStr.split(',')]
                role = Role.objects.get(pk=role_id)
                # 删除所有权限，方便重新添加
                RolePermission.objects.filter(RoleId__id=role_id).delete()
                # 创建空列表，放入需要绑定的数据
                CreateID = []
                for id in ModuleIdListInt:
                    CreateID.append(RolePermission(RoleId=role,
                                                   ModuleId=Module.objects.get(
                                                       pk=id)))
                # 执行批量创建操作
                RolePermission.objects.bulk_create(CreateID)
                return JsonResponse({'code': 200, 'msg': '角色添加权限成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': '权限添加失败'})


class UserPage(View):
    @PermissionCheck(['5030'])
    def get(self, request):
        return render(request, 'system/user/user.html')


class UserList(View):
    def get(self, request):
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页几条
        limit = request.GET.get('limit')
        UserList = User.objects.values('id', 'username', 'truename', 'email',
                                       'phone', 'createDate',
                                       'updateDate').filter(state=1,
                                                            deleted=0).all()
        username = request.GET.get('username')
        if username:
            UserList = UserList.filter(username__contains=username)
        email = request.GET.get('email')
        if email:
            UserList = UserList.filter(email__contains=email)
        phone = request.GET.get('phone')
        if phone:
            UserList = UserList.filter(phone__contains=phone)
        p = Paginator(UserList, limit)
        data = p.page(page_num).object_list
        count = p.count
        context = {
            'code': 0,
            'msg': '加载成功',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)


class UserAddOrUpdate(View):
    @PermissionCheck(['503001', '503002', '503003'])
    def get(self, request):
        id = request.GET.get('id')
        if id:
            user = User.objects.get(pk=id)
            return render(request, 'system/user/add_update.html',
                          {'user': user})
        else:
            return render(request, 'system/user/add_update.html')

    @PermissionCheck(['503001', '503002', '503003'])
    def post(self, request):
        data = request.POST.dict()
        # 用户id，如果有则表示当前为编辑用户的操作
        id = data.get('id')
        # 用户名称
        username = data.get('username')
        # 邮箱
        email = data.get('email')
        # 电话
        phone = data.get('phone')
        data.pop('id')
        select = data.get('select')
        data.pop('select')
        if id:
            if User.objects.filter(
                    ~Q(pk=id), Q(username=username) | Q(phone=phone) | Q(
                        email=email)):
                return JsonResponse({'code': 400, 'msg': '用户信息已存在'})
            else:
                User.objects.filter(pk=id).update(**data)
                if select != '':
                    self.CreateUserRole(id, select)
                else:
                    UserRole.objects.filter(UserId=id).delete()
                return JsonResponse({'code': 200, 'msg': '用户编辑成功'})
        else:
            if User.objects.filter(Q(username=username) | Q(phone=phone) | Q(
                    email=email)):
                return JsonResponse({'code': 400, 'msg': '用户信息已存在'})
            # 设置初始化密码，方便用户直接登录
            password = data.get('username')
            _salt = GenerateCode(4)
            md5_password = md5((password + _salt).encode(
                encoding='utf-8')).hexdigest()
            data['password'] = md5_password
            data['state'] = 1
            data['salt'] = _salt
            user = User.objects.create(**data)
            try:
                if select != '':
                    self.CreateUserRole(user.id, select)
            except Exception as e:
                print(e)
            return JsonResponse({'code': 200, 'msg': '用户创建成功,密码为用户名，请尽快修改密码'})

    @staticmethod
    def CreateUserRole(idaa, RoleIDS):
        if RoleIDS != '':
            # 清除用户已添加角色信息
            UserRole.objects.filter(UserId=idaa).delete()
            # 获取添加角色的ID
            RoleIDS = [int(id) for id in RoleIDS.split(',')]
            # 便利角色id放入list,后续可以批量创建
            role_list = []
            for RoleId in RoleIDS:
                role_list.append(UserRole(UserId=User.objects.get(pk=idaa),
                                          RoleId=Role.objects.get(
                                              pk=RoleId)))
            UserRole.objects.bulk_create(role_list)


class SelectRoleForUser(View):
    def get(self, request):
        try:
            role = Role.objects.values('id', 'RoleName').all().order_by('id')
            data = {'role': list(role)}
            id = request.GET.get('id')
            if id:
                roleIds = UserRole.objects.values_list('RoleId',
                                                       flat=True).filter(
                    UserId__id=id)
                userRole = Role.objects.values('id', 'RoleName').filter(
                    pk__in=roleIds).all()
                data['userRole'] = list(userRole)
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': '角色获取失败'})


class DelUser(View):
    @PermissionCheck(['503004'])
    def post(self, request):
        ids = request.POST.getlist('ids')
        try:
            # 方式一
            # 删除勾选用户和角色的关联关系
            # 根据用户id查询所有用户和角色关联的字段
            # UserRoleID = UserRole.objects. \
            #     values_list('id', flat=True).filter(UserId__in=ids)
            # if UserRoleID:
            #     UserRole.objects.filter(pk__in=list(UserRoleID)).delete()
            # 方式二
            # UserRole.objects.filter(UserId__id__in=ids).delete()
            # 删除用户
            User.objects.filter(pk__in=ids).update(deleted=1)
            return JsonResponse({'code': 200, 'msg': '用户删除成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': '用户删除失败'})


@require_GET
def index_init(request):
    """初始化菜单"""
    context = {
        "homeInfo": {
            "title": "首页",
            "href": "welcome"
        },
        "logoInfo": {
            "title": "CRM-智能办公",
            "image": "static/images/logo.png",
            "href": ""
        },
    }
    # 初始化一级列表
    GradeOne = []
    # 查询所有的一级菜单
    first_module = Module.objects.values('id', 'moduleName', 'moduleStyle',
                                         'url', 'orders').filter(grade=0).all()
    # 从session获取当前用户信息
    user = User.objects.get(id=request.session.get('user')['id'])
    # 根据用户id获取角色id
    roleids = UserRole.objects.values_list('RoleId', flat=True).filter(
        UserId=user.id)
    # 根据角色id获取角色关联权限信息

    modules = RolePermission.objects.values_list('ModuleId', flat=True).filter(
        RoleId__in=roleids)

    for m1 in first_module:
        if m1['id'] not in modules:
            continue
        first = {
            "title": m1['moduleName'],
            "icon": m1['url'],
            "href": "",
            "target": "_self",
        }
        GradeOne.append(first)

        # 初始化二级列表
        GradeTwo = []
        # 查询所有的二级菜单
        GradeTwo_module = Module.objects.values \
            ('id', 'moduleName', 'moduleStyle', 'url', 'orders').filter(
            parent=m1['id']).all()
        for m2 in GradeTwo_module:
            if m2['id'] not in modules:
                continue
            second = {
                "title": m2['moduleName'],
                "href": m2['url'],
                "icon": m2['moduleStyle'],
                "target": "_self"
            }
            # 将二级新信息添加二级菜单
            GradeTwo.append(second)
        # 将二级信息添加如first格式内
        first['child'] = GradeTwo
    # 一级菜单加入menu内
    context['menuInfo'] = GradeOne
    return JsonResponse(context)
