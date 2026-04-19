from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("",                              views.home,              name="home"),
    path("about/",                        views.about,             name="about"),
    path("contact/",                      views.contact,           name="contact"),
    path("contact/read/<int:pk>/",        views.mark_message_read, name="mark_message_read"),
]
