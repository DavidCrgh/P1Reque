from django.urls import path
from django.conf.urls import url
from django.contrib.auth.views import login

from . import views

app_name = 'baratico'
urlpatterns = [
    url(r'^login$', views.login),
    path('redirect_inicio/', views.inicio, name='redirect-inicio'),
    path('resultados/', views.ResultadosBusquedaList.as_view(), name='resultados-busqueda'),
    path('<int:pk>/', views.DetalleProducto.as_view(), name='detalle_producto'),
    path('<int:id_producto>/agregarProducto', views.agregar_producto_carrito, name="anadir_producto_carrito"),
    path('carrito/', views.CarritoList.as_view(), name='ver_carrito'),
    path('carrito/borrar_producto/<int:id_producto>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
]
