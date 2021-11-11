from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20211002_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
