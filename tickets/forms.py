from django import forms
from . import models


class LoginForm(forms.Form):
    login = forms.CharField(label="Логин", max_length=20)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class TicketForm(forms.ModelForm):

    class Meta:
        model = models.Ticket
        fields = ("departament","title", "description", "deadline")
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"})
        }


class ExecutorAssignmentForm(forms.Form):
    executor = forms.ModelChoiceField(label="Исполнитель", queryset=models.User.objects.all(), to_field_name="id")

    def __init__(self, *args, **kwargs):
        qs = kwargs.get("queryset")
        super().__init__(*args)
        if qs:
            self.fields["executor"].queryset = qs
        # ToDo узнать, почему переопределение метода не сработало
        # https://docs.djangoproject.com/en/3.0/ref/forms/fields/#modelchoicefield
        self.fields["executor"].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"
