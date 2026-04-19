from django.urls import path
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from . import views

app_name = 'register'

urlpatterns = [
    path('register/',               views.register_view,     name='register'),
    path('register/success/',       views.register_success,  name='register_success'),
    path('login/',                  views.login_view,        name='login'),
    path('logout/',                 views.logout_view,       name='logout'),
    path('verify/<str:token>/',     views.verify_email,      name='verify_email'),
    path('admin-dashboard/',        views.admin_dashboard,   name='admin_dashboard'),
    path('profile/',                views.profile_dashboard, name='profile_dashboard'),
    path('profile/edit/',           views.edit_profile,      name='edit_profile'),
    path('profile/change-password/', PasswordChangeView.as_view(
        template_name='register/change_password.html',
        success_url='/profile/change-password/done/'
    ), name='change_password'),
    path('profile/change-password/done/', PasswordChangeDoneView.as_view(
        template_name='register/change_password_done.html'
    ), name='change_password_done'),
    path('profile/change-password/',      views.change_password,      name='change_password'),
    path('profile/change-password/done/', views.change_password_done, name='change_password_done'),
    path('manage/change-role/<int:user_id>/', views.change_user_role,       name='change_user_role'),
    path('membership/',                       views.membership_plans,        name='membership_plans'),
    path('membership/<str:plan>/checkout/',   views.membership_checkout,     name='membership_checkout'),
    path('membership/<str:plan>/confirmed/',  views.membership_confirmation, name='membership_confirmation'),
]
