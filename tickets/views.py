from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from . import forms
from . import models

COMMON_TEMPLATE_NAME_SUFFIX = "_create_form"

# Create your views here.
def index(request):
    return render(request, "index.html")


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
                models.TicketStatuses.IN_WORK,
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
                models.TicketStatuses.DELAYED,
                models.TicketStatuses.DENIED,
                models.TicketStatuses.COMPLETE
            ),
            "can_set_complete": (
                models.TicketStatuses.IN_WORK,
            ),
        }
        for action in available_actions:
            context[action] = self.object.status in available_actions[action]

        if not context["can_manage"]:
            return context

        if context["can_assign_executor"]:
            executor_form = forms.ExecutorAssignmentForm(queryset=self.object.departament.employees.all())
            executor_form.helper.form_action = reverse("ticket-assign", kwargs={"pk": self.object.id})
            context["executor_assignment_form"] = executor_form
        
        if context["can_delay"]:
            delay_form = forms.DelayTicketForm()
            delay_form.helper.form_action = reverse("ticket-delay", kwargs={"pk": self.object.id})
            context["delay_form"] = delay_form
        
        if context["can_deny"]:
            deny_form = forms.DenyTicketForm()
            deny_form.helper.form_action = reverse("ticket-deny", kwargs={"pk": self.object.id})
            context["deny_form"] = deny_form
        
        if context["can_refresh"]:
            refresh_form = forms.RefreshTicketForm()
            refresh_form.helper.form_action = reverse("ticket-refresh", kwargs={"pk": self.object.id})
            context["refresh_form"] = refresh_form

        if context["can_set_complete"]:
            complete_form = forms.CompleteTicketForm()
            complete_form.helper.form_action = reverse("ticket-set-complete", kwargs={"pk": self.object.id})
            context["complete_form"] = complete_form

        return context


class TicketManagementView(LoginRequiredMixin, View):

    def get_updates(self):
        url = self.request.get_full_path()
        action = url[url.rfind("/"):]
        status_map = {
            "/refresh": models.TicketStatuses.NEW,
            "/delay": models.TicketStatuses.DELAYED,
            "/deny": models.TicketStatuses.DENIED,
            "/assign": models.TicketStatuses.IN_WORK,
            "/done": models.TicketStatuses.DONE,
        }
        new_status = status_map.get(action)
        return {"status": new_status}

    def get_ticket(self):
        # ToDo url tampering?
        ticket_id = self.kwargs["pk"]
        # ToDo exception if ticket does not exist
        return models.Ticket.objects.get(id=ticket_id)
    
    def calculate_redirect_url(self):
        return "/index"

    def update_ticket(self, updates):
        for field in updates:
            setattr(self.ticket, field, updates[field])
        self.ticket.save()
    
    def post(self, request, *args, **kwargs):
        self.ticket = self.get_ticket()
        updates = self.get_updates()
        if updates:
            self.update_ticket(updates)
            pass
        redirect_url = self.calculate_redirect_url()
        return HttpResponseRedirect(redirect_url)

class AssignExecutorView(TicketManagementView):

    def get_updates(self):
        updates = super().get_updates()
        form = forms.ExecutorAssignmentForm(self.request.POST)
        if form.is_valid():
            updates["executor"] = form.cleaned_data["executor"]
        return updates


