from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20210930_2221'),
    ]

    operations = [
        migrations.RenameField(
            model_name='group',
            old_name='titel',
            new_name='title',
        ),
    ]
