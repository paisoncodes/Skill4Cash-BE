# Generated by Django 3.2.9 on 2022-09-15 12:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_auto_20220804_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=225, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.AlterField(
            model_name='user',
            name='service_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.category'),
        ),
    ]
