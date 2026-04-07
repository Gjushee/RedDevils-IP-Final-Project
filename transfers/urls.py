from django.urls import path
from . import views

app_name = 'transfers'

urlpatterns = [
    path('transfers/', views.transfers, name='transfers'),
    path('transfers/my-rumours/', views.my_rumours, name='my_rumours'),
    path('transfers/delete/<int:pk>/', views.delete_rumour, name='delete_rumour'),
    path('transfers/moderate/', views.admin_moderate, name='admin_moderate'),
]
