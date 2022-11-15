from django.db import models
from customer.models import Customer
from system.models import User


class ModelManager(models.Manager):

    def get_queryset(self):
        return super(ModelManager, self).get_queryset().filter(isValid=1,
                                                               deleted=0)


# 服务模型
class CustomerServe(models.Model):
    # 服务类型 6 咨询 / 7 建议 / 8 投诉
    serveType = models.IntegerField(db_column='serve_type', help_text='服务类型')
    # 客户咨询描述
    overview = models.CharField(db_column='overview', max_length=500,
                                help_text='咨询描述')
    # 客户
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING,
                                 help_text=u'客户信息')
    # 1 新创建 / 2 已分配 / 3 已处理 / 4 已反馈
    state = models.IntegerField(db_column='state', help_text='服务状态')
    # 服务请求
    serviceRequest = models.CharField(db_column='service_request',
                                      max_length=500)
    # 创建人
    createPeople = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                     help_text=u'创建人', related_name='CUser')
    # 分配人
    assigner = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                                 help_text=u'分配人', related_name='ASUser',
                                 null=True)
    # 分配日期
    assignTime = models.DateTimeField(db_column='assign_time', null=True)
    # 服务处理
    serviceProce = models.CharField(db_column='service_proce', max_length=500,
                                    null=True)
    # 服务处理人
    serviceProcePeople = models.CharField(db_column='service_proce_people',
                                          max_length=50, null=True)
    # 服务处理日期
    serviceProceTime = models.DateTimeField(db_column='service_proce_time',
                                            null=True)
    # 服务处理结果
    serviceProceResult = models.CharField(db_column='service_proce_result',
                                          max_length=500, null=True)

    # 客户满意度
    myd = models.CharField(db_column='myd', max_length=50, null=True)
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True, null=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True, null=True)
    DELETE_CHOICE = (
        (0, u'未删除'),
        (1, u'已删除')
    )
    deleted = models.IntegerField(default=0, choices=DELETE_CHOICE,
                                  help_text=u'是否删除')
    objects = ModelManager()

    class Meta:
        db_table = 't2_customer_serve'
        verbose_name = u'工作流表'
        verbose_name_plural = verbose_name
