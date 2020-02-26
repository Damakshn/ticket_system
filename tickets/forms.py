from django import forms
from . import models


class LoginForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=20)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class TicketForm(forms.ModelForm):

    class Meta:
        model = models.Ticket
        fields = ('title', 'description', 'deadline')
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'})
        }
