from django.db import migrations, models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('providers', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='stars',
            field=models.DecimalField(
                default=Decimal('0.00'),
                max_digits=3,
                decimal_places=2,
                validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
            ),
        ),
    ]

