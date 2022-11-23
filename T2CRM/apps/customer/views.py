from apscheduler.schedulers.background import BackgroundScheduler
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.views.decorators.http import require_GET

from customer.models import Customer, CityCourse, Province, CustomerOrders, \
    OrdersDetail, CustomerLoss, CustomerReprieve, LinkMan
from sales.views import connect
from system.views import GenerateCode


class CustomerIndex(View):
    @xframe_options_exempt
    def get(self, request):
        return render(request, 'customer/customer.html')


class CustomerList(View):
    def get(self, request):
        try:
            # 获取第几页
            page_num = request.GET.get('page')
            # 获取每页几条
            limit = request.GET.get('limit')
            # 客户名称
            name = request.GET.get('name')
            # 客户编号
            khno = request.GET.get('khno')
            level = request.GET.get('level')
            # 查询所有账号信息
            customer_list = None
            if name and khno and level:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name, khno__icontains=khno,
                    level=level, state=0).all().order_by('id')
            elif name and khno:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name,
                    khno__icontains=khno, state=0).all().order_by('id')
            elif name and level:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name, level=level,
                    state=0).all().order_by('id')
            elif name:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name, state=0).all().order_by('id')
            elif khno:
                customer_list = Customer.objects.values().filter(
                    khno__icontains=khno, state=0).all().order_by('id')
            elif level:
                customer_list = Customer.objects.values().filter(
                    level=level, state=0).all().order_by('id')
            else:
                customer_list = Customer.objects.values().filter(
                    state=0).order_by('id')
            for customer in customer_list:
                customer['city_id'] = CityCourse.objects.filter(
                    id=customer['city_id'])[0].city_name

            p = Paginator(customer_list, limit)
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
            return JsonResponse(
                {'state': 401, 'msg': '审核用户列表异常，请重新刷新页面'})


class AddCuster(View):
    @xframe_options_exempt
    def get(self, request):
        # 有ID确认为更新用户信息
        id = request.GET.get('id')
        context = None
        if id:
            cus = Customer.objects.get(id=id)
            context = {'cus': cus}
            return render(request, 'customer/customer_add_update.html',
                          context)
        else:
            return render(request, 'customer/customer_add_update.html', context)

    def post(self, request):
        try:
            name = request.POST.get('name').strip()
            id = request.POST.get('id').strip()
            leader_of_company = request.POST.get('leader_of_company').strip()
            area = request.POST.get('area').strip()
            cusManager = request.POST.get('cusManager').strip()
            level = request.POST.get('level').strip()
            xyd = request.POST.get('xyd').strip()
            postCode = request.POST.get('postCode').strip()
            phone = request.POST.get('phone').strip()
            address = request.POST.get('address').strip()
            fax = request.POST.get('fax').strip()
            web_url = request.POST.get('web_url').strip()
            registered_capital = request.POST.get('registered_capital').strip()
            bank = request.POST.get('bank').strip()
            bank_number = request.POST.get('bank_number').strip()
            the_irs = request.POST.get('the_irs').strip()
            land_tax = request.POST.get('land_tax').strip()
            annual_turnover = request.POST.get('annual_turnover').strip()
            city_id = int(request.POST.get('city_name').strip())
            if len(id) > 1:
                return JsonResponse({'code': 400, 'msg': '仅可以勾选一个用户'})
            if id:
                customer = Customer.objects.filter(id=id)
                customer.update(name=name,
                                leader_of_company=leader_of_company,
                                area=area, cusManager=cusManager,
                                level=level, xyd=xyd, postCode=postCode,
                                phone=phone, address=address, fax=fax,
                                web_url=web_url,
                                registered_capital=registered_capital,
                                bank=bank, bank_number=bank_number,
                                the_irs=the_irs, land_tax=land_tax,
                                annual_turnover=annual_turnover,
                                city_id=city_id
                                )
                return JsonResponse({'code': 200, 'msg': '用户信息修改成功'})
            else:
                # 生成客户编号
                _khno = 'T2KH' + GenerateCode(8)
                Customer.objects.create(khno=_khno, name=name,
                                        leader_of_company=leader_of_company,
                                        area=area, cusManager=cusManager,
                                        level=level, xyd=xyd, postCode=postCode,
                                        phone=phone, address=address, fax=fax,
                                        web_url=web_url,
                                        registered_capital=registered_capital,
                                        bank=bank, bank_number=bank_number,
                                        the_irs=the_irs, land_tax=land_tax,
                                        annual_turnover=annual_turnover,
                                        city_id=city_id,
                                        )
                return JsonResponse({'code': 200, 'msg': '用户创建成功'})
        except Exception as e:
            print(e)
            return JsonResponse(
                {'state': 401, 'msg': '创建客户信息异常'})


