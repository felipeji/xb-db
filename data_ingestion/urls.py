from django.urls import path
from . import views

app_name = 'data_ingestion'

urlpatterns = [
    path('data_ingestion/', views.upload, name='upload'),
    path('remove/<str:filename>/', views.remove, name='remove'),
    path('push_button/', views.push_button, name='push_button'),

]
