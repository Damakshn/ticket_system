from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views import View
from tickets import forms, logic, models


def index(request):
    return render(request, "index.html")


class CreateTicketView(LoginRequiredMixin, CreateView):
    template_name_suffix = "_create_form"
    form_class = forms.TicketCreateForm
    model = models.Ticket

    def form_valid(self, form):
        """
        При создании заявки устанавливает текущего пользователя как её создателя.
        """
        new_ticket = form.save(commit=False)
        new_ticket.creator = self.request.user
        new_ticket.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("index")


class TicketList(LoginRequiredMixin, View):
    template_name = "tickets/ticket_list.html"

    def get(self, request):
        url_name = resolve(self.request.path_info).url_name
        context = logic.get_ticket_list_context(url_name=url_name, current_user=request.user)
        filterset_class, column_list, queryset = context.values()
        filterset = filterset_class(self.request.GET, request=self.request, queryset=queryset)
        template_context = {
            "ticket_list": filterset.qs,
            "column_list": column_list,
            "filterset": filterset
        }
        return render(request, self.template_name, template_context)


class TicketDetail(LoginRequiredMixin, DetailView):
    model = models.Ticket

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        actions = logic.get_available_actions_for_ticket(ticket=self.object, current_user=self.request.user)
        forms = logic.get_management_forms_for_ticket(ticket=self.object, actions=actions)
        context["actions"] = actions
        context["has_actions"] = any(actions.values())
        context.update(forms)
        return context


class TicketChangeView(LoginRequiredMixin, View):

    def get_changed_ticket(self):
        ticket_id = self.kwargs["pk"]
        try:
            return models.Ticket.objects.get(id=ticket_id)
        except models.Ticket.DoesNotExist:
            raise RuntimeError(f"Попытка изменить несуществующую заявку, id={ticket_id}")

    def check_permission(self):
        raise NotImplementedError("Проверка прав доступа не реализована")

    def calculate_redirect_url(self):
        return reverse("index")

    def apply_changes(self):
        raise NotImplementedError("Действие не определено")

    def check_action_available(self):
        pass

    def post(self, request, *args, **kwargs):
        self.ticket = self.get_changed_ticket()
        self.check_permission()
        self.check_action_available()
        self.apply_changes()
        redirect_url = self.calculate_redirect_url()
        return HttpResponseRedirect(redirect_url)


class RefreshTicketView(TicketChangeView):

    def check_permission(self):
        if not logic.check_user_can_refresh_ticket:
            raise PermissionDenied("Действие невозможно - вы должны либо быть создателем заявки, либо иметь права на управление")

    def calculate_redirect_url(self):
        # руководителя возвращаем в свой список заявок
        # создателя заявки - в свой
        # если это двое в одном лице - роль руководителя приоритетнее
        if logic.check_user_is_ticket_supervisor(self.ticket, self.request.user):
            return reverse("supervision")
        else:
            return reverse("outbox")

    def apply_changes(self):
        logic.refresh_ticket(self.ticket)


class CancelTicketView(TicketChangeView):

    def check_permission(self):
        if not logic.check_user_is_ticket_creator(self.ticket, self.request.user):
            raise PermissionDenied("Действие невозможно - вы не являетесь создателем заявки")

    def apply_changes(self):
        logic.cancel_ticket(self.ticket)

    def calculate_redirect_url(self):
        return reverse("outbox")


class SetTicketDoneView(TicketChangeView):

    def check_permission(self):
        if not logic.check_user_is_ticket_executor(self.ticket, self.request.user):
            raise PermissionDenied("Действие невозможно - вы не назначены исполнителем заявки")

    def apply_changes(self):
        logic.set_ticket_done(self.ticket)

    def calculate_redirect_url(self):
        return reverse("inbox")


class TicketChangeViewSupervisor(TicketChangeView):

    def check_permission(self):
        if not logic.check_user_is_ticket_supervisor(self.ticket, self.request.user):
            raise PermissionDenied("Действие невозможно - вы не можете управлять этой заявкой")

    def calculate_redirect_url(self):
        return reverse("supervision")


class DenyTicketView(TicketChangeViewSupervisor):

    def apply_changes(self):
        logic.deny_ticket(self.ticket)


class DelayTicketView(TicketChangeViewSupervisor):

    def apply_changes(self):
        logic.delay_ticket(self.ticket)


class CompleteTicketView(TicketChangeViewSupervisor):

    def apply_changes(self):
        logic.complete_ticket(self.ticket)


class AssignExecutorView(TicketChangeViewSupervisor):

    def apply_changes(self):
        form = forms.ExecutorAssignmentForm(self.request.POST)
        if form.is_valid():
            executor = form.cleaned_data["executor"]
            logic.assign_executor_for_ticket(self.ticket, executor)
