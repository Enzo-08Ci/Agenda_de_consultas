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
            reverse('agendar_consulta'),
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

    def test_pode_editar_uma_consulta_existente(self):
        paciente = Paciente.objects.create(
            nome='Paciente Atual',
            telefone='(11) 11111-1111',
            email='atual@email.com'
        )
        profissional = Profissional.objects.create(
            nome='Dr. Teste',
            especialidade='Cardiologia',
            telefone='(11) 99999-0000'
        )
        consulta = Consulta.objects.create(
            paciente=paciente,
            profissional=profissional,
            data='2026-09-15',
            horario='09:00',
            duracao=60,
            observacoes='Observação antiga'
        )

        response = self.client.post(
            reverse('editar_consulta', args=[consulta.id]),
            {
                'paciente': paciente.id,
                'paciente_nome': 'Paciente Atual',
                'profissional': profissional.id,
                'data': '2026-09-16',
                'horario': '10:00',
                'duracao': '90',
                'status': 'confirmada',
                'observacoes': 'Observação nova',
            }
        )

        self.assertEqual(response.status_code, 302)
        consulta.refresh_from_db()
        self.assertEqual(consulta.data.isoformat(), '2026-09-16')
        self.assertEqual(consulta.horario.strftime('%H:%M'), '10:00')
        self.assertEqual(consulta.status, 'confirmada')
        self.assertEqual(consulta.observacoes, 'Observação nova')

    def test_pode_excluir_uma_consulta_existente(self):
        paciente = Paciente.objects.create(
            nome='Paciente Excluir',
            telefone='(11) 22222-2222',
            email='excluir@email.com'
        )
        profissional = Profissional.objects.create(
            nome='Dr. Delete',
            especialidade='Dermatologia',
            telefone='(11) 88888-0000'
        )
        consulta = Consulta.objects.create(
            paciente=paciente,
            profissional=profissional,
            data='2026-09-17',
            horario='11:00',
            duracao=60,
            observacoes='Vai sair'
        )

        response = self.client.post(
            reverse('excluir_consulta', args=[consulta.id]),
            {'confirmar': 'true'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Consulta.objects.filter(id=consulta.id).exists())

    def test_pessoa_pode_se_cadastrar_com_dados_completos(self):
        response = self.client.post(
            reverse('cadastrar_pessoa'),
            {
                'nome': 'Maria da Silva',
                'cpf': '12345678909',
                'telefone': '(11) 98888-7777',
                'email': 'maria@email.com',
                'data_nascimento': '1990-05-10',
                'endereco': 'Rua das Flores, 123',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'observacoes': 'Paciente novo',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Paciente.objects.filter(nome='Maria da Silva', cpf='12345678909').exists())

    def test_agendamento_pode_incluir_cadastro_completo_da_pessoa(self):
        profissional = Profissional.objects.create(
            nome='Dr. Teste',
            especialidade='Cardiologia',
            telefone='(11) 99999-0000'
        )

        response = self.client.post(
            reverse('agendar_consulta'),
            {
                'paciente_nome': 'Joana Souza',
                'cpf': '98765432100',
                'telefone': '(11) 97777-1234',
                'email': 'joana@email.com',
                'data_nascimento': '1995-04-23',
                'endereco': 'Av. Paulista, 1000',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'observacoes': 'Quero agendar a consulta',
                'profissional': profissional.id,
                'data': '2026-09-20',
                'horario': '14:00',
                'duracao': '60',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Paciente.objects.filter(nome='Joana Souza', cpf='98765432100').exists())
        self.assertTrue(Consulta.objects.filter(paciente__cpf='98765432100').exists())
