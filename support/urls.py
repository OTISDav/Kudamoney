# support/urls.py
from django.urls import path
from .views import (
    TicketCreateView, UserTicketListView, UserTicketDetailView, UserMessageCreateView,
    AdminTicketListView, AdminTicketDetailView, AdminMessageCreateView
)

urlpatterns = [
    # utilisateurs
    path('tickets/create/', TicketCreateView.as_view(), name='ticket_create'),
    path('tickets/my/', UserTicketListView.as_view(), name='user_ticket_list'),
    path('tickets/<int:pk>/', UserTicketDetailView.as_view(), name='user_ticket_detail'),
    path('tickets/<int:pk>/messages/add/', UserMessageCreateView.as_view(), name='user_message_add'),

    # administrateurs
    path('admin/tickets/', AdminTicketListView.as_view(), name='admin_ticket_list'),
    path('admin/tickets/<int:pk>/', AdminTicketDetailView.as_view(), name='admin_ticket_detail'),
    path('admin/tickets/<int:pk>/messages/add/', AdminMessageCreateView.as_view(), name='admin_message_add'),
]
