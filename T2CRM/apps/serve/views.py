from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from datetime import datetime

from T2CRM.common import PermissionCheck
from customer.models import Customer
from sales.views import connect
from serve.models import CustomerServe
from system.models import User


class ServeIndex(View):
    @PermissionCheck(['3010'])
    def get(self, request):
        user = request.session.get('user'),
        return render(request, 'serve/serve_create.html', {
            'user': user[0]['id']
        })


class ServeList(View):
    def get(self, request):
        try:
            page_num = request.GET.get('page', 1)
            page_size = request.GET.get('limit', 10)
            connection = connect()
            cursor = connection.cursor()
            sql = '''
                  SELECT
                        s.id id,
                        s.assign_time assign_time,
                        s.createPeople_id createPeople,
                        s.service_proce_result serviceProceResult,
                        s.myd myd,
                        s.customer_id customer_id,
                        s.serve_type serveType,
                        s.service_proce service_proce,
                        s.overview overview,
                        s.create_date createDate,
                        s.update_date updateDate,
                        U.id CreateUserID,
                        U.username createPeopleName,
                        su.username AssignUserName,
                        su.id AssignUserID,
                        cu.id customer_id,
                        cu.`name` customer,
                        tu.id  serviceProcePeopleId,
                        tu.username serviceProcePeopleName,
                        TIMESTAMPDIFF(HOUR,s.create_date,s.update_date) UTIME 
                  FROM
                        t2_customer_serve s
                        LEFT JOIN t2_user u ON s.createPeople_id = u.id
                        LEFT JOIN t2_user su ON s.assigner_id = su.id
                        LEFT JOIN t2_user tu ON s.serviceProcePeople_id = tu.id
                        LEFT JOIN t2_customer cu ON s.customer_id = cu.id 
                  WHERE
                        u.is_valid = 1 
                        AND u.state = 1 
                        AND s.deleted = 0
    
           '''
            # 获取查询state信息
            state = request.GET.get('state')
            # 搜索客户名称
            customer_Name = request.GET.get('customer')
            # 搜索客户服务类型
            type = request.GET.get('serveType')
            # 查询处于不同服务进度的客户
            if state:
                sql += ' AND s.state = "{}" '.format(state)
            # 如果有查询条件需要拼接sql
            if customer_Name:
                sql += ' AND s.customer_name like "%{}%" '.format(
                    customer_Name)
            if type:
                sql += ' AND s.serve_type = "{}"'.format(type)
            user_id = request.session['user']['id']
            if user_id != 1:
                sql += ' AND (s.createPeople_id = "%s" OR s.assigner_id = "%s" ' \
                       'OR s.serviceProcePeople_id = "%s")' \
                       % (user_id, user_id, user_id)
            sql += 'ORDER BY s.id DESC;'
            # 执行 SQL
            cursor.execute(sql)
            # 返回结果，类型是dict
            sale_list = cursor.fetchall()  # 查询当前 SQL 执行后所有的记录
            # 关闭游标
            cursor.close()

            p = Paginator(sale_list, page_size)
            data = p.page(page_num).object_list
            count = p.count
            context = {
                'code': 0,
                'msg': '加载成功',
                'count': count,
                'data': data,
            }
            return JsonResponse(context)
        except Exception as e:
            return JsonResponse({'code': 401, 'msg': '执行数据库失败'})
        finally:
            connection.close()


# 进入服务分配页面
class ServeAssign(View):
    @PermissionCheck(['3020'])
    def get(self, request):
        return render(request, 'serve/serve_assign.html')


# 服务创建内创建服务
class CreateWorkflow(View):
    @PermissionCheck(['301001', '301002'])
    def get(self, request):
        id = request.GET.get('id')
        context = None
        if id:
            cs = CustomerServe.objects.get(pk=id)
            context = {"cs": cs}
            return render(request, 'serve/serve_create_create.html', context)
        else:
            return render(request, 'serve/serve_create_create.html', context)

    @PermissionCheck(['301001', '3010012'])
    def post(self, request):
        try:
            # 创建的用户ID
            create_user_id = request.POST.get('createPeople')
            # 服务类型
            serveType = request.POST.get('serveType')
            # 客户名称
            customer = request.POST.get('customer')
            # 服务内容
            serviceRequest = request.POST.get('serviceRequest')
            # 服务描述
            overview = request.POST.get('overview')
            # id如果获取到id则表示为编辑操作
            CsId = request.POST.get('CsId')
            cs = Customer.objects.get(id=customer)
            create_us = User.objects.get(id=create_user_id)
            if CsId:

                CustomerServe.objects.filter(pk=CsId). \
                    update(serveType=serveType, overview=overview,
                           customer=cs, state=1, serviceRequest=serviceRequest,
                           createPeople=create_us, updateDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': "客服服务编辑成功"})

            else:
                server_type = {
                    6: u'咨询', 8: '投诉', 7: u'建议'
                }
                # 插入数据库数据
                cs_repeat = CustomerServe.objects.filter(~Q(state=4),
                                                         customer=cs,
                                                         serveType=serveType)
                if cs_repeat:
                    server_name = server_type.get(cs_repeat[0].serveType)
                    # 已创建
                    if cs_repeat[0].state == 1:
                        return JsonResponse(
                            {'code': 401,
                             'msg': "客户的%s服务已创建，请勿重复创建" % (server_name)})
                    # 已分配
                    if cs_repeat[0].state == 2:
                        return JsonResponse(
                            {'code': 401,
                             'msg': "客户的%s服务已处于分配阶段，请勿重复创建" % (server_name)})
                    # 已处理
                    if cs_repeat[0].state == 3:
                        return JsonResponse(
                            {'code': 401,
                             'msg': "客户的%s服务已处于处理阶段，请勿重复创建" % (server_name)})

                CustomerServe.objects.create(serveType=serveType,
                                             overview=overview,
                                             customer=cs, state=1,
                                             serviceRequest=serviceRequest,
                                             createPeople=create_us,
                                             createDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': "客服%s服务添加成功" % (
                    server_type.get(serveType))})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': e})


