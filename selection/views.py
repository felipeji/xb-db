from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import json
from trm.molly import rmolly
import plotly.graph_objs as go
import os
from data_ingestion.models import Spect, Object
from django.conf import settings
from selection.line_list import H, He, sky




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

    
    # Read .mol spectra data for each selected spectrum and store in wave_data and flux_data determining the wavelength range of the whole set
    w_range = [np.inf, -np.inf]

    for selected_spect in spect_objects:
        file = str(selected_spect.file)
        file_path = os.path.join(settings.BASE_DIR, 'dotmol', 'database', file)
            
        slot = selected_spect.slot
        wave, flux = read_spec(file_path, slot)

        # Check max and min
        w_range[0] = min(w_range[0],min(wave))
        w_range[1] = max(w_range[1],max(wave))


        name = 'File: ' + file + '    Slot: ' + str(slot)
        trace = go.Scatter(x=wave, y=flux, mode='lines', line_shape='hvh', name=name)
        
        traces.append(trace)


    # Create a Plotly layout
    layout = go.Layout( xaxis=dict(title=r'Wavelength (Å)'), yaxis=dict(title='Intensity'))

    # Create a Plotly figure
    fig = go.Figure(data=traces, layout=layout)

    # Call spec_lines function to add vertical line
    # List of transitions
    transitions = [
        [H.balmer, "Balmer",'black'],
        [H.paschen, "Pashen", 'black'],
        [He.I, "HeI", 'black'],
        [He.II, "HeII", 'black'],
        [sky.sky, "Sky lines", '#3498DB'],

    ]
    spec_line(fig, w_range,transitions)



    return fig.to_html(full_html=False)



def spec_line(figure, w_range, transitions):
    buttons = [
        dict(
            label="None",
            method="relayout",
            args=["shapes", []]
        )
    ]

    all_shapes = []
    for transition in transitions:
        line_list = transition[0]
        button_label = transition[1]
        color = transition[2]

        lines = []
        for line in line_list:
            label = line[0]
            wavelength = line[1]
            if w_range[0] <= wavelength <= w_range[1]:
                lines.append(
                    dict(
                        type='line',
                        x0=wavelength,
                        y0=0,
                        x1=wavelength,
                        y1=1,
                        line=dict(color=color, width=2, dash='dash'),
                        yref='paper',
                        label=dict(text=label,
                                   textposition="end",
                                   textangle="0",
                                   font = dict(size=15, color=color)
                                   ),
                    )
                )

        button = dict(
            label=button_label,
            method="relayout",
            args=["shapes", lines]
        )

        buttons.append(button)
        all_shapes.extend(lines)

    buttons.append(
        dict(
            label="All",
            method="relayout",
            args=["shapes", all_shapes],

        )
    )

    figure.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                buttons=buttons,
                direction = "left",  # Align the buttons horizontally
                x = 0.82,  # Position the buttons in the center
                y = 1.25,  # Adjust the vertical position of the buttons
                showactive=True,
                bgcolor='#E5E8E8',
                borderwidth=0,
                font=dict(size=14,color="#566573", family="verdana")
            )
        ],
        showlegend = True,
        annotations=[dict(text="Line marks",
                          x=0.02,
                          xref="paper",
                          y=1.24,
                          yref="paper",
                          align="left",
                          showarrow=False,
                          font=dict(size=16,color="#566573", family="verdana"),
                         )
                     ],
    )

