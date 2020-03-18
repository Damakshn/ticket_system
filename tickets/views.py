from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from . import forms
from . import models

COMMON_TEMPLATE_NAME_SUFFIX = '_create_form'

# Create your views here.
def index(request):
    return render(request, 'index.html')


class CreateTicketView(LoginRequiredMixin, CreateView):
    template_name_suffix = COMMON_TEMPLATE_NAME_SUFFIX
    form_class = forms.TicketForm
    model = models.Ticket

    def form_valid(self, form):
        """
        При создании заявки устанавливает текущего пользователя как её создателя.
        """
        new_ticket = form.save(commit=False)
        new_ticket.creator = self.request.user
        new_ticket.save()
        return HttpResponseRedirect(self.get_success_url())


class TicketList(LoginRequiredMixin, ListView):
    model = models.Ticket


class InboxTickets(TicketList):

    def get_queryset(self):
        return self.model.objects.filter(executor=self.request.user)


class OutboxTickets(TicketList):

    def get_queryset(self):
        return self.model.objects.filter(creator=self.request.user)


class DepartamentSupervision(TicketList):

   def get_queryset(self):
        return self.model.objects.filter(departament__in=self.request.user.supervised_departaments.all())


class TicketDetail(LoginRequiredMixin, DetailView):
    model = models.Ticket

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = (self.object.departament in self.request.user.supervised_departaments.all())

        available_actions = {
            "can_assign_executor": (
                models.TicketStatuses.NEW,
            ),
            "can_deny": (
                models.TicketStatuses.NEW,
                models.TicketStatuses.IN_WORK,
                models.TicketStatuses.DELAYED
            ),
            "can_delay": (
                models.TicketStatuses.NEW,
                models.TicketStatuses.IN_WORK
            ),
            "can_refresh": (
                models.TicketStatuses.DENIED,
            ),
            "can_set_done": (
                models.TicketStatuses.IN_WORK,
            ),
        }
        for action in available_actions:
            context[action] = self.object.status in available_actions[action]
        if context["can_manage"]:
            context["executor_assignment_form"] = forms.ExecutorAssignmentForm(queryset=self.object.departament.employees.all())
        return context
