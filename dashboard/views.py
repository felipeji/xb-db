from django.shortcuts import render
from data_ingestion.models import Spect, Object
from modules.plotutils import skymap_gen

# Create your views here.

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import json
from data_ingestion.models import Spect
from modules.plotutils import *


@csrf_exempt
def dashboard(request):

    if request.method == "POST":
        # Retrieve the value of the wavelength from the POST parameters
        wavelength = request.POST.get('wavelength')
    
        # Retrieve the list of selected row IDs from the POST parameters
        selected_ids = np.int_(json.loads(request.POST["selected_rows"]))

        # Filter Selected Spectra
        selected_spect = Spect.objects.filter(spect_id__in=selected_ids)

        # Produce plots
        wave_spect_plot, vel_spect_plot = spect_plot(selected_spect, wavelength)


    else:

        # Produce plots
        wave_spect_plot, vel_spect_plot = '',''



    spect_objects = Spect.objects.all()
    object_objects = Object.objects.all()

    # Set Sky Map with all the objects in the database
    objects_data = Object.objects.values_list("ra", "dec", "pretty_name")

    ra_deg = [obj[0] for obj in objects_data]
    dec_deg = [obj[1] for obj in objects_data]
    object = [obj[2] for obj in objects_data]
    color = ["blue" for _ in object]
    symbol = ["star" for _ in object]

    # Generate sky map
    skymap_div = skymap_gen(
        ra_deg,
        dec_deg,
        object,
        symbol,
        color,
        height=140,
        width=300,
        showlegend=False,
        mark_size=8,
    )

    # Total spectra
    total_spectra = Spect.objects.all().count()

    # Total objects
    total_objects = Object.objects.all().count()

    context = {
        "spect_objects": spect_objects,
        "object_objects": object_objects,
        "skymap_div": skymap_div,
        "total_spectra": total_spectra,
        "total_objects": total_objects,
        "wave_spect_plot": wave_spect_plot,
        "vel_spect_plot": vel_spect_plot, 

    }
    return render(request, "dashboard.html", context=context)

