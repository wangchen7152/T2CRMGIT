from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from sales.views import connect


class ServeIndex(View):
    def get(self, request):
        return render(request, 'serve/serve_create.html')


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
                        U.username createPeople,
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
