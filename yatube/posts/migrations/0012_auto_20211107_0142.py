# Generated by Django 2.2.16 on 2021-11-06 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='comment',
        ),
    ]
