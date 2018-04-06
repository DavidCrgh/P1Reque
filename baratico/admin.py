from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Categoria, Oferta, Producto, Resenna, ProductoOferta, Factura, LineaFacturaProducto,\
    LineaFacturaOferta, Usuario

# Register your models here.

admin.site.site_header = 'Administración de Sistema El Baratico'


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'supercategoria']
    list_filter = ['nombre']
    search_fields = ['nombre']
    ordering = ('supercategoria',)

    class Meta:
        model = Categoria


class ProductoOfertaInLine(admin.TabularInline):
    model = ProductoOferta
    fk_name = 'oferta'
    fields = ['producto', 'cantidad']
    extra = 1


class OfertaAdmin(admin.ModelAdmin):
    list_display_links = None
    list_display = ['nombre', 'tipo', 'fecha_inicio', 'fecha_fin']
    list_filter = ['tipo']
    search_fields = ['nombre']
    inlines = [ProductoOfertaInLine]


class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cantidad',  'precio', 'categoria', 'calificacion_general', 'ventas_totales']
    list_filter = ['categoria']
    search_fields = ['nombre']


class ResennaAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['usuario', 'comentario', 'calificacion', 'fecha']
    fields = ['usuario', 'calificacion', 'comentario']
    readonly_fields = ['usuario', 'calificacion']


class UsuarioInLine(admin.StackedInline):
    model = Usuario
    can_delete = False
    verbose_name_plural = 'Datos Personales'


class UserAdmin(BaseUserAdmin):
    inlines = (UsuarioInLine,)


class LineaFacturaProductoInLine(admin.TabularInline):
    model = LineaFacturaProducto
    readonly_fields = ['cantidad', 'precio', ]


class LineaFacturaOfertaInLine(admin.TabularInline):
    model = LineaFacturaOferta
    readonly_fields = ['cantidad', 'precio',]


class FacturaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'fecha']
    inlines = [LineaFacturaProductoInLine, LineaFacturaOfertaInLine]
    readonly_fields = ['usuario']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Oferta, OfertaAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Resenna, ResennaAdmin)
admin.site.register(Factura, FacturaAdmin)
