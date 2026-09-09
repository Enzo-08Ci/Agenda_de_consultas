from django.test import TestCase
from django.urls import reverse

from .models import Consulta, Paciente, Profissional


class AgendaConsultasTests(TestCase):
    def test_paciente_pode_cadastrar_proprio_nome(self):
        profissional = Profissional.objects.create(
            nome='Dr. Teste',
            especialidade='Cardiologia',
            telefone='(11) 99999-0000'
        )

        response = self.client.post(
            reverse('index'),
            {
                'paciente': '',
                'paciente_nome': 'Novo Paciente',
                'profissional': profissional.id,
                'data': '2026-09-15',
                'horario': '09:00',
                'duracao': '60',
                'observacoes': 'Consulta de teste',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Paciente.objects.filter(nome='Novo Paciente').exists())
        self.assertTrue(Consulta.objects.filter(paciente__nome='Novo Paciente').exists())
