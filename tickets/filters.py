import django_filters
from tickets import models


def user_departaments(request):
    if request is None:
        return models.Departament.objects.none()
    return request.user.supervised_departaments.all()


class TicketFilter(django_filters.FilterSet):
    departament = django_filters.ModelChoiceFilter(queryset=user_departaments)
    creator = django_filters.ModelChoiceFilter(queryset=models.User.objects.all())
    status = django_filters.ChoiceFilter(choices= models.Ticket.status.field.choices)
    priority = django_filters.ChoiceFilter(choices= models.Ticket.priority.field.choices)

    class Meta:
        model = models.Ticket
        fields = ["departament", "creator", "status", "priority"]
