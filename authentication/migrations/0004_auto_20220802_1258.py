# Generated by Django 3.2.9 on 2022-08-02 11:58

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_auto_20220802_1258'),
        ('authentication', '0003_rename__is_verified_user_is_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='business_name',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='card_back',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='card_front',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gallery',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=225), default=list, size=None),
        ),
        migrations.AddField(
            model_name='user',
            name='is_verified_business',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='keywords',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=225), default=list, size=None),
        ),
        migrations.AddField(
            model_name='user',
            name='pob',
            field=models.CharField(blank=True, max_length=225, null=True, verbose_name='Proof of business'),
        ),
        migrations.AddField(
            model_name='user',
            name='service_category',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('customer', 'customer'), ('service_provider', 'service_provider')], max_length=20),
        ),
        migrations.DeleteModel(
            name='ServiceProvider',
        ),
    ]
