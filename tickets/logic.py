from django.urls import reverse
from tickets import filters, forms, models

# таблица переходов статусов заявки
# ключ - доступное пользователю действие
# значение - набор статусов, которые позволяют это действие выполнять
STATUS_TRANSITION_TABLE = {
    "can_assign_executor": (
        models.Ticket.STATUS_NEW,
        models.Ticket.STATUS_IN_WORK,
    ),
    "can_deny": (
        models.Ticket.STATUS_NEW,
        models.Ticket.STATUS_IN_WORK,
        models.Ticket.STATUS_DELAYED
    ),
    "can_delay": (
        models.Ticket.STATUS_NEW,
        models.Ticket.STATUS_IN_WORK
    ),
    "can_refresh": (
        models.Ticket.STATUS_DELAYED,
        models.Ticket.STATUS_DENIED,
        models.Ticket.STATUS_COMPLETE
    ),
    "can_set_complete": (
        models.Ticket.STATUS_IN_WORK,
    ),
}


def get_ticket_list_context(**kwargs):
    """
    Отдаёт контекст для списка заявок

    По типу списка и текущему пользователю определяет, какие колонки таблицы
    будут видны, какие заявки выведены и какую форму для фильтрации разместить
    на странице.
    """
    url_name = kwargs["url_name"]
    current_user = kwargs["current_user"]
    filterset_class = filters.TicketFilter
    column_list = ["title", "date_create", "priority", "deadline", "days_left"]
    ticket_list = models.Ticket.objects.all()

    if url_name == "inbox":
        filterset_class = filters.ExecutorTicketFilter
        column_list.append('creator')
        ticket_list = models.Ticket.objects.filter(
            executor=current_user
        ).filter(
            status=models.Ticket.STATUS_IN_WORK
        )
    elif url_name == "outbox":
        filterset_class = filters.CreatorTicketFilter
        column_list.append('status')
        ticket_list = models.Ticket.objects.filter(creator=current_user)
    elif url_name == "supervision":
        filterset_class = filters.SupervisorTicketFilter
        column_list.extend(['creator', 'status', 'executors'])
        ticket_list = models.Ticket.objects.filter(
            departament__in=current_user.supervised_departaments.all()
        )

    context = {
        "filterset_class": filterset_class,
        "column_list": column_list,
        "ticket_list": ticket_list
    }
    return context


def get_available_actions_for_ticket(**kwargs):
    current_user = kwargs["current_user"]
    ticket = kwargs["ticket"]
    actions = {}
    actions["can_manage"] = (
        ticket.departament in current_user.supervised_departaments.all()
    )
    if not actions["can_manage"]:
        return actions
    for action in STATUS_TRANSITION_TABLE:
        actions[action] = ticket.status in STATUS_TRANSITION_TABLE[action]
    return actions


def get_management_forms_for_ticket(**kwargs):
    """
    Сверяется с доступными действиями над заявкой, и отдаёт набор форм
    для управления заявкой, которые следует разместить на странице.
    """
    actions = kwargs["actions"]
    ticket = kwargs["ticket"]
    management_forms = {}

    if actions.get("can_assign_executor"):
        # ToDo должен стоять текущий исполнитель, если он есть
        executor_form = forms.ExecutorAssignmentForm(queryset=ticket.departament.employees.all())
        executor_form.helper.form_action = reverse("ticket-assign", kwargs={"pk": ticket.id})
        management_forms["executor_assignment_form"] = executor_form

    if actions.get("can_delay"):
        delay_form = forms.DelayTicketForm()
        delay_form.helper.form_action = reverse("ticket-delay", kwargs={"pk": ticket.id})
        management_forms["delay_form"] = delay_form

    if actions.get("can_deny"):
        deny_form = forms.DenyTicketForm()
        deny_form.helper.form_action = reverse("ticket-deny", kwargs={"pk": ticket.id})
        management_forms["deny_form"] = deny_form

    if actions.get("can_refresh"):
        refresh_form = forms.RefreshTicketForm()
        refresh_form.helper.form_action = reverse("ticket-refresh", kwargs={"pk": ticket.id})
        management_forms["refresh_form"] = refresh_form

    if actions.get("can_set_complete"):
        complete_form = forms.CompleteTicketForm()
        complete_form.helper.form_action = reverse("ticket-complete", kwargs={"pk": ticket.id})
        management_forms["complete_form"] = complete_form

    return management_forms


def set_ticket_done(ticket):
    ticket.status = models.Ticket.STATUS_CONTROL
    ticket.save()


def cancel_ticket(ticket):
    # ToDo создать ещё один статус - отменено пользователем
    ticket.status = models.Ticket.STATUS_COMPLETE
    ticket.save()


def refresh_ticket(ticket):
    ticket.status = models.Ticket.STATUS_NEW
    ticket.save()


def delay_ticket(ticket):
    ticket.status = models.Ticket.STATUS_DELAYED
    ticket.save()


def deny_ticket(ticket):
    ticket.status = models.Ticket.STATUS_DENIED
    ticket.save()


def assign_executor_for_ticket(ticket, executor):
    ticket.status = models.Ticket.STATUS_IN_WORK
    ticket.executor = executor
    ticket.save()


def complete_ticket(ticket):
    ticket.status = models.Ticket.STATUS_COMPLETE
    ticket.save()


def check_user_can_cancel_ticket(ticket, current_user):
    return (ticket.creator == current_user)


def check_user_can_set_ticket_done(ticket, current_user):
    return (ticket.executor == current_user)


def check_user_can_refresh_ticket(ticket, current_user):
    return (
        ticket.creator == current_user
        or ticket.departament in current_user.supervised_departaments.all()
    )


def check_user_can_manage_ticket(ticket, current_user):
    return (ticket.departament in current_user.supervised_departaments.all())
