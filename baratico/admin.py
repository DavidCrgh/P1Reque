from django.contrib import admin

from .models import Categoria, Producto

# Register your models here.


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'supercategoria']
    list_filter = ['nombre']
    search_fields = ['nombre']
    ordering = ('supercategoria',)

    class Meta:
        model = Categoria


class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cantidad', 'precio', 'categoria']
    list_filter = ['categoria']
    search_fields = ['nombre']


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