class DeleteCustomer(View):
    def post(self, request):
        try:
            id = request.POST.get('id')

            Customer.objects.filter(id=id).update(isValid=0, deleted=1,
                                                  updateDate=datetime.now())
            return JsonResponse({'code': 200, 'msg': '删除成功'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 200, 'msg': '删除失败'})


@require_GET
def OrderIndex(request):
    id = request.GET.get('id')
    c = Customer.objects.get(id=id)
    context = {
        'id': id,
        'khnc': c.khno,
        'name': c.name,
        'leader_of_company': c.leader_of_company,
        'address': c.address,
        'phone': c.phone,
    }

    return render(request, 'customer/customer_order.html', context)


@require_GET
def GetOrderList(request):
    # 根据客户主键查询订单信息
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('limit')
        id = request.GET.get('id')
        order = CustomerOrders.objects.values().filter(customer=id)
        p = Paginator(order, page_size)
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
        return JsonResponse(
            {'state': 401, 'msg': '审核用户列表异常，请重新刷新页面'})


@require_GET
def OrderDetail(request):
    # 根据订单ID获取订单详情
    try:
        id = request.GET.get('id')
        c = CustomerOrders.objects.get(id=id)
        context = {
            'id': id,
            'orderNo': c.orderNo,
            'totalPrice': c.totalPrice,
            'address': c.address,
            'state': c.get_state_display(),
        }

        return render(request, 'customer/customer_order_detail.html', context)

    except Exception as e:
        print(e)
        return JsonResponse(
            {'state': 401, 'msg': '获取订单详情异常'})


@require_GET
def OrderDetailList(request):
    # 根据订单ID获取订单详情
    try:
        page_num = request.GET.get('page')
        page_size = request.GET.get('limit')
        id = request.GET.get('id')
        order = OrdersDetail.objects.values().filter(order=id)
        p = Paginator(order, page_size)
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
        return JsonResponse(
            {'state': 401, 'msg': '审核用户列表异常，请重新刷新页面'})


def create_customer_loss():
    """添加暂缓流失客户"""
    try:
        # 创建游标对象
        cursor = connection.cursor()
        # ---------- 第一步：查询暂缓流失客户数据 ----------
        # 编写 SQL
        sql = '''
            SELECT
                c.id id,
                c.khno cusNo,
                c.NAME cusName,
                c.cus_manager cusManager,
                max( co.order_date ) lastOrderTime 
            FROM
                t2_customer c
                LEFT JOIN t2_customer_order co ON c.id = co.cus_id 
            WHERE
                c.is_valid = 1 
                AND c.state = 0 
                AND NOW() > DATE_ADD( c.create_date, INTERVAL 6 MONTH ) 
                AND NOT EXISTS (
                SELECT DISTINCT
                    o.cus_id 
                FROM
                    t2_customer_order o 
                WHERE
                    o.is_valid = 1 
                    AND NOW() < DATE_ADD( o.order_date, INTERVAL 6 MONTH ) 
                    AND c.id = o.cus_id 
                ) 
            GROUP BY
                c.id;
        '''
        # 执行 SQL
        cursor.execute(sql)
        # 返回结果，类型是元组
        customer_loss_tuple = cursor.fetchall()  # 查询当前 SQL 执行后所有的记录
        # 关闭游标
        cursor.close()
        # ---------- 第二步：将暂缓流失客户数据插入客户流失表 ----------
        # 将元组转为列表
        customer_loss_id = []  # 暂缓流失客户 id 列表
        customer_loss_list = []  # 暂缓流失客户数据列表
        # 遍历元组
        for cl in customer_loss_tuple:
            customer_loss_id.append(cl[0])
            customer_loss_list.append(CustomerLoss(cusNo=cl[1],
                                                   cusName=cl[2],
                                                   cusManager=cl[3],
                                                   lastOrderTime=cl[4],
                                                   state=0, deleted=0,
                                                   isValid=1, ))  # 暂缓流失

        # 批量插入客户流失表
        CustomerLoss.objects.bulk_create(customer_loss_list)
        # ---------- 第三步：修改刚才这些数据客户表的状态为 1 暂时流失 ----------
        Customer.objects.filter(id__in=customer_loss_id).update(state=1,
                                                                deleted=0,
                                                                updateDate=datetime.now())
    except Exception as e:
        print(e)
    finally:
        # 关闭连接
        connection.close()


