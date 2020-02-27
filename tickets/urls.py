from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('new_ticket/', views.CreateTicketView.as_view(), name='new_ticket'),
    path('inbox/', views.InboxTickets.as_view()),
    path('outbox/', views.OutboxTickets.as_view()),
    path('supervision/', views.index)
]
