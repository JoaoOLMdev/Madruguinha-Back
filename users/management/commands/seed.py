from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from providers.models import Provider, ProviderApplication
from services.models import ServiceType
from servicerequests.models import ServiceRequest, Rating
from django.db import transaction
from django.utils import timezone
import random

try:
    from faker import Faker
except Exception:
    Faker = None

User = get_user_model()


def _make_cpf_cnpj():
    # Simple cpf_cnpj-like generator (not valid checksum), formatted
    return "{:03d}.{:03d}.{:03d}-{:02d}".format(
        random.randint(0, 999), random.randint(0, 999), random.randint(0, 999), random.randint(0, 99)
    )


SERVICE_TEMPLATES = {
    'Encanamento': {
        'provider': 'Encanador com experiência em instalação de torneiras, reparo de vazamentos e desentupimento. Atende residências e pequenos comércios, oferece orçamento no local e atendimento emergencial.',
        'request': 'Necessito de serviço de encanamento para {issue} em {address}. Preciso de atendimento {when} e prefiro orçamento de custo estimado de R${price}.'
    },
    'Elétrica': {
        'provider': 'Eletricista qualificado para instalações, troca de disjuntores, reparos em curtos-circuitos e manutenção elétrica predial. Trabalha com padrão de segurança, laudos quando necessário e serviços com garantia.',
        'request': 'Preciso de serviço elétrico para {issue} em {address}. Preferência por atendimento {when}; orçamento aproximado R${price}.'
    },
    'Limpeza': {
        'provider': 'Serviço de limpeza profissional para residências e escritórios: faxina, passagem de aspirador, limpeza profunda e organização. Fornece materiais se solicitado e trabalha por hora ou por projeto.',
        'request': 'Solicito serviço de limpeza para {issue} em {address}. Horário {when}. Estimativa de horas: {hours}h.'
    },
    'Pintura': {
        'provider': 'Pintor experiente em pintura interna e externa, preparação de superfícies, aplicação de massas e acabamento profissional. Fornece garantia limitada e orçamento por m².',
        'request': 'Necessito pintura para {issue} em {address}. Área aproximada {area}m²; posso agendar para {when}.'
    },
    'Marcenaria': {
        'provider': 'Marceneiro e carpinteiro para fabricação de móveis sob medida, reparos em portas e armários, montagem e acabamentos. Trabalha com diversos materiais e fornece projeto e orçamento detalhado.',
        'request': 'Preciso de serviços de marcenaria para {issue} em {address}. Material disponível: {material}; prioridade: {when}.'
    },
    'Guincho': {
        'provider': 'Serviço de guincho e reboque 24h para carros leves e motos. Atendimento rápido, transporte seguro até oficina ou local indicado, equipe treinada para manuseio de veículos avariados.',
        'request': 'Preciso de guincho para transporte de veículo em {address}. Situação: {issue}. Necessidade de atendimento {when} e indicação do destino para orçamento de valor.'
    },
    'Chaveiro': {
        'provider': 'Chaveiro experiente em abertura de portas, troca de fechaduras, cópia de chaves e instalação de fechaduras eletrônicas. Atende emergência com atendimento móvel e garantia no serviço.',
        'request': 'Necessito de serviço de chaveiro para {issue} em {address}. Preferência por atendimento {when} e possível substituição de peça conforme orçamento.'
    }
}


def provider_description_for(service_type_name, fake):
    tpl = SERVICE_TEMPLATES.get(service_type_name, None)
    if tpl:
        return tpl['provider']
    # fallback
    return fake.text(max_nb_chars=140)


def request_description_for(service_type_name, fake, address):
    tpl = SERVICE_TEMPLATES.get(service_type_name, None)
    when = random.choice(['urgente', 'na próxima semana', 'em duas semanas', 'o quanto antes'])
    price = random.randint(100, 2000)
    hours = random.randint(1, 8)
    area = random.randint(5, 60)
    material = random.choice(['madeira', 'MDF', 'compensado', 'metal'])
    issue = fake.sentence(nb_words=4)
    if tpl:
        return tpl['request'].format(issue=issue, address=address, when=when, price=price, hours=hours, area=area, material=material)
    return fake.paragraph(nb_sentences=3)


