from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    path('register/',               views.register_view,      name='register'),
    path('login/',                  views.login_view,         name='login'),
    path('logout/',                 views.logout_view,        name='logout'),
    path('verify/<str:token>/',     views.verify_email,       name='verify_email'),
    path('admin-dashboard/',        views.admin_dashboard,    name='admin_dashboard'),
    path('profile/',                views.profile_dashboard,  name='profile_dashboard'),
    path('profile/edit/',           views.edit_profile,       name='edit_profile'),
    path('admin/change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
]
