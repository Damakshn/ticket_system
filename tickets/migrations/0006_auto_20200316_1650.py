# Generated by Django 3.0.3 on 2020-03-16 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0005_auto_20200316_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='attachments',
            field=models.ManyToManyField(blank=True, null=True, to='tickets.Attachment'),
        ),
    ]
