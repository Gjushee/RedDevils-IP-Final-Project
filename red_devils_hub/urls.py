from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("", include("register.urls")),
    path("", include("catalogue.urls")),
    path("", include("matches.urls")),
    path("", include("transfers.urls")),
    path("", include("cart.urls")),    
    path("", include("checkout.urls")),   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
