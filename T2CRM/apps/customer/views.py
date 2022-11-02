from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from django.views.decorators.http import require_GET

from customer.models import Customer, CityCourse, Province, CustomerOrders, \
    OrdersDetail
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
                    level=level).all().order_by('id')
            elif name and khno:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name,
                    khno__icontains=khno).all().order_by('id')
            elif name and level:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name, level=level).all().order_by(
                    'id')
            elif name:
                customer_list = Customer.objects.values().filter(
                    username__icontains=name).all().order_by('id')
            elif khno:
                customer_list = Customer.objects.values().filter(
                    khno__icontains=khno).all().order_by('id')
            elif level:
                customer_list = Customer.objects.values().filter(
                    level=level).all().order_by('id')
            else:
                customer_list = Customer.objects.values().all().order_by('id')
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
        city = CityCourse.objects.all()
        id = request.GET.get('id')
        if id:
            custer = Customer.objects.values().filter(id=id)
            return render(request, 'customer/customer_add_update.html',
                          custer[0])
        else:
            return render(request, 'customer/customer_add_update.html', {
                'city': city
            })

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
            city_id = request.POST.get('city_id').strip()
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
            'state': c.state,
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