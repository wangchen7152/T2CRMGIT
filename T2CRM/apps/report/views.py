from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from customer.models import Customer


class ReportIndex(View):
    def get(self, request):
        return render(request, 'report/contribute.html')


class ReportCustomerSalePrice(View):
    def get(self, request):
        try:
            page_num = request.GET.get('page', 1)
            page_size = request.GET.get('limit', 10)
            '''sql 未执行
                 SELECT
                    t.id id,
                    t.NAME NAME,
                    sum( d.sum ) Price
                 FROM
                    t2_customer t
                    LEFT JOIN t2_customer_order o ON t.id = o.cus_id
                    LEFT JOIN t2_order_details d ON d.order_id = o.id 
                 WHERE
                    t.is_valid = 1 
                    AND t.deleted = 0 
                    AND o.is_valid = 1 
                    AND d.deleted = 0

           '''
            # 查询所有客户
            cs_list = Customer.objects.values('id', 'name').annotate(
                sum=Sum('customerorders__ordersdetail__sum')).order_by('-sum')
            # 客户服务名称
            customerName = request.GET.get('customerName')
            if customerName:
                cs_list = cs_list.filter(name__icontains=customerName)
            type = int(request.GET.get('type'))
            if type == 1:
                cs_list = cs_list.filter(sum__gte=0, sum__lte=1000)
            if type == 2:
                cs_list = cs_list.filter(sum__gt=1000, sum__lte=3000)
            if type == 3:
                cs_list = cs_list.filter(sum__gt=3000, sum__lte=5000)
            if type == 4:
                cs_list = cs_list.filter(sum__gt=5000)
            p = Paginator(cs_list, page_size)
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
            return JsonResponse({'code': 401, 'msg': '执行数据库失败'})
