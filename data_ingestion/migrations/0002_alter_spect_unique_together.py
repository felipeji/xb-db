# Generated by Django 4.2.11 on 2024-04-18 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("data_ingestion", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="spect",
            unique_together={("object", "jd")},
        ),
    ]
