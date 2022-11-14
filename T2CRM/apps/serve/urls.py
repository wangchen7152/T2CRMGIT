from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import ServeIndex, ServeList

app_name = 'serve'
urlpatterns = [
    # 进入服务创建页面
    url(r'^ServeIndex/', csrf_exempt(ServeIndex.as_view()), name='ServeIndex'),
    # 查询创建的服务列表
    url(r'^ServeList/', csrf_exempt(ServeList.as_view()), name='ServeList')
]
