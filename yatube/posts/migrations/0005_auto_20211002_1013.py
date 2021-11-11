from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20211002_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
