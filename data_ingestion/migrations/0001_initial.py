# Generated by Django 4.2.11 on 2024-04-17 08:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Object",
            fields=[
                (
                    "object_id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("name", models.CharField(max_length=30)),
                ("pretty_name", models.CharField(max_length=30)),
                ("ra", models.FloatField()),
                ("dec", models.FloatField()),
            ],
            options={
                "unique_together": {("ra", "dec")},
            },
        ),
        migrations.CreateModel(
            name="Spect",
            fields=[
                (
                    "spect_id",
                    models.AutoField(primary_key=True, serialize=False, unique=True),
                ),
                ("exptime", models.FloatField()),
                ("min_wavelenght", models.FloatField()),
                ("max_wavelenght", models.FloatField()),
                ("header", models.TextField()),
                ("jd", models.FloatField()),
                ("hjd", models.FloatField()),
                ("file", models.FileField(upload_to="")),
                ("slot", models.IntegerField()),
                ("sn", models.FloatField(blank=True, null=True)),
                ("instrument", models.CharField(blank=True, max_length=30, null=True)),
                ("outburts", models.BooleanField(blank=True, null=True)),
                ("ob", models.IntegerField(blank=True, null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("soft", "Soft"),
                            ("intermediate", "Intermediate"),
                            ("hard", "Hard"),
                        ],
                        default="soft",
                        max_length=12,
                    ),
                ),
                ("flux_calibrated", models.BooleanField(blank=True, null=True)),
                ("spect_resolution", models.FloatField(blank=True, null=True)),
                (
                    "object",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_ingestion.object",
                    ),
                ),
            ],
            options={
                "unique_together": {("object", "instrument", "jd")},
            },
        ),
    ]
