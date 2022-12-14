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
            # ????????????state??????
            state = request.GET.get('state')
            # ??????????????????
            customer_Name = request.GET.get('customer')
            # ????????????????????????
            type = request.GET.get('serveType')
            # ???????????????????????????????????????
            if state:
                sql += ' AND s.state = "{}" '.format(state)
            # ?????????????????????????????????sql
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
            # ?????? SQL
            cursor.execute(sql)
            # ????????????????????????dict
            sale_list = cursor.fetchall()  # ???????????? SQL ????????????????????????
            # ????????????
            cursor.close()

            p = Paginator(sale_list, page_size)
            data = p.page(page_num).object_list
            count = p.count
            context = {
                'code': 0,
                'msg': '????????????',
                'count': count,
                'data': data,
            }
            return JsonResponse(context)
        except Exception as e:
            return JsonResponse({'code': 401, 'msg': '?????????????????????'})
        finally:
            connection.close()


# ????????????????????????
class ServeAssign(View):
    @PermissionCheck(['3020'])
    def get(self, request):
        return render(request, 'serve/serve_assign.html')


# ???????????????????????????
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
            # ???????????????ID
            create_user_id = request.POST.get('createPeople')
            # ????????????
            serveType = request.POST.get('serveType')
            # ????????????
            customer = request.POST.get('customer')
            # ????????????
            serviceRequest = request.POST.get('serviceRequest')
            # ????????????
            overview = request.POST.get('overview')
            # id???????????????id????????????????????????
            CsId = request.POST.get('CsId')
            cs = Customer.objects.get(id=customer)
            create_us = User.objects.get(id=create_user_id)
            if CsId:

                CustomerServe.objects.filter(pk=CsId). \
                    update(serveType=serveType, overview=overview,
                           customer=cs, state=1, serviceRequest=serviceRequest,
                           createPeople=create_us, updateDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': "????????????????????????"})

            else:
                server_type = {
                    6: u'??????', 8: '??????', 7: u'??????'
                }
                # ?????????????????????
                cs_repeat = CustomerServe.objects.filter(~Q(state=4),
                                                         customer=cs,
                                                         serveType=serveType)
                if cs_repeat:
                    server_name = server_type.get(cs_repeat[0].serveType)
                    # ?????????
                    if cs_repeat[0].state == 1:
                        return JsonResponse(
                            {'code': 401,
                             'msg': "?????????%s????????????????????????????????????" % (server_name)})
                    # ?????????
                    if cs_repeat[0].state == 2:
                        return JsonResponse(
                            {'code': 401,
                             'msg': "?????????%s????????????????????????????????????????????????" % (server_name)})
                    # ?????????
                    if cs_repeat[0].state == 3:
                        return JsonResponse(
                            {'code': 401,
                             'msg': "?????????%s????????????????????????????????????????????????" % (server_name)})

                CustomerServe.objects.create(serveType=serveType,
                                             overview=overview,
                                             customer=cs, state=1,
                                             serviceRequest=serviceRequest,
                                             createPeople=create_us,
                                             createDate=datetime.now())
                return JsonResponse({'code': 200, 'msg': "??????%s??????????????????" % (
                    server_type.get(serveType))})
        except Exception as e:
            return JsonResponse({'code': 400, 'msg': e})


# ?????????????????????????????????
class DelWorkflow(View):
    @PermissionCheck(['301003'])
    def post(self, request):
        id = request.POST.get('id')
        CustomerServe.objects.filter(pk=id).update(deleted=1)
        return JsonResponse({'code': 200, 'msg': "????????????????????????"})


# ???????????????????????????
class AssignWorkflow(View):
    @PermissionCheck(['302001'])
    def get(self, request):
        id = request.GET.get('id')
        cs = CustomerServe.objects.get(pk=id)
        customer = Customer.objects.get(id=cs.customer_id)
        context = {
            'cs': cs, 'customerName': customer.name}
        return render(request, 'serve/serve_assign_assign.html', context)


# ???????????????????????????
class AssignUpdate(View):
    def post(self, request):
        id = request.POST.get('id')
        # ?????????
        assigner = request.POST.get('assigner')
        # ?????????
        user_id = request.session['user']['id']
        user = User.objects.get(id=user_id)

        CustomerServe.objects.filter(pk=id).update(assigner=user,
                                                   serviceProcePeople=assigner,
                                                   assignTime=datetime.now(),
                                                   state=2,
                                                   updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': "????????????"})


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
        # ?????????/?????????
        serviceProcePeople = User.objects.get(
            id=cs.serviceProcePeople_id).username
        context = {"cs": cs, 'customer_name': customer_name,
                   'serviceProcePeople': serviceProcePeople}
        return render(request, 'serve/serve_handle_handle.html', context)

    @PermissionCheck(['303001'])
    def post(self, request):
        # ??????ID
        id = request.POST.get('id')
        # ????????????
        serviceProce = request.POST.get('serviceProce')
        CustomerServe.objects.filter(pk=id).update(state=3,
                                                   serviceProce=serviceProce,
                                                   serviceProceTime=datetime.now(),
                                                   updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': "????????????????????????"})


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
        # ?????????/?????????
        serviceProcePeople = User.objects.get(
            id=cs.serviceProcePeople_id).username
        context = {'cs': cs, 'customer_name': customer_name,
                   'serviceProcePeople': serviceProcePeople}
        return render(request, 'serve/serve_feedback_feedback.html', context)

    @PermissionCheck(['304001'])
    def post(self, request):
        # ??????ID
        id = request.POST.get('id')
        # ?????????
        myd = request.POST.get('myd')
        # ????????????
        serviceProceResult = request.POST.get('serviceProceResult')
        CustomerServe.objects.filter(pk=id).update(state=4, myd=myd,
                                                   serviceProceResult=serviceProceResult,
                                                   updateDate=datetime.now())
        return JsonResponse({'code': 200, 'msg': "??????????????????"})


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
                2: '??????????????????', 3: u'??????????????????', 4: u'??????????????????'
            }
            return JsonResponse({'code': 200, 'msg': server_type[state]})
        except:
            return JsonResponse({'code': 400, 'msg': "????????????"})
