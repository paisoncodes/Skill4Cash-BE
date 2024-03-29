# Generated by Django 3.2.9 on 2023-04-05 13:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=225, unique=True)),
                ('image', models.URLField(default='https://res.cloudinary.com/skill4cash/image/upload/v1/profile/default')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=225, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=25)),
                ('country', models.CharField(default='NIGERIA', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Lga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lga', models.CharField(max_length=25)),
                ('country', models.CharField(default='NIGERIA', max_length=50)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='utils.state')),
            ],
        ),
    ]
