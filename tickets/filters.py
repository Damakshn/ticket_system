import django_filters
from tickets import models


def user_departaments(request):
    if request is None:
        return models.Departament.objects.none()
    return request.user.supervised_departaments.all()

def user_supervised_executors(request):
    if request is None:
        return models.User.objects.none()
    return models.User.objects.filter(
        departaments__in=request.user.supervised_departaments.all()
    )


class TicketFilter(django_filters.FilterSet):
    """
    Стандартный фильтр для списка заявок.
    Фильтрует по создателю заявки и приоритету.
    """
    creator = django_filters.ModelChoiceFilter(queryset=models.User.objects.all())
    priority = django_filters.ChoiceFilter(choices= models.Ticket.priority.field.choices)

    class Meta:
        model = models.Ticket
        fields = ["creator", "priority"]


class ExecutorTicketFilter(TicketFilter):
    """
    Фильтр заявок для исполнителя.
    """
    
    class Meta:
        model = models.Ticket
        fields = ["creator", "priority"]


class SupervisorTicketFilter(TicketFilter):
    """
    Фильтр списка заявок для руководителя.
    По умолчанию показывает следующие заявки: новые, в работе, отложенные, выполненные
    """
    departament = django_filters.ModelChoiceFilter(queryset=user_departaments)
    status = django_filters.MultipleChoiceFilter(choices= models.Ticket.status.field.choices)
    executor = django_filters.ModelMultipleChoiceFilter(queryset=user_supervised_executors)
    
    def __init__(self, data, *args, **kwargs):
        if data is not None:
            data = data.copy()
            data.setlistdefault(
                "status",
                [
                    models.Ticket.STATUS_NEW,
                    models.Ticket.STATUS_IN_WORK,
                    models.Ticket.STATUS_DELAYED,
                    models.Ticket.STATUS_DONE
                ]
            )
        super().__init__(data, *args, **kwargs)
    

    class Meta:
        model = models.Ticket
        fields = ["departament", "creator", "status", "priority", "executor"]
