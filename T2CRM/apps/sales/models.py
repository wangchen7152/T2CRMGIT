from django.db import models
from datetime import datetime


class ModelManager(models.Manager):

    def get_queryset(self):
        return super(ModelManager, self).get_queryset().filter(isValid=1,
                                                               deleted=0)


# 营销机会模型
class SaleChance(models.Model):
    # 信息来源
    chanceSource = models.CharField(max_length=300, db_column='chance_source',
                                    help_text=u'信息来源')
    # 客户id
    customerId = models.IntegerField(db_column='customer_id', help_text=u'客户id')
    # 客户名称
    customerName = models.CharField(max_length=100, db_column='customer_name',
                                    help_text=u'客户名称')
    # 成功几率
    cgjl = models.IntegerField(db_column='cgjl', help_text=u'成功机率', null=True)
    # 概要
    overview = models.CharField(max_length=300, db_column='overview',
                                help_text=u'概要', null=True)
    # 联系人
    linkMan = models.CharField(max_length=20, db_column='link_man',
                               help_text=u'联系人')
    # 联系电话
    linkPhone = models.CharField(max_length=20, db_column='link_phone',
                                 help_text=u'联系电话')
    # 描述
    description = models.CharField(max_length=1000, db_column='description',
                                   help_text=u'描述')
    # 创建人
    createMan = models.CharField(max_length=20, db_column='create_man',
                                 help_text=u'创建人')
    # 分配给谁
    assignMan = models.CharField(max_length=20, db_column='assign_man',
                                 help_text=u'分配给谁', null=True)
    # 分配时间
    assignTime = models.DateTimeField(db_column='assign_time',
                                      help_text=u'分配时间', null=True)
    # 状态：1-如果有分配就是已分配状态，0-未分配
    state = models.CharField(max_length=20, db_column='state',
                             help_text=u'状态', null=True)
    # 开发状态：0=未开发 1=开发中 2=开完完成 3=开发失败
    devResult = models.CharField(max_length=20, db_column='dev_result',
                                 help_text=u'开发状态', null=True)

    isValid = models.IntegerField(db_column='is_valid', default=1, null=True)
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True,
                                      help_text=u'创建时间', null=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',
                                      help_text=u'更新时间', null=True)
    DELETE_CHOICE = (
        (0, u'未删除'),
        (1, u'已删除')
    )
    deleted = models.IntegerField(default=0, choices=DELETE_CHOICE,
                                  help_text=u'是否删除')

    objects = ModelManager()

    class Meta:
        db_table = 't2_sale_chance'
        verbose_name = u'营销客户'
        verbose_name_plural = verbose_name


# 客户计划模型
class CusDevPlan(models.Model):
    # 关联营销机会
    saleChance = models.ForeignKey(SaleChance, db_constraint=False,
                                   db_column='sale_chance_id',
                                   on_delete=models.DO_NOTHING,
                                   help_text=u'关联营销机会')
    # 计划内容
    planItem = models.CharField(max_length=300, db_column='plan_item',
                                help_text=u'执行内容')
    # 计划时间
    planDate = models.DateTimeField(max_length=20, db_column='plan_date',
                                    help_text=u'执行时间', auto_now_add=True)
    # 执行效果
    exeAffect = models.CharField(max_length=100, db_column='exe_affect',
                                 help_text=u'执行效果')
    isValid = models.IntegerField(db_column='is_valid')
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True, null=True,
                                      help_text=u'创建时间')
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',
                                      default=datetime.now, null=True,
                                      help_text=u'更新时间')
    DELETE_CHOICE = (
        (0, u'未删除'),
        (1, u'已删除')
    )
    deleted = models.IntegerField(default=0, choices=DELETE_CHOICE,
                                  help_text=u'是否删除')

    objects = ModelManager()

    class Meta:
        db_table = 't2_sale_plan'
        verbose_name = u'客户营销计划'
        verbose_name_plural = verbose_name
