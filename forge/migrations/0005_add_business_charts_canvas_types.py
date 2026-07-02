from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forge', '0004_add_category_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codeentry',
            name='type',
            field=models.CharField(
                choices=[
                    ('html_graphics', 'HTML Graphics'),
                    ('html_text', 'HTML / Text Panel'),
                    ('business_text', 'Business Text'),
                    ('business_charts', 'Business Charts'),
                    ('canvas', 'Canvas'),
                    ('dashboard_json', 'Dashboard JSON'),
                    ('sql', 'SQL Query'),
                    ('javascript', 'JavaScript'),
                    ('css', 'CSS'),
                    ('svg', 'SVG'),
                ],
                max_length=50,
            ),
        ),
    ]
