from django.contrib import admin

from .models import Consulta, Paciente, Profissional


admin.site.register(Paciente)
admin.site.register(Profissional)
admin.site.register(Consulta)
