# Generated by Django 3.1 on 2020-11-19 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_covid19data', '0002_auto_20201107_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datacovid19item',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]