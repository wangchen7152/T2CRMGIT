# Generated by Django 3.2 on 2022-11-12 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_alter_linkman_sex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linkman',
            name='officePhone',
            field=models.CharField(db_column='office_phone', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='linkman',
            name='zhiwei',
            field=models.CharField(db_column='zhiwei', max_length=20, null=True),
        ),
    ]
