from django.urls import path
from .views import NotificationListView, NotificationMarkAsReadView, NotificationDeleteView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('mark-as-read/', NotificationMarkAsReadView.as_view(), name='notification_mark_all_read'),
    path('mark-as-read/<int:notification_id>/', NotificationMarkAsReadView.as_view(), name='notification_mark_single_read'),
    path('delete/<int:pk>/', NotificationDeleteView.as_view(), name='notification_delete'),
]