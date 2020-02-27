from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
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
        new_ticket.creator = self.request.user.userprofile
        new_ticket.save()
        return HttpResponseRedirect(self.get_success_url())


class TicketList(LoginRequiredMixin, ListView):
    model = models.Ticket
    context_object_name = 'tickets_list'


class InboxTickets(TicketList):

    def get_queryset(self):
        # ToDo только входящие
        return self.model.objects.all()


class OutboxTickets(TicketList):

    def get_queryset(self):
        # ToDo только исходящие
        return self.model.objects.all()
