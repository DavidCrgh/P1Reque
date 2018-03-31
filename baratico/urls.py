from sys import path

from django.conf.urls import url

from baratico import views

urlpatterns = [
    url(r'^login$', views.login),
]

