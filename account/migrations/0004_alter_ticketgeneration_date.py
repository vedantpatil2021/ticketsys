# Generated by Django 4.0.2 on 2022-04-04 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_ticketgeneration_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketgeneration',
            name='date',
            field=models.CharField(max_length=250),
        ),
    ]
