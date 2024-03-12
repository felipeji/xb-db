from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import json
from trm.molly import rmolly
import plotly.graph_objs as go
from dotmol.line_list import H, He, sky
import os
from data_ingestion.models import Spect, Object
from django.conf import settings




@csrf_exempt
def process_selection(request):
    

    # Data base dir

    if request.method == 'POST':
        # Retrieve the list of selected row IDs from the POST parameters
        selected_ids = np.int_(json.loads(request.POST['selected_rows']))
        
        # Filter Selected Spectra
        spect_objects = Spect.objects.filter(spect_id__in=selected_ids)


        # Convert the Plotly figure to HTML
        plot_div = create_plotly_figure(spect_objects)

        # Pass the plot HTML and selected_spects to the template
        return render(request, 'selection.html', {'plot_div': plot_div })




def read_spec(file, slot):
    wave = rmolly(file)[slot-1].wave
    flux = rmolly(file)[slot-1].f
    return wave, flux



def create_plotly_figure(spect_objects):
    """
    Create a Plotly figure for the given spectra.

    Args:
    - spect_objects: QuerySet containing the selected spectra objects

    Returns:
    - Plotly figure object
    """

    traces = []

    # Read .mol spectra data for each selected spectrum and store in wave_data and flux_data
    for selected_spect in spect_objects:
        file = str(selected_spect.file)
        file_path = os.path.join(settings.BASE_DIR, 'dotmol', 'database', file)
            
        slot = selected_spect.slot
        wave, flux = read_spec(file_path, slot)
        name = 'File: ' + file + '    Slot: ' + str(slot)
        trace = go.Scatter(x=wave, y=flux, mode='lines', line_shape='hvh', name=name)
        
        traces.append(trace)

    # Create a Plotly layout
    layout = go.Layout( xaxis=dict(title=r'Wavelength (Å)'), yaxis=dict(title='Intensity'))

    # Create a Plotly figure
    fig = go.Figure(data=traces, layout=layout).to_html(full_html=False)

    return fig
