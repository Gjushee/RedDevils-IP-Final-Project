from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    path('register/',               views.register_view,      name='register'),
    path('register/success/',       views.register_success,   name='register_success'),
    path('login/',                  views.login_view,         name='login'),
    path('logout/',                 views.logout_view,        name='logout'),
    path('verify/<str:token>/',     views.verify_email,       name='verify_email'),
    path('admin-dashboard/',        views.admin_dashboard,    name='admin_dashboard'),
    path('profile/',                views.profile_dashboard,  name='profile_dashboard'),
    path('profile/edit/',                 views.edit_profile,         name='edit_profile'),
    path('profile/change-password/',      views.change_password,      name='change_password'),
    path('profile/change-password/done/', views.change_password_done, name='change_password_done'),
    path('manage/change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    path('membership/',                      views.membership_plans,        name='membership_plans'),
    path('membership/<str:plan>/checkout/',  views.membership_checkout,     name='membership_checkout'),
    path('membership/<str:plan>/confirmed/', views.membership_confirmation, name='membership_confirmation'),
    path('manage/messages/<int:pk>/read/', views.mark_message_read, name='mark_message_read'),
    path('manage/messages/<int:pk>/delete/', views.delete_message, name='delete_message'),
]
