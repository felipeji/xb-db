# Generated by Django 4.2.5 on 2024-01-23 22:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_ingestion', '0005_alter_spect_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='spect',
            unique_together={('exptime', 'jd')},
        ),
    ]
