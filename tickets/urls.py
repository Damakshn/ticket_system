from django.urls import path
from django.contrib.auth import views as auth_views
from . import forms
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(authentication_form=forms.LoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("new_ticket/", views.CreateTicketView.as_view(), name="new_ticket"),
    path("inbox/", views.TicketList.as_view(), name="inbox"),
    path("outbox/", views.TicketList.as_view(), name="outbox"),
    path("supervision/", views.TicketList.as_view(), name="supervision"),
    path("ticket/<int:pk>", views.TicketDetail.as_view(), name="ticket-detail"),
    path("ticket/<int:pk>/assign", views.AssignExecutorView.as_view(), name="ticket-assign"),
    path("ticket/<int:pk>/delay", views.DelayTicketView.as_view(), name="ticket-delay"),
    path("ticket/<int:pk>/deny", views.DenyTicketView.as_view(), name="ticket-deny"),
    path("ticket/<int:pk>/refresh", views.RefreshTicketView.as_view(), name="ticket-refresh"),
    path("ticket/<int:pk>/done", views.SetTicketDoneView.as_view(), name="ticket-done"),
    path("ticket/<int:pk>/complete", views.CompleteTicketView.as_view(), name="ticket-complete"),
    path("ticket/<int:pk>/cancel", views.CancelTicketView.as_view(), name="ticket-cancel"),
]
