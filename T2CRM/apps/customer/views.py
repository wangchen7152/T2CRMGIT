from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt

from customer.models import Customer


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
            username = request.GET.get('username')
            # 客户编号
            khno = request.GET.get('khno')
            level = request.GET.get('level')
            # 查询所有账号信息
            customer_list = None
            if username and khno and level:
                customer_list = Customer.objects.values().filter(
                    username__icontains=username, khno__icontains=khno,
                    level=level).all().order_by('id')
            elif username and khno:
                customer_list = Customer.objects.values().filter(
                    username__icontains=username,
                    khno__icontains=khno).all().order_by('id')
            elif username and level:
                customer_list = Customer.objects.values().filter(
                    username__icontains=username, level=level).all().order_by(
                    'id')
            elif username:
                customer_list = Customer.objects.values().filter(
                    username__icontains=username).all().order_by('id')
            elif khno:
                customer_list = Customer.objects.values().filter(
                    khno__icontains=khno).all().order_by('id')
            elif level:
                customer_list = Customer.objects.values().filter(
                    level=level).all().order_by('id')
            else:
                customer_list = Customer.objects.values().all().order_by('id')

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
            return HttpResponse(
                {'state': 401, 'msg': '审核用户列表异常，请重新刷新页面'})
