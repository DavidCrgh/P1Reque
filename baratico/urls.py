from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

app_name = 'baratico'
urlpatterns = [
    url(r'^login$', views.login),
    path('resultados/', views.ResultadosBusquedaList.as_view(), name='resultados-busqueda'),
]
