from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views import View
from tickets import forms, models, filters


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


class TicketList(LoginRequiredMixin, ListView):
    model = models.Ticket
    filterset_class = filters.TicketFilter

    def get_primary_queryset(self):
        return self.model.objects.all()
    
    def get_queryset(self):
        queryset = self.get_primary_queryset()
        self.filterset = self.filterset_class(self.request.GET, request=self.request, queryset=queryset)
        return self.filterset.qs
    
    def get_column_list(self):
        """
        Список колонок в таблице, которые будут видны пользователю.
        """
        return ['title', 'date_create', 'priority', 'deadline', 'days_left']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filterset"] = self.filterset
        context["column_list"] = self.get_column_list()
        return context


class InboxTickets(TicketList):
    filterset_class = filters.ExecutorTicketFilter

    def get_column_list(self):
        """
        Список колонок в таблице, которые будут видны пользователю.
        Исполнитель - Заголовок, от кого, дата создания, приоритет, срок
        """
        column_list = super().get_column_list()
        column_list.append('creator')
        return column_list

    def get_primary_queryset(self):
        return self.model.objects.filter(
            executor=self.request.user
        ).filter(
            status=models.Ticket.STATUS_IN_WORK
        )


class OutboxTickets(TicketList):
    filterset_class = filters.CreatorTicketFilter
    def get_column_list(self):
        """
        Список колонок в таблице, которые будут видны пользователю.
        Создатель - Заголовок, дата создания, приоритет, срок, статус
        """
        column_list = super().get_column_list()
        column_list.append('status')
        return column_list

    def get_primary_queryset(self):
        return self.model.objects.filter(creator=self.request.user)


class DepartamentSupervision(TicketList):
    filterset_class = filters.SupervisorTicketFilter

    def get_column_list(self):
        """
        Список колонок в таблице, которые будут видны пользователю.
        Руководитель - все
        """
        column_list = super().get_column_list()
        column_list.extend(['creator', 'status', 'executors'])
        return column_list

    def get_primary_queryset(self):
        return self.model.objects.filter(departament__in=self.request.user.supervised_departaments.all())


class TicketDetail(LoginRequiredMixin, DetailView):
    model = models.Ticket
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = (
            self.object.departament in self.request.user.supervised_departaments.all()
        )
        if not context["can_manage"]:
            return context
        self._add_available_actions_to_context(context)
        self._add_management_forms_to_context(context)
        return context

    def _add_available_actions_to_context(self, context):
        """
        По статусу заявки определяет, какие действия над ней
        (отложить, отклонить, назначить исполнителя, отметить 
        как выполненное и т.д.) разрешены пользователю и добавляет 
        в контекст ответа соответствующие флаги.
        """
        # ключ - доступное пользователю действие
        # значение - набор статусов, которые позволяют это действие выполнять
        status_transition_table = {
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

        for action in status_transition_table:
            context[action] = self.object.status in status_transition_table[action]
    
    def _add_management_forms_to_context(self, context):
        """
        Для каждого разрешённого действия добавляет на страницу 
        однокнопочную форму, переводящую заявку в новый статус.
        """
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


class TicketManagementView(LoginRequiredMixin, View):
    """
    Представление, обрабатывающее изменение статуса заявки.

    Обслуживается несколькими url'ами.

    В зависимости от того, в какой статус переведена заявка,
    ей могут присваиваться различные дополнительные атрибуты,
    может меняться URL, на который перенаправляется пользователь
    и т.д.

    Главный метод - post, он задаёт шаблон для обработки заявки
    и порядок применения всех методов.
    """

    def get_updates(self):
        """
        Вычисляет и возвращает новые значения атрибутов заявки,
        которые должны быть выставлены.

        В базовом варианте определяет новый статус заявки в завимости от
        url, на который пришёл запрос.
        """
        url_name = resolve(self.request.path_info).url_name
        status_map = {
            "ticket-refresh": models.Ticket.STATUS_NEW,
            "ticket-delay": models.Ticket.STATUS_DELAYED,
            "ticket-deny": models.Ticket.STATUS_DENIED,
            "ticket-assign": models.Ticket.STATUS_IN_WORK,
            "ticket-done": models.Ticket.STATUS_CONTROL,
            "ticket-complete": models.Ticket.STATUS_COMPLETE,
        }
        new_status = status_map.get(url_name)
        return {"status": new_status}

    def get_changed_ticket(self):
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
        self.ticket = self.get_changed_ticket()
        updates = self.get_updates()
        if updates:
            self.update_ticket(updates)
            pass
        redirect_url = self.calculate_redirect_url()
        return HttpResponseRedirect(redirect_url)

class AssignExecutorView(TicketManagementView):
    """
    Представление для назначения исполнителя заявки.
    """

    def get_updates(self):
        updates = super().get_updates()
        form = forms.ExecutorAssignmentForm(self.request.POST)
        if form.is_valid():
            updates["executor"] = form.cleaned_data["executor"]
        return updates
