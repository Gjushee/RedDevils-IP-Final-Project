from django.urls import path
from . import views
 
app_name = 'register'
 
urlpatterns = [
    path('register/',               views.register_view,   name='register'),
    path('login/',                  views.login_view,      name='login'),
    path('logout/',                 views.logout_view,     name='logout'),
    path('register/verify/<str:token>/',     views.verify_email,    name='verify_email'),
    path('admin-dashboard/',        views.admin_dashboard, name='admin_dashboard'),
]