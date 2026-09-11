from django.urls import path

from .views import agendar_consulta, cadastrar_pessoa, detalhes_consulta, editar_consulta, excluir_consulta, home

urlpatterns = [
    path('', home, name='home'),
    path('cadastrar-pessoa/', cadastrar_pessoa, name='cadastrar_pessoa'),
    path('agendar-consulta/', agendar_consulta, name='agendar_consulta'),
    path('consultas/<int:consulta_id>/', detalhes_consulta, name='detalhes_consulta'),
    path('consultas/<int:consulta_id>/editar/', editar_consulta, name='editar_consulta'),
    path('consultas/<int:consulta_id>/excluir/', excluir_consulta, name='excluir_consulta'),
]
