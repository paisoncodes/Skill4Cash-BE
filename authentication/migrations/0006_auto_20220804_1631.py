# Generated by Django 3.2.9 on 2022-08-04 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20220802_1808'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='location',
            new_name='state',
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(default='everywhere', max_length=100),
        ),
    ]
