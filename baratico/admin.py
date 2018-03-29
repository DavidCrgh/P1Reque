from django.contrib import admin

from .models import *

# Register your models here.


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'supercategoria']
    list_filter = ['nombre']
    search_fields = ['nombre']
    ordering = ('supercategoria',)

    class Meta:
        model = Categoria


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto)