scheduler = BackgroundScheduler()
scheduler.add_job(create_customer_loss, 'interval', minutes=10)
scheduler.start()


class CustomerLoseIndex(View):
    def get(self, request):
        return render(request, 'customer/customer_loss.html')


class CustomerLoseList(View):
    def get(self, request):
        page_num = request.GET.get('page')
        page_size = request.GET.get('limit')
        # 客户编码
        cusNo = request.GET.get('cusNo')
        # 客户名称
        cusName = request.GET.get('cusName')
        # 客户状态
        state = request.GET.get('state')

        lose_list = None
        if cusNo and cusName and state:
            lose_list = CustomerLoss.objects.values().filter(
                cusNo__contains=cusNo, cusName__contains=cusName,
                state=state).order_by('-lastOrderTime')
        elif cusNo and cusName:
            lose_list = CustomerLoss.objects.values().filter(
                cusNo__contains=cusNo, cusName__contains=cusName).order_by(
                '-lastOrderTime')
        elif cusName and state:
            lose_list = CustomerLoss.objects.values().filter(
                cusName__contains=cusName,
                state=state).order_by('-lastOrderTime')
        elif cusNo and state:
            lose_list = CustomerLoss.objects.values().filter(
                cusNo__contains=cusNo, state=state).order_by('-lastOrderTime')
        elif cusNo:
            lose_list = CustomerLoss.objects.values().filter(
                cusNo__contains=cusNo).order_by('-lastOrderTime')
        elif cusName:
            lose_list = CustomerLoss.objects.values().filter(
                cusName__contains=cusName).order_by('-lastOrderTime')
        elif state:
            lose_list = CustomerLoss.objects.values().filter(
                state=state).order_by('-lastOrderTime')
        else:
            lose_list = CustomerLoss.objects.values().all().order_by(
                '-lastOrderTime')
        p = Paginator(lose_list, page_size)
        data = p.page(page_num).object_list
        count = p.count
        context = {
            'code': 0,
            'msg': '加载成功',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)


class CusterLossDetail(View):
    def get(self, request):
        try:
            id = request.GET.get('id')
            CustomerLossDetail = CustomerLoss.objects.get(pk=id)
            context = {
                'cl': CustomerLossDetail
            }
            return render(request, 'customer/customer_reprieve.html', context)
        except CustomerLoss.DoesNotExist as e:
            pass


class GetReprieve(View):
    '''
    查询客户现有的流失措施
    '''

    def get(self, request):
        page_num = request.GET.get('page')
        page_size = request.GET.get('limit')
        id = request.GET.get('id')
        reprieve_list = CustomerReprieve.objects.values().filter(
            customerLoss=id)
        p = Paginator(reprieve_list, page_size)
        data = p.page(page_num).object_list
        count = p.count
        context = {
            'code': 0,
            'msg': '加载成功',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)


