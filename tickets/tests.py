from django.contrib.auth.models import User
from django.test import TestCase
from . import forms, models


class NewTicketTestCase(TestCase):

    def setUp(self):
        self.client = django.test.Client()
    
    def test_login_required(self):
        response = self.client.get("/new_ticket/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/new_ticket/")

    def test_current_user_saved_as_creator(self):
        self.fail()

    def test_form_without_title_not_allowed(self):
        form_data = {
            "title": "",
            "description": "We have a problem"
        }
        form = forms.TicketCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_without_description_not_allowed(self):
        form_data = {
            "title": "Just one more ticket",
            "description": ""
        }
        form = forms.TicketCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_sufficient_validation(self):
        departament = models.Departament.objects.create(name="Отдел 1")
        form_data = {
            "departament": departament,
            "title": "Just one more ticket",
            "description": "Its enough to write title and description"
        }
        form = forms.TicketCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
