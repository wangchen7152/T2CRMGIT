from django.db import models
from datetime import datetime


class ModelManager(models.Manager):

    def get_queryset(self):
        return super(ModelManager, self).get_queryset().filter(isValid=1,
                                                               deleted=0)


class Province(models.Model):
    # 主键
    id = models.AutoField(primary_key=True)
    # 城市
    city_name = models.CharField(max_length=64, verbose_name=u'省份名称')

    class Meta:
        db_table = 't2_province'
        verbose_name = u'客户信息表'
        verbose_name_plural = verbose_name


class CityCourse(models.Model):
    # 主键
    id = models.AutoField(primary_key=True)
    # 城市
    city_name = models.CharField(max_length=64, verbose_name=u'城市名称')
    # 外键
    city_province = models.ForeignKey(Province, db_column='city_province_id',
                                      on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 't2_city_customer'
        verbose_name = u'客户信息表'
        verbose_name_plural = verbose_name

    def get_course_list(self):
        # 获取当前城市下所有的客户
        return self.customer_set.all()


class Customer(models.Model):
    # 主键
    id = models.AutoField(primary_key=True)
    # 客户所属城市
    city = models.ForeignKey(CityCourse, db_column='city_id',
                             on_delete=models.DO_NOTHING, verbose_name=u'所属城市')
    # 客户编号 KH + 日
    khno = models.CharField(max_length=20, unique=True, verbose_name=u'客户编号')
    # 客户名称
    name = models.CharField(max_length=128, verbose_name=u'客户名称')
    # 客户所在地区
    area = models.CharField(max_length=128, verbose_name='所在地区')
    # 客户经理
    cusManager = models.CharField(max_length=128, db_column='cus_manager')
    # 客户等级
    level = models.CharField(max_length=128, verbose_name=u'客户级别')
    # 满意度
    myd = models.CharField(max_length=128, verbose_name=u'客户满意度')
    # 信用度
    xyd = models.CharField(max_length=128, verbose_name=u'信用度')
    # 地址
    address = models.CharField(max_length=128, verbose_name=u'地址')
    # 邮编
    postCode = models.CharField(max_length=128, db_column='post_code')
    # 联系电话
    phone = models.CharField(max_length=128)
    # 传真
    fax = models.CharField(max_length=128)
    # 网址
    web_url = models.CharField(max_length=128, db_column='web_url')
    # 营业注册号
    company_num = models.CharField(max_length=128, verbose_name=u'营业注册号')
    # 法人
    leader_of_company = models.CharField(max_length=128, verbose_name=u'法人')
    # 注册资金
    registered_capital = models.CharField(max_length=128, verbose_name=u'注册资本')
    # 年营业额
    annual_turnover = models.CharField(max_length=128, verbose_name='年营业额')
    # 开户银行
    bank = models.CharField(max_length=128, verbose_name=u'开户银行')
    # 开户账号
    bank_number = models.CharField(max_length=128, verbose_name=u'开户账号')
    # 地税
    land_tax = models.CharField(max_length=128, verbose_name=u'地税')
    # 国税
    the_irs = models.CharField(max_length=128, verbose_name=u'国税')
    # 状态 0=正常 1=暂时流失 2=真正流失
    state = models.IntegerField(default=0)
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True)
    # 是否删除，0为未删除,1为已删除
    deleted = models.IntegerField(default=0, choices=((0, '未删除'), (1, '已删除')),
                                  verbose_name=u'是否删除', null=True)

    all = models.Manager()
    objects = ModelManager()

    class Meta:
        db_table = 't2_customer'
        verbose_name = u'客户信息表'
        verbose_name_plural = verbose_name


# 客户联系人
class LinkMan(models.Model):
    # 客户id，外键
    cusId = models.IntegerField(db_column='cus_id')
    linkName = models.CharField(max_length=20, db_column='link_name')
    sex = models.CharField(max_length=4)
    zhiwei = models.CharField(max_length=20, db_column='zhiwei')
    officePhone = models.CharField(max_length=20, db_column='office_phone')
    phone = models.CharField(max_length=20, db_column='phone')

    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',
                                      default=datetime.now)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True)
    # 是否删除，0为未删除,1为已删除
    deleted = models.IntegerField(default=0, choices=((0, '未删除'), (1, '已删除')),
                                  verbose_name=u'是否删除', null=True)

    objects = ModelManager()

    class Meta:
        db_table = 't2_customer_linkman'
        verbose_name = u'客户联系人表'
        verbose_name_plural = verbose_name


