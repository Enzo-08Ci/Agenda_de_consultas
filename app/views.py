from django.shortcuts import get_object_or_404, redirect, render

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


def _salvar_consulta(request, consulta=None):
    paciente_id = request.POST.get('paciente')
    paciente_nome = request.POST.get('paciente_nome', '').strip()
    cpf = request.POST.get('cpf', '').strip()
    telefone = request.POST.get('telefone', '').strip()
    email = request.POST.get('email', '').strip()
    data_nascimento = request.POST.get('data_nascimento')
    endereco = request.POST.get('endereco', '').strip()
    cidade = request.POST.get('cidade', '').strip()
    estado = request.POST.get('estado', '').strip()
    profissional_id = request.POST.get('profissional')
    data = request.POST.get('data')
    horario = request.POST.get('horario')
    duracao = request.POST.get('duracao')
    observacoes = request.POST.get('observacoes', '').strip()
    status = request.POST.get('status', consulta.status if consulta else 'agendada')

    if not all([profissional_id, data, horario]) or not paciente_nome:
        raise ValueError('Preencha todos os campos obrigatórios.')

    if paciente_id:
        paciente = Paciente.objects.get(id=paciente_id)
    else:
        paciente = None
        if cpf:
            paciente, _ = Paciente.objects.get_or_create(
                cpf=cpf,
                defaults={
                    'nome': paciente_nome,
                    'telefone': telefone,
                    'email': email,
                    'data_nascimento': data_nascimento,
                    'endereco': endereco,
                    'cidade': cidade,
                    'estado': estado,
                    'observacoes': observacoes,
                },
            )
        if paciente is None:
            paciente, _ = Paciente.objects.get_or_create(nome=paciente_nome)

        if paciente:
            paciente.nome = paciente_nome
            paciente.telefone = telefone or paciente.telefone
            paciente.email = email or paciente.email
            paciente.data_nascimento = data_nascimento or paciente.data_nascimento
            paciente.endereco = endereco or paciente.endereco
            paciente.cidade = cidade or paciente.cidade
            paciente.estado = estado or paciente.estado
            paciente.observacoes = observacoes or paciente.observacoes
            paciente.save(update_fields=[
                'nome',
                'telefone',
                'email',
                'data_nascimento',
                'endereco',
                'cidade',
                'estado',
                'observacoes',
            ])

    profissional = Profissional.objects.get(id=profissional_id)
    consulta_data = {
        'paciente': paciente,
        'profissional': profissional,
        'data': data,
        'horario': horario,
        'duracao': int(duracao or 60),
        'status': status,
        'observacoes': observacoes,
    }

    if consulta:
        for field, value in consulta_data.items():
            setattr(consulta, field, value)
        consulta.save()
        return consulta

    return Consulta.objects.create(**consulta_data)


def home(request):
    contexto = _get_context()
    return render(request, 'home.html', contexto)


def cadastrar_pessoa(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        email = request.POST.get('email', '').strip()
        data_nascimento = request.POST.get('data_nascimento')
        endereco = request.POST.get('endereco', '').strip()
        cidade = request.POST.get('cidade', '').strip()
        estado = request.POST.get('estado', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()

        if not all([nome, cpf, telefone, data_nascimento]):
            return redirect('home')

        paciente, created = Paciente.objects.get_or_create(
            cpf=cpf,
            defaults={
                'nome': nome,
                'telefone': telefone,
                'email': email,
                'data_nascimento': data_nascimento,
                'endereco': endereco,
                'cidade': cidade,
                'estado': estado,
                'observacoes': observacoes,
            }
        )

        if not created:
            paciente.nome = nome
            paciente.telefone = telefone
            paciente.email = email
            paciente.data_nascimento = data_nascimento
            paciente.endereco = endereco
            paciente.cidade = cidade
            paciente.estado = estado
            paciente.observacoes = observacoes
            paciente.save()

    return redirect('home')


def agendar_consulta(request):
    contexto = _get_context()
    contexto['mensagem'] = None

    if request.method == 'POST':
        try:
            _salvar_consulta(request)
            return redirect('agendar_consulta')
        except (Paciente.DoesNotExist, Profissional.DoesNotExist, ValueError):
            contexto['mensagem'] = 'Não foi possível criar a consulta. Verifique os dados informados.'

    return render(request, 'index.html', contexto)


def editar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    contexto = _get_context()
    contexto['consulta'] = consulta
    contexto['mensagem'] = None

    if request.method == 'POST':
        try:
            _salvar_consulta(request, consulta=consulta)
            return redirect('agendar_consulta')
        except (Paciente.DoesNotExist, Profissional.DoesNotExist, ValueError):
            contexto['mensagem'] = 'Não foi possível atualizar a consulta. Verifique os dados informados.'

    return render(request, 'editar_consulta.html', contexto)


def detalhes_consulta(request, consulta_id):
    consulta = get_object_or_404(
        Consulta.objects.select_related('paciente', 'profissional'),
        id=consulta_id
    )
    return render(request, 'detalhes_consulta.html', {'consulta': consulta})


def excluir_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)

    if request.method == 'POST':
        consulta.delete()
        return redirect('agendar_consulta')

    return redirect('agendar_consulta')
