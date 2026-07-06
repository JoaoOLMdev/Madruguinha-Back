import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from providers.models import Provider
from services.models import ServiceType
from servicerequests.models import ServiceRequest, Rating

User = get_user_model()

MIN_RATINGS = 15


class Command(BaseCommand):
    help = 'Ensure the first N providers (default 3) have at least 15 ratings each.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--providers',
            type=int,
            default=3,
            help='Number of providers to target (default: 3)',
        )
        parser.add_argument(
            '--min-ratings',
            type=int,
            default=MIN_RATINGS,
            help='Minimum number of ratings each targeted provider should have (default: 15)',
        )

    def handle(self, *args, **options):
        n_providers = options['providers']
        min_ratings = options['min_ratings']

        providers = list(Provider.objects.all()[:n_providers])

        if not providers:
            self.stdout.write(self.style.WARNING('No providers found. Run the main seed first.'))
            return

        service_types = list(ServiceType.objects.all())

        for idx, provider in enumerate(providers):
            existing = provider.ratings.count()
            needed = min_ratings - existing

            if needed <= 0:
                self.stdout.write(
                    f'  Provider #{idx + 1} ({provider.user.email}): '
                    f'already has {existing} ratings. Skipping.'
                )
                continue

            self.stdout.write(
                f'  Provider #{idx + 1} ({provider.user.email}): '
                f'creating {needed} ratings...'
            )

            for r in range(needed):
                reviewer_email = f'reviewer.seed.p{idx}.{existing + r}@example.com'
                reviewer, created = User.objects.get_or_create(
                    email=reviewer_email,
                    defaults={
                        'username': reviewer_email,
                        'first_name': f'Reviewer{r}',
                        'last_name': f'P{idx}',
                    },
                )
                if created:
                    reviewer.set_password('password')
                    reviewer.save()

                svc_type = random.choice(service_types) if service_types else None

                sr = ServiceRequest.objects.create(
                    title=f'Servico de teste #{existing + r + 1}',
                    description='Solicitacao de servico gerada pelo seeder de avaliacoes.',
                    address='Rua Exemplo, 123 - Sao Paulo, SP',
                    client=reviewer,
                    service_type=svc_type,
                    provider=provider,
                    status=ServiceRequest.STATUS_COMPLETED,
                )

                score = round(random.uniform(3.5, 5.0), 2)
                Rating.objects.create(
                    service_request=sr,
                    provider=provider,
                    reviewer=reviewer,
                    score=score,
                    comment=f'Otimo servico! Avaliacao #{existing + r + 1}',
                )

            total = provider.ratings.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [+] Provider #{idx + 1} now has {total} ratings '
                    f'(stars: {provider.stars})'
                )
            )

        self.stdout.write(self.style.SUCCESS('\nDone.'))
