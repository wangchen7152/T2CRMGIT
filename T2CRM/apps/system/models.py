from django.db import models
from datetime import datetime

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, verbose_name=u'用户名')
    password = models.CharField(max_length=100, verbose_name=u'密码')
    salt = models.CharField(max_length=4, verbose_name=u'盐加密')
    truename = models.CharField(max_length=20, null=True, verbose_name=u'昵称')
    email = models.CharField(max_length=30, null=True, verbose_name=u'邮箱')
    phone = models.CharField(max_length=20, null=True, verbose_name=u'电话号码')
    state = models.IntegerField(default=0, verbose_name=u'状态')
    isValid = models.IntegerField(db_column='is_valid', default=1,
                                  verbose_name=u'是否可用')
    createDate = models.DateTimeField(db_column='create_date',
                                      default=datetime.now,
                                      verbose_name=u'创建时间')
    updateDate = models.DateTimeField(db_column='update_date', null=True,
                                      verbose_name=u'更新时间')
    company = models.CharField(max_length=24, verbose_name=u'所属公司', null=True)

    # 元信息
    class Meta:
        db_table = 'T2_user'
        verbose_name = u'用户信息'
        verbose_name_plural = verbose_name


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name=u"城市名称")
    add_time = models.DateField(datetime.now)
    des = models.CharField(max_length=200, verbose_name="u描述")

    class Meta:
        db_table = 'T2_user_city'
        verbose_name = u"城市"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name