# 客户订单
class CustomerOrders(models.Model):
    # 关联的客户
    customer = models.ForeignKey(Customer, db_column='cus_id',
                                 on_delete=models.DO_NOTHING)
    # 订单编号
    orderNo = models.CharField(db_column='order_no', max_length=64)
    # 下单日期
    orderDate = models.DateTimeField(db_column='order_date', auto_now_add=True)
    # 收货地址
    address = models.CharField(max_length=120, db_column='address')
    # 订单总金额
    totalPrice = models.FloatField(db_column='total_price')
    # 0=未回款 1=已回款
    state = models.IntegerField(verbose_name=u'是否回款', choices=((0, '未回款'),
                                                               (1, '已回款')))
    isValid = models.IntegerField(db_column='is_valid')
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True)
    # 是否删除，0为未删除,1为已删除
    deleted = models.IntegerField(default=0, choices=((0, '未删除'), (1, '已删除')),
                                  verbose_name=u'是否删除', null=True)

    objects = ModelManager()

    class Meta:
        db_table = 't2_customer_order'
        verbose_name = u'客户订单'
        verbose_name_plural = verbose_name


# 订单详情表
class OrdersDetail(models.Model):
    # 关联订单
    order = models.ForeignKey(CustomerOrders, db_column='order_id',
                              on_delete=models.DO_NOTHING)
    # 商品名称
    goodsName = models.CharField(max_length=100, db_column='goods_name')
    # 商品数量
    goodsNum = models.IntegerField(db_column='goods_num')
    # 单位
    unit = models.CharField(max_length=10, db_column='unit')
    # 单价
    price = models.FloatField(db_column='price')
    # 总价
    sum = models.FloatField(db_column='sum')

    isValid = models.IntegerField(db_column='is_valid')
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True)
    # 是否删除，0为未删除,1为已删除
    deleted = models.IntegerField(default=0, choices=((0, '未删除'), (1, '已删除')),
                                  verbose_name=u'是否删除', null=True)

    objects = ModelManager()

    class Meta:
        db_table = 't2_order_details'
        verbose_name = u'客户订单详情表'
        verbose_name_plural = verbose_name


# 客户流失表
class CustomerLoss(models.Model):
    # 客户编号
    cusNo = models.CharField(max_length=40, db_column='cus_no')
    # 客户名称
    cusName = models.CharField(max_length=20, db_column='cus_name')
    # 客户经理
    cusManager = models.CharField(max_length=20, db_column='cus_manager')
    # 上次下单日期
    lastOrderTime = models.DateTimeField(db_column='last_order_time')
    # 确认流失日期
    confirmLossTime = models.DateTimeField(db_column='confirm_loss_time')
    # 状态 0=暂缓流失 1=确认流失
    state = models.IntegerField()
    # 流失原因
    lossReason = models.CharField(max_length=1000, db_column='loss_reason')

    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True)
    # 是否删除，0为未删除,1为已删除
    deleted = models.IntegerField(default=0, choices=((0, '未删除'), (1, '已删除')),
                                  verbose_name=u'是否删除', null=True)
    objects = ModelManager()

    class Meta:
        db_table = 't2_customer_loss'
        verbose_name = u'客户流失情况表'
        verbose_name_plural = verbose_name


# 流失暂缓措施
class CustomerReprieve(models.Model):
    customerLoss = models.ForeignKey(CustomerLoss, db_column='loss_id',
                                     db_constraint=False,
                                     on_delete=models.DO_NOTHING)
    # 采取措施
    measure = models.CharField(max_length=1000, db_column='measure')

    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True)
    # 是否删除，0为未删除,1为已删除
    deleted = models.IntegerField(default=0, choices=((0, '未删除'), (1, '已删除')),
                                  verbose_name=u'是否删除', null=True)

    objects = ModelManager()

    class Meta:
        db_table = 't2_customer_reprieve'
        verbose_name = u'客户六十暂缓措施表'
        verbose_name_plural = verbose_name
