from django import forms

class LoginForm(forms.Form):
    login = forms.CharField(label='Логин', max_length=20)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
