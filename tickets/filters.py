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
    title = django_filters.CharFilter(lookup_expr='icontains')
    creator = django_filters.ModelChoiceFilter(queryset=models.User.objects.all())
    priority = django_filters.ChoiceFilter(choices= models.Ticket.priority.field.choices)
    description = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = models.Ticket
        fields = ["title", "creator", "priority", "description"]

class ExecutorTicketFilter(TicketFilter):
    
    class Meta:
        model = models.Ticket
        fields = ["title", "creator", "priority", "description"]

class SupervisorTicketFilter(TicketFilter):
    departament = django_filters.ModelChoiceFilter(queryset=user_departaments)
    status = django_filters.ChoiceFilter(choices= models.Ticket.status.field.choices)
    executor = django_filters.ModelMultipleChoiceFilter(queryset=user_supervised_executors)

    class Meta:
        model = models.Ticket
        fields = ["title", "departament", "creator", "status", "priority", "description", "executor"]


