from django.urls import path
from . import views

app_name = 'selection'

urlpatterns = [
    path('process_selection/', views.process_selection, name='process_selection'),
]
