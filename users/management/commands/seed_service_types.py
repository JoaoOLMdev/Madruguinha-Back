from django.core.management.base import BaseCommand
from services.models import ServiceType

SERVICE_TYPES = [
    'Encanamento',
    'Elétrica',
    'Limpeza',
    'Pintura',
    'Marcenaria',
    'Guincho',
    'Chaveiro',
]


class Command(BaseCommand):
    help = 'Seed only the ServiceType table with the default service categories.'

    def handle(self, *args, **options):
        created_count = 0
        for name in SERVICE_TYPES:
            _, created = ServiceType.objects.get_or_create(name=name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [+] Created: {name}'))
            else:
                self.stdout.write(f'  – Already exists: {name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {created_count} new service type(s) created, '
                f'{len(SERVICE_TYPES) - created_count} already existed.'
            )
        )
