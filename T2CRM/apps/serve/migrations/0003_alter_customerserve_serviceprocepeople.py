# Generated by Django 3.2 on 2022-11-19 17:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
        ('serve', '0002_auto_20221114_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customerserve',
            name='serviceProcePeople',
            field=models.ForeignKey(help_text='分配人', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ASPro', to='system.user'),
        ),
    ]
