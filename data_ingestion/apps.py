from django.apps import AppConfig


class DataIngestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_ingestion'  # Update to the new app name