class Command(BaseCommand):
    help = 'Seed the database with realistic sample data for local testing (uses Faker)'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear seeded data before creating')
        parser.add_argument('--users', type=int, default=10, help='Number of users to create (default: 10)')
        parser.add_argument('--providers', type=int, default=3, help='Number of providers to create (default: 3)')
        parser.add_argument('--locale', type=str, default='pt_BR', help='Faker locale to use (default: pt_BR)')

    def handle(self, *args, **options):
        if Faker is None:
            self.stderr.write('Faker is not installed. Add Faker to your environment (pip install Faker)')
            return

        fake = Faker(options.get('locale') or 'pt_BR')

        clear = options['clear']
        users_count = options['users']
        providers_count = options['providers']

        if clear:
            self.stdout.write('Clearing existing seeded data...')
            self._clear_seeded()

        self.stdout.write('Seeding service types...')
        service_types = self._create_service_types()

        self.stdout.write('Creating admin user...')
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={'username': 'admin', 'first_name': 'Admin', 'last_name': 'User'}
        )
        if created:
            admin.set_password('adminpass')
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()

        self.stdout.write(f'Creating {users_count} regular users...')
        users = []
        for i in range(users_count):
            first = fake.first_name()
            last = fake.last_name()
            # use dots and index to ensure uniqueness
            email = f'{first.lower()}.{last.lower()}.{i}@example.com'
            # generate and sanitize phone to fit model field (max_length=15)
            raw_phone = getattr(fake, 'phone_number', lambda: '')()
            if raw_phone is None:
                raw_phone = ''
            # keep digits and plus sign, remove spaces, parentheses, etc.
            phone_digits = ''.join(ch for ch in raw_phone if ch.isdigit() or ch == '+')
            phone = phone_digits[:15]

            defaults = {
                'username': email,
                'first_name': first,
                'last_name': last,
                'phone_number': phone or None,
                'address': fake.address().replace('\n', ', '),
                'birth_date': fake.date_of_birth(minimum_age=18, maximum_age=75),
            }

            try:
                u, created = User.objects.get_or_create(email=email, defaults=defaults)
            except Exception as exc:
                # In case of unexpected DB constraints, log and skip this user
                self.stderr.write(f'Failed to create user {email}: {exc}')
                continue
            if created:
                u.set_password('password')
                u.save()
            users.append(u)

        self.stdout.write(f'Creating {providers_count} providers...')
        providers = []
        for idx, user in enumerate(users[:providers_count]):
            cpf_cnpj = _make_cpf_cnpj()
            p, created = Provider.objects.get_or_create(
                user=user,
                defaults={
                    'description': '',
                    'cpf_cnpj': cpf_cnpj,
                    'is_active': True,
                }
            )
            if created:
                # assign a random service type and set description based on it
                chosen = random.sample(list(service_types), k=1)
                p.service_types.set(chosen)
                svc_name = chosen[0].name
                p.description = provider_description_for(svc_name, fake)
                p.save()
            providers.append(p)

        self.stdout.write('Creating some provider applications...')
        for user in users[providers_count:]:
            cpf_cnpj = _make_cpf_cnpj()
            chosen = random.sample(list(service_types), k=1)
            app_desc = provider_description_for(chosen[0].name, fake)
            app, created = ProviderApplication.objects.get_or_create(
                applicant=user,
                cpf_cnpj=cpf_cnpj,
                defaults={'description': app_desc}
            )
            if created:
                app.service_types.set(chosen)
                app.save()

        self.stdout.write('Creating some service requests and ratings...')
        for i in range(15):
            client = random.choice(users)
            service_type = random.choice(service_types)
            title = fake.sentence(nb_words=6)
            addr = fake.address().replace('\n', ', ')
            sr = ServiceRequest.objects.create(
                title=title,
                description=request_description_for(service_type.name, fake, addr),
                address=addr,
                client=client,
                service_type=service_type,
                requested_date=timezone.now(),
                status=random.choice([ServiceRequest.STATUS_PENDING, ServiceRequest.STATUS_IN_PROGRESS, ServiceRequest.STATUS_COMPLETED])
            )

            if providers and random.random() < 0.6:
                sr.provider = random.choice(providers)
                if sr.status == ServiceRequest.STATUS_PENDING:
                    sr.status = ServiceRequest.STATUS_IN_PROGRESS
                sr.save()

            if sr.status == ServiceRequest.STATUS_COMPLETED and sr.provider:
                score = round(random.uniform(3.0, 5.0), 2)
                Rating.objects.create(
                    service_request=sr,
                    provider=sr.provider,
                    reviewer=sr.client,
                    score=score,
                    comment=fake.sentence(nb_words=12)
                )

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))

    def _create_service_types(self):
        names = ['Encanamento', 'Elétrica', 'Limpeza', 'Pintura', 'Marcenaria']
        objs = []
        for name in names:
            obj, created = ServiceType.objects.get_or_create(name=name)
            objs.append(obj)
        return objs

    def _clear_seeded(self):
        Rating.objects.all().delete()
        ServiceRequest.objects.all().delete()
        ProviderApplication.objects.all().delete()
        Provider.objects.all().delete()
        ServiceType.objects.filter(name__in=['Encanamento', 'Elétrica', 'Limpeza', 'Pintura', 'Marcenaria']).delete()
        User.objects.filter(email__endswith='@example.com').delete()