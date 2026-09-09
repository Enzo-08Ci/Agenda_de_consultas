from django.urls import path

from .views import agendar_consulta, home

urlpatterns = [
    path('', home, name='home'),
    path('agendar-consulta/', agendar_consulta, name='agendar_consulta'),
]
