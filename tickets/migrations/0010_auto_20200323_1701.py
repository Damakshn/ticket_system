# Generated by Django 3.0.3 on 2020-03-23 09:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0009_auto_20200318_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='departament',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='incoming_tickets', to='tickets.Departament', verbose_name='Подразделение'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.IntegerField(choices=[(0, 'Новая'), (1, 'Отложена'), (2, 'Отклонена'), (3, 'В работе'), (4, 'Выполнена'), (5, 'Завершена')], default=0, verbose_name='Статус'),
        ),
    ]