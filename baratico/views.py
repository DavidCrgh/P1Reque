from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.shortcuts import render, render_to_response
from django.views import generic

from baratico.models import Producto


class ResultadosBusquedaList(generic.ListView):
    model = Producto
    paginate_by = 10
    template_name = 'baratico/resultadosBusqueda.html'  # TODO crear html para resultados de busqueda

    def get_queryset(self):
        qs = Producto.objects.all()

        keywords = self.request.GET.get('barraBusqueda')
        if keywords:
            consulta = SearchQuery(keywords)
            vector = SearchVector('nombre', 'descripcion')
            qs = qs.annotate(search=vector).filter(search=consulta)
            qs = qs.annotate(rank=SearchRank(vector, consulta)).order_by('-rank')

        return qs


def login(request):
    return render(request, 'baratico/login.html', {})
