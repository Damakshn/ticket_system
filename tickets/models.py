from datetime import datetime
from enum import IntEnum
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from . import helpers


class TicketStatuses(IntEnum):
    NEW = 0
    DELAYED = 1
    DENIED = 2
    IN_WORK = 3
    DONE = 4
    COMPLETE = 5

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Departament(models.Model):
    name = models.CharField(
        verbose_name="Название подразделения",
        max_length=200
    )
    supervisors = models.ManyToManyField(
        User,
        verbose_name="Руководители",
        related_name="supervised_departaments",
        blank=True
    )
    employees = models.ManyToManyField(
        User,
        verbose_name="Сотрудники",
        related_name="departaments",
        blank=True
    )

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Логин"
    )
    is_executor = models.BooleanField(
        verbose_name="Является исполнителем",
        default=False
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Фамилия"
    )
    departament = models.ForeignKey(
        Departament,
        blank=True,
        null=True,
        verbose_name="Подразделение",
        on_delete=models.PROTECT
    )

    def  __str__(self):
        if (self.first_name or self.last_name):
            return (f"{self.last_name} {self.first_name}").rstrip()
        else:
            return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()

class Attachment(models.Model):
    name = models.CharField(verbose_name="Имя вложения", max_length=100)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    STATUS_NEW = 0
    STATUS_DELAYED = 1
    STATUS_DENIED = 2
    STATUS_IN_WORK = 3
    STATUS_CONTROL = 4
    STATUS_COMPLETE = 5

    ORDINARY = 100
    MEDIUM = 200
    HIGH = 300
    URGENT = 400
    CRITICAL = 500

    date_create = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    departament = models.ForeignKey(
        Departament,
        related_name="incoming_tickets",
        on_delete=models.PROTECT,
        verbose_name="Подразделение",
        blank=False
    )
    title = models.CharField(verbose_name="Заголовок", max_length=300)
    description = models.TextField(verbose_name="Описание проблемы")
    creator = models.ForeignKey(
        User,
        related_name="created_tickets",
        on_delete=models.PROTECT,
        verbose_name="От кого"
    )
    executor = models.ForeignKey(
        User,
        related_name="tickets_in_work",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Исполнитель"
    )
    status = models.IntegerField(
        choices=[
            (STATUS_NEW, "Новая"),
            (STATUS_DELAYED, "Отложена"),
            (STATUS_DENIED, "Отклонена"),
            (STATUS_IN_WORK, "В работе"),
            (STATUS_CONTROL, "Контроль"),
            (STATUS_COMPLETE,"Завершена"),
        ],
        default=STATUS_NEW,
        verbose_name="Статус"
    )
    attachments = models.ManyToManyField(Attachment, blank=True)
    deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name="Срок"
    )
    priority = models.PositiveIntegerField(
        choices=[
            (ORDINARY, "Обычный"),
            (MEDIUM, "Средний"),
            (HIGH, "Высокий"),
            (URGENT, "Срочный"),
            (CRITICAL, "Критический"),
        ],
        blank=True,
        default=ORDINARY,
        verbose_name="Приоритет"
    )

    @property
    def status_text(self):
        return [item for item in Ticket.status.field.choices if item[0] == self.status][0][1]

    @property
    def priority_text(self):
        return [item for item in Ticket.priority.field.choices if item[0] == self.priority][0][1]

    @property
    def days_left(self):
        """
        Количество дней до истечения срока.
        Если заявка отклонена или выполнена, то дедлайн не имеет значения;
        Если срок не указан, вернёт None, если заявка просрочена,
        то вернёт отрицательное число.
        """
        if self.status in (Ticket.STATUS_DENIED, Ticket.STATUS_COMPLETE):
            return None
        if self.deadline is None:
            return None
        return (self.deadline - datetime.now().date()).days

    @property
    def verbose_deadline_status(self):
        """
        Возвращает словесное описание статуса заявки по срокам исполнения
        """
        if self.days_left is None:
            return ""
        if self.days_left > 0:
            days_between = self.days_left - 1
            if days_between == 0:
                return "Остался последний день"
            # склоняем слова "Осталось" и "дней"
            days_reminder = days_between % 10
            left_plural = "Остался" if days_reminder == 1 else "Осталось"
            days_plural_declension = {
                (1,): "день",
                (2, 3, 4,): "дня",
                (5, 6, 7, 8, 9, 0): "дней"
            }
            days_plural = ""
            for remainders in days_plural_declension:
                if days_reminder in remainders:
                    days_plural = days_plural_declension[remainders]
                    break
            # ------------------------------------------------------
            return f"{left_plural} {days_between} {days_plural}"
        elif self.days_left == 0:
            return "Крайний срок"
        else:
            formatted_deadline = datetime.strftime(self.deadline, helpers.RUSSIAN_DATE_FORMAT)
            return f"Просрочено с {formatted_deadline}"

    @property
    def deadline_css(self):
        """
        Класс CSS для отображения дедлайна
        """
        if self.days_left is None:
            return ""
        if  self.days_left > 1:
            return "ticket_deadline_ok"
        elif self.days_left == 1:
            return "ticket_deadline_last_day"
        elif self.days_left == 0:
            return "ticket_deadline_critical"
        else:
            return "ticket_deadline_expired"

    @property
    def status_css(self):
        """
        Класс CSS для отображения статуса
        """
        status_classes = {
            Ticket.STATUS_NEW: "ticket_status_new",
            Ticket.STATUS_DELAYED: "ticket_status_delayed",
            Ticket.STATUS_DENIED: "ticket_status_denied",
            Ticket.STATUS_IN_WORK: "ticket_status_in_work",
            Ticket.STATUS_CONTROL: "ticket_status_done",
            Ticket.STATUS_COMPLETE: "ticket_status_complete",
        }
        return status_classes[self.status]

    @property
    def priority_css(self):
        """
        Класс CSS для отображения приоритета
        """
        priority_classes = {
            Ticket.ORDINARY: "ticket_priority_ordinary",
            Ticket.MEDIUM: "ticket_priority_medium",
            Ticket.HIGH: "ticket_priority_high",
            Ticket.URGENT: "ticket_priority_urgent",
            Ticket.CRITICAL: "ticket_priority_critical",
        }
        return priority_classes[self.priority]

    def get_absolute_url(self):
        return reverse("ticket-detail", args=[str(self.id)])

    def __str__(self):
        return self.title
