# Generated by Django 3.0.3 on 2020-03-18 04:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tickets', '0008_auto_20200317_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='departament',
            name='employees',
            field=models.ManyToManyField(blank=True, related_name='departaments', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудники'),
        ),
        migrations.AlterField(
            model_name='departament',
            name='supervisors',
            field=models.ManyToManyField(blank=True, related_name='supervised_departaments', to=settings.AUTH_USER_MODEL, verbose_name='Руководители'),
        ),
    ]
