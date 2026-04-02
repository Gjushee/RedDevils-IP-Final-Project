from django.urls import path
from . import views
 
app_name = 'catalogue'
 
urlpatterns = [
    path('catalogue/',           views.catalogue,       name='catalogue'),
    path('catalogue/<slug:slug>/', views.product_detail, name='product_detail'),
]