from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from . import models


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", max_length=20)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = self.request.get_full_path()
        self.helper.layout = Layout(
            Fieldset(
                "",
                "username",
                "password"
            ),
            ButtonHolder(
                Submit("submit", "Войти")
            )
        )


class TicketCreateForm(forms.ModelForm):

    class Meta:
        model = models.Ticket
        fields = ("departament", "title", "description", "deadline")
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"})
        }

    def __init__(self, *args, **kwargs):
        super(). __init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""
        self.helper.layout = Layout(
            Fieldset(
                "",
                "departament",
                "title",
                "description",
                "deadline"
            ),
            ButtonHolder(
                Submit("submit", "Сохранить")
            )
        )


class ExecutorAssignmentForm(forms.Form):
    executor = forms.ModelChoiceField(label="Исполнитель", queryset=models.User.objects.all(), to_field_name="id")

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop("queryset") if "queryset" in kwargs else None
        super().__init__(*args, **kwargs)
        if qs:
            self.fields["executor"].queryset = qs
        # ToDo узнать, почему переопределение метода не сработало
        # https://docs.djangoproject.com/en/3.0/ref/forms/fields/#modelchoicefield
        self.fields["executor"].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"
        # ----------------------------------------------------------
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "----calculated dynamically----"
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap4/layout/inline_field.html"
        self.helper.layout = Layout(
            Fieldset(
                "",
                "executor"
            ),
            ButtonHolder(
                Submit("submit", "Назначить")
            )
        )


class SimpleInlineForm(forms.Form):
    def __init__(self, *args):
        super().__init__(*args)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = "----calculated dynamically----"
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap4/layout/inline_field.html"


class DelayTicketForm(SimpleInlineForm):

    def __init__(self, *args):
        super().__init__(*args)
        self.helper.layout = Layout(
            ButtonHolder(
                Submit("submit", "Отложить", css_class="btn btn-secondary")
            )
        )


class DenyTicketForm(SimpleInlineForm):

    def __init__(self, *args):
        super().__init__(*args)
        self.helper.layout = Layout(
            ButtonHolder(
                Submit("submit", "Отклонить", css_class="btn btn-danger")
            )
        )


class RefreshTicketForm(SimpleInlineForm):

    def __init__(self, *args):
        super().__init__(*args)
        self.helper.layout = Layout(
            ButtonHolder(
                Submit("submit", "Возобновить", css_class="btn btn-success")
            )
        )


class SetTicketDoneForm(SimpleInlineForm):

    def __init__(self, *args):
        super().__init__(*args)
        self.helper.layout = Layout(
            ButtonHolder(
                Submit("submit", "Готово", css_class="btn btn-success")
            )
        )


class CompleteTicketForm(SimpleInlineForm):

    def __init__(self, *args):
        super().__init__(*args)
        self.helper.layout = Layout(
            ButtonHolder(
                Submit("submit", "Проверено", css_class="btn btn-success")
            )
        )


class CancelTicketForm(SimpleInlineForm):

    def __init__(self, *args):
        super().__init__(*args)
        self.helper.layout = Layout(
            ButtonHolder(
                Submit("submit", "Отменить", css_class="btn btn-danger")
            )
        )
