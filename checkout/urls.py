from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('checkout/checkout/',                       views.checkout,              name='checkout'),
    path('checkout/confirmation/<str:order_ref>/',   views.confirmation,          name='confirmation'),
    path('checkout/orders/',                         views.order_history,         name='order_history'),
    path('checkout/paypal/create/',                  views.paypal_create_order,   name='paypal_create'),
    path('checkout/paypal/execute/',                 views.paypal_capture,        name='paypal_capture'),
    path('checkout/paypal/save-billing/',            views.save_billing_session,  name='save_billing'),
]
