from django.shortcuts import render
from data_ingestion.models import Spect, Object

# Create your views here.


def dashboard(request):
    spect_objects = Spect.objects.all()
    object_objects = Object.objects.all()

    # You can further filter, order, or manipulate the queryset as needed

    context = {
        'spect_objects': spect_objects,
        'object_objects': object_objects,
    }
    return render(request, 'dashboard.html', context=context)
