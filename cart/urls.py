from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('cart/',                          views.cart_detail,     name='cart_detail'),
    path('cart/summary/',                  views.cart_summary,    name='cart_summary'),
    path('cart/add/<int:product_id>/',     views.add_to_cart,     name='add_to_cart'),
    path('cart/update/<int:item_id>/',     views.update_quantity,  name='update_quantity'),
    path('cart/remove/<int:item_id>/',     views.remove_item,     name='remove_item'),
    path('cart/clear/',                    views.clear_cart,      name='clear_cart'),
    path('wishlist/',                         views.wishlist_page,   name='wishlist_page'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),

]
