from django.urls import path
from . import views
from .views import download_selected_spectra

urlpatterns = [
 path('', views.dashboard, name='dashboard'),
 path('download_selected_spectra/', download_selected_spectra, name='download_selected_spectra'),
]
