from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from datetime import datetime

from customer.models import Customer
from sales.views import connect
from serve.models import CustomerServe
from system.models import User


class ServeIndex(View):
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
                        U.id CreateUserID,
                        U.username createPeopleName,
                        su.username AssignUserName,
                        su.id AssignUserID,
                        s.customer_id customer_id,
                        s.serve_type serveType,
                        s.overview overview,
                        s.create_date createDate,
                        s.update_date updateDate,
                        cu.id customer_id,
                        cu.`name` customer 
                  FROM
                        t2_customer_serve s
                        LEFT JOIN t2_user u ON s.createPeople_id = u.id
                        LEFT JOIN t2_user su ON s.assigner_id = u.id
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
                sql += ' AND s.createPeople_id = "{}"'.format(user_id)
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


class ServeAssign(View):
    def get(self, request):
        return render(request, 'serve/serve_assign.html')


class CreateWorkflow(View):
    def get(self, request):
        id = request.GET.get('id')
        context = None
        if id:
            cs = CustomerServe.objects.get(pk=id)
            context = {"cs": cs}
            return render(request, 'serve/serve_create_create.html', context)
        else:
            return render(request, 'serve/serve_create_create.html', context)

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
                # 插入数据库数据
                if CustomerServe.objects.filter(customer=cs,
                                                serveType=serveType):
                    return JsonResponse(
                        {'code': 401, 'msg': "客户同样的服务已创建，请勿重复添加"})

                CustomerServe.objects.create(serveType=serveType,
                                             overview=overview,
                                             customer=cs, state=1,
                                             serviceRequest=serviceRequest,
                                             createPeople=create_us,
                                             createDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': "客服服务添加成功"})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': e})


class DelWorkflow(View):
    def post(self, request):
        id = request.POST.get('id')
        CustomerServe.objects.filter(pk=id).update(deleted=1)
        return JsonResponse({'code': 200, 'msg': "客服服务删除成功"})
