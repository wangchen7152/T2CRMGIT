# Create your views here.
import pymysql
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from datetime import datetime

from dbutil import pymysql_pool
from .models import SaleChance

# 准备数据
config = {
    'host': 'localhost',  # 数据库ip
    'port': 3306,  # 数据库端口
    'user': 'root',  # 数据库用户名
    'password': '123456',  # 数据库密码
    'database': 't2crm',  # 具体的一个库 等价于database
    'charset': 'utf8mb4',  # 字符集
    # 默认获取的数据是元祖类型，如果想要字典类型的数据
    'cursorclass': pymysql.cursors.DictCursor
}

# 初始化连接池对象
connect_pool = pymysql_pool.ConnectionPool(size=10, name='mysql_pool', **config)


# 从连接池中获取连接
def connect():
    # 从连接池中获取连接
    connection = connect_pool.get_connection()
    return connection


class SalesIndex(View):
    """跳转营销管理首页"""

    @xframe_options_exempt
    def get(self, request):
        return render(request, 'sales/sale_chance.html')


class SalesList(View):
    """
    获取所有营销客户列表
    """

    @xframe_options_exempt
    def get(self, request):
        try:
            page_num = request.GET.get('page', 1)
            page_size = request.GET.get('limit', 10)
            connection = connect()
            cursor = connection.cursor()
            sql = '''
               SELECT
                   sc.id id,
                   sc.chance_source chanceSource,
                   sc.customer_id customerId,
                   sc.customer_name customerName,
                   sc.cgjl cgjl,
                   sc.overview overview,
                   sc.link_man linkMan,
                   sc.link_phone linkPhone,
                   sc.description description,
                   u.username createMan,
                   u.username assignMan,
                   sc.assign_time assignTime,
                   sc.state state,
                   sc.dev_result devResult,
                   sc.is_valid isValid,
                   sc.create_date createDate,
                   sc.update_date updateDate
               FROM
                   t2_sale_chance sc
               INNER JOIN t2_customer c ON sc.customer_id = c.id
               LEFT JOIN t2_user u ON sc.assign_man = u.id 
               WHERE
                   sc.is_valid = 1 AND c.is_valid = 1
           '''

            # 搜索客户名称
            customerName = request.GET.get('customerName')
            # 搜索客户状态
            state = request.GET.get('state')
            # 搜索创建人
            createMan = request.GET.get('createMan')
            # 开发计划状态
            devResult = request.GET.get('devResult')
            # 如果有查询条件需要拼接sql
            if customerName:
                sql += ' AND sc.customerName like "%{}%" '.format(customerName)
            if createMan:
                sql += ' AND sc.createMan like "%{}%" '.format(createMan)
            if state:
                sql += ' AND sc.state = "{}"  '.format(state)
            if devResult:
                sql += ' AND sc.devResult = "%{}%" '.format(devResult)
            sql += 'ORDER BY sc.id DESC;'
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


class CreateUpdateSales(View):
    """
    进入添加或编辑营销机会
    """

    @xframe_options_exempt
    def get(self, request):
        salechanceId = request.GET.get('saleChanceId')
        if salechanceId:
            sale = SaleChance.objects.filter(id=salechanceId)
            return render(request, 'sales/add_update.html',
                          sale[0])
        else:
            return render(request, 'sales/add_update.html')

    def post(self, request):
        pass


class CustomerCompany(View):
    def get(self, request):
        try:
            # 创建连接
            connection = connect()
            # 建立游标
            cursor = connection.cursor()
            # 编辑sql
            sql = """
                SELECT
                    t.name,
                    t.id 
                FROM
                    t2_customer t 
                WHERE
                    t.state = 0 AND
                    t.id not IN (select s.customer_id from t2_sale_chance s) 

            """
            # 执行sql
            cursor.execute(sql)
            # 获取返回值
            sc = cursor.fetchall()
            # 关闭游标
            cursor.close()
            return JsonResponse(list(sc), safe=False)
        except Exception as e:
            return JsonResponse({'code': 200, 'msg': '查询客户信息失败'})
        finally:
            connection.close()


class CreateSaleChance(View):
    def post(self, request):
        try:
            # 获取营销机会的ID
            id = request.POST.get('id')
            # 获取客户ID
            customerId = request.POST.get('customerId')
            # 获取客户名称
            customerName = request.POST.get('customerName')
            # 获取指派人的ID
            assignManId = request.POST.get('assignManId')
            # 获取指派人名称
            assignMan = request.POST.get('assignMan')
            # 机会来源
            chanceSource = request.POST.get('chanceSource')
            # 联系人
            linkMan = request.POST.get('linkMan')
            # 联系电话
            linkPhone = request.POST.get('linkPhone')
            # 概要
            overview = request.POST.get('overview')
            # 成功机率
            cgjl = request.POST.get('cgjl')
            # 机会描述
            description = request.POST.get('description')

            SaleChance.objects.create(chanceSource=chanceSource,
                                      customerId=customerId,
                                      customerName=customerName, cgjl=cgjl,
                                      overview=overview, linkMan=linkMan,
                                      linkPhone=linkPhone,
                                      description=description, createMan=1,
                                      assignMan=assignMan,
                                      assignTime=datetime.now(), state=1)
            return JsonResponse({'code': 200, 'msg': '营销机会创建成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': e})
