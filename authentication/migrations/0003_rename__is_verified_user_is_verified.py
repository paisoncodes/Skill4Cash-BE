# Generated by Django 3.2.9 on 2022-06-18 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20220618_1334'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='_is_verified',
            new_name='is_verified',
        ),
    ]
