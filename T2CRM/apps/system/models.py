from django.db import models
from datetime import datetime

# Create your models here.
from django.contrib.auth.models import AbstractUser


class ModelManager(models.Manager):
    def get_queryset(self):
        return super(ModelManager, self).get_queryset().filter(isValid=1)


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


# 权限资源表
class Module(models.Model):
    # 资源名称
    moduleName = models.CharField(max_length=64, db_column='module_name',
                                  help_text=u'权限名称')
    # 权限样式
    moduleStyle = models.CharField(max_length=128, db_column='module_style',
                                   help_text=u'样式', null=True)
    # 跳转url
    url = models.CharField(max_length=120, db_column='url', null=True)
    # 自关联
    parent = models.ForeignKey('self', db_column='parent_id',
                               db_constraint=False, on_delete=models.DO_NOTHING,
                               default=-1)
    # 父级操作值
    parentOptValue = models.CharField(max_length=64,
                                      db_column='parent_opt_value',
                                      help_text=u'父级操作值', null=True)
    # 级别
    grade = models.IntegerField(db_column='grade')
    # 操作值
    optValue = models.CharField(max_length=20, db_column='opt_value')
    # 排序
    orders = models.IntegerField(db_column='orders', help_text=u'排序', null=True)
    # 是否可用
    isValid = models.IntegerField(db_column='is_valid', help_text=u'是否可用',
                                  default=1)
    createDate = models.DateTimeField(db_column='create_date',
                                      auto_now_add=True, null=True)
    updateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True, max_length=64,
                                      null=True)
    objects = ModelManager()

    class Meta:
        db_table = 't2_module'


class Role(models.Model):
    RoleName = models.CharField(max_length=24, db_column='role_name',
                                help_text=u'角色名称')
    RoleRemark = models.CharField(max_length=64, db_column='role_remark',
                                  help_text=u'角色名称')
    CreateDate = models.DateTimeField(db_column='create_date',
                                      help_text=u'创建时间', auto_now_add=True,
                                      null=True)
    UpdateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True, null=True)
    # 是否可用
    isValid = models.IntegerField(db_column='is_valid', help_text=u'是否可用',
                                  default=1)
    objects = ModelManager()

    class Meta:
        db_table = 't2_role'


class RolePermission(models.Model):
    RoleId = models.ForeignKey(Role, on_delete=models.DO_NOTHING,
                               db_column='role_id')
    ModuleId = models.ForeignKey(Module, on_delete=models.DO_NOTHING,
                                 db_column='module_id')
    AclValue = models.CharField(max_length=64, null=True)
    CreateDate = models.DateTimeField(db_column='create_date',
                                      help_text=u'创建时间', auto_now_add=True,
                                      null=True)
    UpdateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True, null=True)
    # 是否可用
    isValid = models.IntegerField(db_column='is_valid', help_text=u'是否可用',
                                  default=1)
    objects = ModelManager()

    class Meta:
        db_table = 't2_role_permission'


class UserRole(models.Model):
    UserId = models.ForeignKey(User, on_delete=models.DO_NOTHING,
                               db_column='user_id')
    RoleId = models.ForeignKey(Role, on_delete=models.DO_NOTHING,
                               db_column='role_id')
    CreateDate = models.DateTimeField(db_column='create_date',
                                      help_text=u'创建时间', auto_now_add=True,
                                      null=True)
    UpdateDate = models.DateTimeField(db_column='update_date',
                                      auto_now_add=True, null=True)
    # 是否可用
    isValid = models.IntegerField(db_column='is_valid', help_text=u'是否可用',
                                  default=1)
    objects = ModelManager()

    class Meta:
        db_table = 't2_user_role'
