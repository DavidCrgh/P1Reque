from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.shortcuts import render, render_to_response
from django.views import generic
from django.db import connection
from django.http import HttpResponseRedirect

from baratico.models import Producto, Resenna, CarritoProducto, CarritoOferta, Usuario


class DetalleProducto(generic.DetailView):
    model = Producto
    template_name = 'baratico/producto.html'


class ResultadosBusquedaList(generic.ListView):
    model = Producto
    paginate_by = 10
    template_name = 'baratico/resultadosBusqueda.html'

    def get_queryset(self):
        qs = Producto.objects.all()

        keywords = self.request.GET.get('barraBusqueda')
        if keywords:
            consulta = SearchQuery(keywords)
            vector = SearchVector('nombre', 'descripcion')
            qs = qs.annotate(search=vector).filter(search=consulta)
            qs = qs.annotate(rank=SearchRank(vector, consulta)).order_by('-rank')

        return qs


class CarritoList(generic.ListView):
    template_name = 'baratico/carrito.html'
    # context_object_name = 'carrito_producto_list'


    def get_queryset(self):
        usuario_actual = self.request.user
        return CarritoProducto.objects.filter(usuario=usuario_actual)

    def get_context_data(self, **kwargs):
        context = super(CarritoList, self).get_context_data(**kwargs)
        usuario_actual = self.request.user
        cp = CarritoProducto.objects.filter(usuario=usuario_actual)
        co = CarritoOferta.objects.filter(usuario=usuario_actual)
        total = Usuario.objects.get(nombre_usuario=usuario_actual).get_total_productos()
        context['carrito_producto_list'] = cp
        context['carrito_oferta_list'] = co
        context['total'] = total
        return context


def login(request):
    return render(request, 'baratico/login.html', {})


def inicio(request):
    return render(request, 'baratico/inicio.html', {})


def agregar_producto_carrito(request, id_producto):
    if request.user.is_authenticated:
        cantidad = request.POST.get('cantidadCarrito')
        producto = Producto.objects.get(pk=id_producto)
        usuario_actual = request.user
        cp = CarritoProducto(cantidad=cantidad, producto=producto, usuario=usuario_actual)
        cp.save()
        print("Cantidad: ", cantidad)
        print("Producto: ", producto.nombre)
        print("Usuario: ", usuario_actual.username)
        print("CarritoProducto agregado")

    return render(request, 'baratico/inicio.html', {})


def eliminar_producto_carrito(request, id_producto):
    usuario_actual = request.user
    CarritoProducto.objects.filter(usuario=usuario_actual, producto=id_producto).delete()
    return render(request, 'baratico/inicio.html', {})
