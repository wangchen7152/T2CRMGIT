from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import ServeIndex, ServeList, ServeAssign, CreateWorkflow, \
    DelWorkflow, AssignWorkflow, AssignUpdate

app_name = 'serve'
urlpatterns = [
    # 进入服务创建页面
    url(r'^ServeIndex/', csrf_exempt(ServeIndex.as_view()), name='ServeIndex'),
    # 查询创建的服务列表
    url(r'^ServeList/', csrf_exempt(ServeList.as_view()), name='ServeList'),
    # 查询服务分配的列表列表
    url(r'^ServeAssign/', csrf_exempt(ServeAssign.as_view()),
        name='ServeAssign'),
    # 创建服务接口
    url(r'^CreateWorkflow/', csrf_exempt(CreateWorkflow.as_view()),
        name='CreateWorkflow'),
    # 创建服务接口
    url(r'^DelWorkflow/', csrf_exempt(DelWorkflow.as_view()),
        name='DelWorkflow'),
    # 进入服务分配接口
    url(r'^AssignWorkflow/', csrf_exempt(AssignWorkflow.as_view()),
        name='AssignWorkflow'),
    # 服务分配创接口
    url(r'^AssignUpdate/', csrf_exempt(AssignUpdate.as_view()),
        name='AssignUpdate'),
]
