from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from enum import IntEnum


class TicketStatuses(IntEnum):
    NEW = 0
    DELAYED = 1
    DENIED = 2
    IN_WORK = 3
    DONE = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Departament(models.Model):
    name = models.CharField(
        verbose_name='Название подразделения',
        max_length=200
    )

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Логин'
    )
    is_executor = models.BooleanField(
        verbose_name='Является исполнителем',
        default=False
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Фамилия'
    )
    departament = models.ForeignKey(
        Departament,
        blank=True,
        null=True,
        verbose_name='Подразделение',
        on_delete=models.PROTECT
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name='Срок'
    )

    def  __str__(self):
        if (self.first_name or self.last_name):
            return (f'{self.last_name} {self.first_name}').rstrip()
        else:
            return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

class Attachment(models.Model):
    name = models.CharField(verbose_name='Имя вложения', max_length=100)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    date_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    title = models.CharField(verbose_name='Заголовок', max_length=300)
    description = models.TextField(verbose_name='Описание проблемы')
    creator = models.ForeignKey(
        UserProfile,
        related_name='created_tickets',
        on_delete=models.PROTECT,
        verbose_name='Автор'
    )
    executor = models.ForeignKey(
        UserProfile,
        related_name='tickets_in_work',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Исполнитель'
    )
    status = models.IntegerField(
        choices=TicketStatuses.choices(),
        default=TicketStatuses.NEW,
        verbose_name='Статус'
    )
    attachments = models.ManyToManyField(Attachment)

    def __str__(self):
        return self.title

class Supervision(models.Model):
    departament = models.OneToOneField(Departament, primary_key=True, on_delete=models.CASCADE)
    supervisors = models.ManyToManyField(UserProfile)

    def __str__(self):
        return f'Руководители {self.departament.name}'
