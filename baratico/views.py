from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.forms import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.datetime_safe import datetime
from django.views import generic
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.utils import timezone

from baratico import form
from baratico.form import RegistroForm
from baratico.models import Producto, Resenna, CarritoProducto, CarritoOferta, Usuario, Factura, LineaFacturaProducto


class RegistrarUsuario(CreateView):
    model = User
    template_name = 'baratico/registerUser.html'
    form_class = RegistroForm

    def post(self, request):
        try:
            username = User.objects.get(username=request.POST.get('username'))
            return render(request, 'baratico/registerUser.html', {})
        except:
            user = User.objects.create_user(
                request.POST.get('username'),
                request.POST.get('email'),
                request.POST.get('password')
            )
            user.email = request.POST.get('email')
            user.is_active = True
            user.is_staff = False
            user.save()
            nuevoUsuario = Usuario(direccion=request.POST.get('direccion'), nombre_usuario=user)
            nuevoUsuario.save()
            redirect('inicio')


class DetalleProducto(generic.DetailView):
    model = Producto
    template_name = 'baratico/producto.html'


class DetalleFactura(generic.DetailView):
    model = Factura
    template_name = 'baratico/lineasFactura.html'


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


class ComprasList(generic.ListView):
    model = Factura
    paginate_by = 10
    template_name = 'baratico/compras.html'

    def get_queryset(self):
        qs = Factura.objects.filter(usuario=self.request.user).order_by('-fecha')
        return qs


class ProductosList(generic.ListView):
    model = Producto
    paginate_by = 10
    template_name = 'baratico/productosList.html'

    def get_queryset(self):
        qs=Producto.objects.all()
        return qs


class CarritoList(generic.ListView):
    template_name = 'baratico/carrito.html'
    # context_object_name = 'carrito_producto_list'

    def get_queryset(self):
        try:
            usuario_actual = self.request.user
            return CarritoProducto.objects.filter(usuario=usuario_actual)
        except:
            return

    def get_context_data(self, **kwargs):
        context = super(CarritoList, self).get_context_data(**kwargs)
        usuario_actual = self.request.user
        context['carrito_producto_list'] = CarritoProducto.objects.filter(usuario=usuario_actual)
        context['carrito_oferta_list'] = CarritoOferta.objects.filter(usuario=usuario_actual)
        cp = CarritoProducto.objects.filter(usuario=usuario_actual)
        co = CarritoOferta.objects.filter(usuario=usuario_actual)
        total = Usuario.objects.get(nombre_usuario=usuario_actual).get_total_productos()
        context['carrito_producto_list'] = cp
        context['carrito_oferta_list'] = co
        context['total'] = total
        return context


def calificar_producto(request,id_producto):
    if request.method == 'POST':
        pUsuario = request.user
        producto = Producto.objects.get(pk=id_producto)
        calificacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario')
        fecha = datetime.now()
        resena_obj = Resenna(usuario=pUsuario, producto=producto, calificacion=calificacion, comentario=comentario, fecha=fecha)
        try:
            resena_obj.save()
        except:
            if comentario != '':
                resena_obj = Resenna.objects.get(usuario=pUsuario,producto=producto)
                resena_obj.comentario = comentario
                resena_obj.calificacion = calificacion
                resena_obj.save()

    return redirect('baratico:detalle_producto',pk=id_producto)


def inicio(request):
    return render(request, 'baratico/inicio.html', {})


def agregar_producto_carrito(request, id_producto):
    try:
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
            return redirect('baratico:detalle_producto', pk=id_producto)
    except Exception as e:
        usuario_actual = request.user
        producto = Producto.objects.get(pk=id_producto)
        producto=CarritoProducto.objects.get(usuario=usuario_actual, producto=producto)
        producto.cantidad=request.POST.get('cantidadCarrito')
        producto.save()
        return redirect('baratico:detalle_producto',pk=id_producto)


def eliminar_producto_carrito(request, id_producto):
    usuario_actual = request.user
    CarritoProducto.objects.filter(usuario=usuario_actual, producto=id_producto).delete()
    return redirect('baratico:ver_carrito')


def pagar_carrito(request):
    usuario = request.user
    qs_lineas_producto = CarritoProducto.objects.filter(usuario=usuario)

    if qs_lineas_producto:
        factura = Factura(fecha=timezone.now(), usuario=usuario)
        factura.save()
        for linea_producto_carrito in qs_lineas_producto:
            factura.lineafacturaproducto_set.create(
                cantidad=linea_producto_carrito.cantidad,
                precio=linea_producto_carrito.producto.precio,
                producto=linea_producto_carrito.producto
            )
        CarritoProducto.objects.filter(usuario=usuario).delete()
    return redirect('baratico:redirect-inicio')