# 服务创建内删除客户服务
class DelWorkflow(View):
    @PermissionCheck(['301003'])
    def post(self, request):
        id = request.POST.get('id')
        CustomerServe.objects.filter(pk=id).update(deleted=1)
        return JsonResponse({'code': 200, 'msg': "客服服务删除成功"})


# 服务分配内进入分配
class AssignWorkflow(View):
    @PermissionCheck(['302001'])
    def get(self, request):
        id = request.GET.get('id')
        cs = CustomerServe.objects.get(pk=id)
        customer = Customer.objects.get(id=cs.customer_id)
        context = {
            'cs': cs, 'customerName': customer.name}
        return render(request, 'serve/serve_assign_assign.html', context)


# 服务分配内分配服务
class AssignUpdate(View):
    def post(self, request):
        id = request.POST.get('id')
        # 指派人
        assigner = request.POST.get('assigner')
        # 分配人
        user_id = request.session['user']['id']
        user = User.objects.get(id=user_id)

        CustomerServe.objects.filter(pk=id).update(assigner=user,
                                                   serviceProcePeople=assigner,
                                                   assignTime=datetime.now(),
                                                   state=2,
                                                   updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': "分配成功"})


class ServiceHandle(View):
    @PermissionCheck(['3030'])
    def get(self, request):
        return render(request, 'serve/serve_handle.html')


class HandleWorkflow(View):
    @PermissionCheck(['303001'])
    def get(self, request):
        id = request.GET.get('id')
        cs = CustomerServe.objects.get(pk=id)
        customer_id = cs.customer_id
        customer_name = Customer.objects.get(pk=customer_id).name
        # 指派人/处理人
        serviceProcePeople = User.objects.get(
            id=cs.serviceProcePeople_id).username
        context = {"cs": cs, 'customer_name': customer_name,
                   'serviceProcePeople': serviceProcePeople}
        return render(request, 'serve/serve_handle_handle.html', context)

    @PermissionCheck(['303001'])
    def post(self, request):
        # 服务ID
        id = request.POST.get('id')
        # 处理内容
        serviceProce = request.POST.get('serviceProce')
        CustomerServe.objects.filter(pk=id).update(state=3,
                                                   serviceProce=serviceProce,
                                                   serviceProceTime=datetime.now(),
                                                   updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': "服务处理确认成功"})


class ServeFeedback(View):
    @PermissionCheck(['3040'])
    def get(self, request):
        return render(request, 'serve/serve_feedback.html')

    def post(self, request):
        pass


class ServeFeedbackFeedback(View):
    @PermissionCheck(['304001'])
    def get(self, request):
        id = request.GET.get('id')
        cs = CustomerServe.objects.get(pk=id)
        customer_name = Customer.objects.get(pk=cs.customer_id).name
        # 指派人/处理人
        serviceProcePeople = User.objects.get(
            id=cs.serviceProcePeople_id).username
        context = {'cs': cs, 'customer_name': customer_name,
                   'serviceProcePeople': serviceProcePeople}
        return render(request, 'serve/serve_feedback_feedback.html', context)

    @PermissionCheck(['304001'])
    def post(self, request):
        # 服务ID
        id = request.POST.get('id')
        # 满意度
        myd = request.POST.get('myd')
        # 处理结果
        serviceProceResult = request.POST.get('serviceProceResult')
        CustomerServe.objects.filter(pk=id).update(state=4, myd=myd,
                                                   serviceProceResult=serviceProceResult,
                                                   updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': "服务反馈成功"})


class ServeArchive(View):
    @PermissionCheck(['3050'])
    def get(self, request):
        return render(request, 'serve/serve_archive.html')


class ServeHandleRepeat(View):
    @PermissionCheck(['304002', '303002'])
    def post(self, request):
        try:
            id = request.POST.get('id')
            state = int(request.POST.get('state'))
            CustomerServe.objects.filter(pk=id).update(state=state - 1,
                                                       updateDate=datetime.now())
            server_type = {
                2: '退回分配成功', 3: u'退回处理成功', 4: u'退回反馈成功'
            }
            return JsonResponse({'code': 200, 'msg': server_type[state]})
        except:
            return JsonResponse({'code': 400, 'msg': "操作失败"})
