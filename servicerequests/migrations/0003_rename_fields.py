from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicerequests', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='servicerequest',
            old_name='adress',
            new_name='address',
        ),
        migrations.RenameField(
            model_name='servicerequest',
            old_name='ServiceType',
            new_name='service_type',
        ),
    ]

