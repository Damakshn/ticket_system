# Generated by Django 3.0.5 on 2020-05-24 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0012_auto_20200509_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='status',
            field=models.IntegerField(choices=[(0, 'Новая'), (1, 'Отложена'), (2, 'Отклонена'), (3, 'В работе'), (4, 'Контроль'), (5, 'Завершена'), (6, 'Отменена пользователем')], default=0, verbose_name='Статус'),
        ),
    ]
