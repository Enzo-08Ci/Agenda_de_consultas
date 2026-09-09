from django.shortcuts import redirect, render

from .models import Consulta, Paciente, Profissional


def _seed_initial_data():
    if not Paciente.objects.exists():
        Paciente.objects.create(
            nome='João da Silva',
            telefone='(11) 99999-1111',
            email='joao@email.com',
            observacoes='Paciente de exemplo.'
        )
        Paciente.objects.create(
            nome='Maria Souza',
            telefone='(11) 98888-2222',
            email='maria@email.com',
            observacoes='Paciente de exemplo.'
        )

    if not Profissional.objects.exists():
        Profissional.objects.create(
            nome='Dra. Ana Pereira',
            especialidade='Cardiologia',
            telefone='(11) 97777-3333'
        )
        Profissional.objects.create(
            nome='Dr. Carlos Mendes',
            especialidade='Dermatologia',
            telefone='(11) 96666-4444'
        )


def _get_context():
    _seed_initial_data()

    return {
        'pacientes': Paciente.objects.all(),
        'profissionais': Profissional.objects.all(),
        'consultas': Consulta.objects.select_related('paciente', 'profissional').all(),
    }


def home(request):
    contexto = _get_context()
    return render(request, 'home.html', contexto)


def agendar_consulta(request):
    contexto = _get_context()
    contexto['mensagem'] = None

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente')
        paciente_nome = request.POST.get('paciente_nome', '').strip()
        profissional_id = request.POST.get('profissional')
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        duracao = request.POST.get('duracao')
        observacoes = request.POST.get('observacoes', '').strip()

        if not all([profissional_id, data, horario]):
            contexto['mensagem'] = 'Preencha todos os campos obrigatórios.'
        else:
            try:
                paciente = None
                if paciente_id:
                    paciente = Paciente.objects.get(id=paciente_id)
                elif paciente_nome:
                    paciente, _ = Paciente.objects.get_or_create(nome=paciente_nome)
                else:
                    contexto['mensagem'] = 'Informe seu nome para agendar a consulta.'

                if paciente:
                    profissional = Profissional.objects.get(id=profissional_id)
                    Consulta.objects.create(
                        paciente=paciente,
                        profissional=profissional,
                        data=data,
                        horario=horario,
                        duracao=int(duracao or 60),
                        observacoes=observacoes,
                    )
                    return redirect('agendar_consulta')
            except (Paciente.DoesNotExist, Profissional.DoesNotExist, ValueError):
                contexto['mensagem'] = 'Não foi possível criar a consulta. Verifique os dados informados.'

    return render(request, 'index.html', contexto)
