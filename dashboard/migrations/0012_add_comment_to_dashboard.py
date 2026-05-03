# Generated manually to add the optional comment field to Dashboard

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_add_description_to_dashboard'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='comment',
            field=models.TextField(blank=True, default=''),
        ),
    ]
