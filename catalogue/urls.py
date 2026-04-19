from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    # ── Public ───────────────────────────────────────────────
    path('catalogue/',              views.catalogue,      name='catalogue'),
    path('catalogue/clear-viewed/', views.clear_viewed,   name='clear_viewed'),
    path('catalogue/<slug:slug>/',  views.product_detail, name='product_detail'),

    # ── AJAX rating ──────────────────────────────────────────
    path('catalogue/<int:product_id>/rate/', views.rate_product, name='rate_product'),

    # ── Admin — Products ─────────────────────────────────────
    path('manage/products/',                      views.admin_product_list,   name='admin_product_list'),
    path('manage/products/add/',                  views.admin_product_add,    name='admin_product_add'),
    path('manage/products/<int:pk>/edit/',        views.admin_product_edit,   name='admin_product_edit'),
    path('manage/products/<int:pk>/delete/',      views.admin_product_delete, name='admin_product_delete'),

    # ── Admin — Categories ───────────────────────────────────
    path('manage/categories/',                    views.admin_category_list,   name='admin_category_list'),
    path('manage/categories/add/',                views.admin_category_add,    name='admin_category_add'),
    path('manage/categories/<int:pk>/edit/',      views.admin_category_edit,   name='admin_category_edit'),
    path('manage/categories/<int:pk>/delete/',    views.admin_category_delete, name='admin_category_delete'),

    # ── Admin — Subcategories ────────────────────────────────
    path('manage/subcategories/add/',             views.admin_subcategory_add,    name='admin_subcategory_add'),
    path('manage/subcategories/<int:pk>/edit/',   views.admin_subcategory_edit,   name='admin_subcategory_edit'),
    path('manage/subcategories/<int:pk>/delete/', views.admin_subcategory_delete, name='admin_subcategory_delete'),
]