class ReprieveAddOrUpdate(View):

    def get(self, request):
        id = request.GET.get('id')
        lossId = request.GET.get('lossId')
        context = {'lossId': lossId}
        if id:
            prieve = CustomerReprieve.objects.get(pk=id)
            context['id'] = id
            context['cp'] = prieve

            return render(request, 'customer/customer_reprieve_add_update.html',
                          context)
        else:
            return render(request, 'customer/customer_reprieve_add_update.html',
                          context)

    def post(self, request):
        try:
            measure = request.POST.get('measure')
            lossId = request.POST.get('lossId')
            id = request.POST.get('id')
            if id:
                CustomerReprieve.objects.filter(pk=id). \
                    update(measure=measure, updateDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': '流失措施修改成功'})
            else:
                cl = CustomerLoss.objects.get(pk=lossId)
                CustomerReprieve.objects.create(customerLoss=cl,
                                                measure=measure)
                return JsonResponse({'code': 200, 'msg': '流失措施新增成功'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'msg': '流失措施新增或修改失败'})


class LossConfirm(View):
    def get(self, request):
        try:
            lossId = request.GET.get('lossId')
            lossReason = request.GET.get('lossReason')
            cl = CustomerLoss.objects.get(pk=lossId)
            cl.lossReason = lossReason
            cl.state = 1
            cl.confirmLossTime = datetime.now()
            cl.save()
            # 修改客户表状态

            Customer.objects.filter(khno=cl.cusNo). \
                update(state=2, updateDate=datetime.now())
            return JsonResponse({'code': 200, 'msg': '用户确认流失成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': e})


class ReprieveDelete(View):
    def get(self, request):
        try:
            id = request.GET.get('id')
            CustomerReprieve.objects.filter(pk=id). \
                update(deleted=1, updateDate=datetime.now())
            return JsonResponse({'code': 200, 'msg': '流失措施删除成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': '流失措施删除失败'})


class GetUserAdd(View):
    """
    进入联系人管理页面
    """

    def get(self, request):
        id = request.GET.get('id')
        cs = Customer.objects.get(id=id)
        context = {
            'cs': cs
        }
        return render(request, 'customer/customer_user.html', context)


class CustomerUserList(View):
    """
    获取客户联系人列表
    """

    def get(self, request):
        try:
            page_num = request.GET.get('page')
            page_size = request.GET.get('limit')
            # 创建连接
            connection = connect()
            # 建立游标
            cursor = connection.cursor()
            # 编辑sql
            sql = """
              SELECT
                    lk.id id,
                    lk.link_name linkName,
                    lk.sex sex,
                    lk.zhiwei zhiwei,
                    lk.phone phone,
                    lk.create_date createDate,
                    lk.office_phone officePhone,
                    lk.update_date updateDate,
                    lk.cus_id CusId	
                FROM
                    t2_customer_linkman lk 
                WHERE
                    is_valid = 1 
                    AND deleted = 0
           """
            # 执行sql
            cursor.execute(sql)
            # 获取返回值
            sc = cursor.fetchall()
            id = request.GET.get('id')

            if id:
                sql += ' AND cus_id = {}'.format(id)

            cursor.execute(sql)
            # 返回结果，类型是dict
            user_list = cursor.fetchall()  # 查询当前 SQL 执行后所有的记录
            # 关闭游标
            cursor.close()
            p = Paginator(user_list, page_size)
            data = p.page(page_num).object_list
            count = p.count
            context = {
                'code': 0,
                'msg': '加载成功',
                'count': count,
                'data': data
            }
            return JsonResponse(context)
        except Exception as e:
            return JsonResponse({'code': 401, 'msg': e})
        finally:
            connection.close()


class AddOrEditUser(View):
    """
    编辑联系人
    """

    def get(self, request):
        id = request.GET.get('id')
        CusId = request.GET.get('CusId')
        context = {'CusId': CusId}
        if id:
            cus_user = LinkMan.objects.get(pk=id)
            context['cus'] = cus_user
            return render(request, 'customer/customer_user_add_edit.html',
                          context)
        else:
            return render(request, 'customer/customer_user_add_edit.html',
                          context)

    def post(self, request):
        try:
            id = request.POST.get('id')
            cus_id = request.POST.get('CusId')
            linkName = request.POST.get('linkName')
            sex = request.POST.get('sex')
            zhiwei = request.POST.get('zhiwei')
            phone = request.POST.get('phone')
            officePhone = request.POST.get('officePhone')
            if id:
                LinkMan.objects.filter(id=id).update(linkName=linkName, sex=sex,
                                                     zhiwei=zhiwei, phone=phone,
                                                     officePhone=officePhone,
                                                     updateDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': '客户联系人修改成功'})
            else:
                # 查询新增用户联系人是否已经录入系统
                linkuser = LinkMan.objects.values().filter(cusId=cus_id,
                                                           linkName=linkName)
                if linkuser:
                    return JsonResponse({'code': 401, 'msg': '客户联系人已存在'})
                else:
                    LinkMan.objects.create(linkName=linkName, sex=sex,
                                           zhiwei=zhiwei, phone=phone,
                                           cusId=cus_id,
                                           officePhone=officePhone)
                return JsonResponse({'code': 200, 'msg': '客户联系人添加成功'})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': e})


class DelUser(View):
    """
    删除联系人
    """

    def post(self, request):
        id = request.POST.get('id')
        if id:
            LinkMan.objects.filter(pk=id).update(deleted=1,
                                                 updateDate=datetime.now())
            return JsonResponse({'code': 200, 'msg': '客户联系人删除成功'})


class CityList(View):
    def get(self, request):
        CityList = CityCourse.objects.values('id', 'city_name').all()
        return JsonResponse(list(CityList), safe=False)
