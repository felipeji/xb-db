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
import astropy.units as u
from astropy.constants import c




@csrf_exempt
def process_selection(request):
    
    if request.method == 'POST':
        # Retrieve the list of selected row IDs from the POST parameters
        selected_ids = np.int_(json.loads(request.POST['selected_rows']))
        
        # Filter Selected Spectra
        spect_objects = Spect.objects.filter(spect_id__in=selected_ids)

        # Priduce plots
        wave_spect_plot, vel_spect_plot  = spect_plot(spect_objects)


        # Pass the plot HTML and selected_spects to the template
        return render(request, 'selection.html', {'wave_spect_plot': wave_spect_plot, 'vel_spect_plot': vel_spect_plot })




def read_spec(file, slot):
    wave = rmolly(file)[slot-1].wave
    flux = rmolly(file)[slot-1].f
    return wave, flux




def spect_plot(spect_objects):
    traces_wave = []
    traces_vel = []
    w_range = [np.inf, -np.inf]

    for selected_spect in spect_objects:
        file = str(selected_spect.file)
        file_path = os.path.join(settings.BASE_DIR, 'dotmol', 'database', file)
        slot = selected_spect.slot
        wave, flux = read_spec(file_path, slot)

        # Check max and min wavelength
        w_range[0] = min(w_range[0], min(wave))
        w_range[1] = max(w_range[1], max(wave))

        name = f'File: {file}    Slot: {slot}'

        # Wavelength plot
        trace_wave = go.Scatter(x=wave, y=flux, mode='lines', line_shape='hvh', name=name)
        traces_wave.append(trace_wave)

        # Velocity plot
        trace_vel = go.Scatter(x=wave, y=flux, mode='lines', line_shape='hvh', name=name)
        traces_vel.append(trace_vel)


    # Layouts
    layout_wave = go.Layout(xaxis=dict(title='Wavelength (Å)'), yaxis=dict(title='Intensity'), )
    layout_vel = go.Layout(xaxis=dict(title='Velocity (km/s)', ), yaxis=dict(title='Intensity'),)



    # Figures
    fig_wave = go.Figure(data=traces_wave, layout=layout_wave)
    fig_vel = go.Figure(data=traces_vel, layout=layout_vel)

    
    # Plot reference lines in wavelenght representation
    # List of transitions
    transitions = [
        [range_filter(H.balmer, w_range), "Balmer",'black'],
        [range_filter(H.paschen, w_range), "Pashen", 'black'],
        [range_filter(He.I, w_range), "HeI", 'black'],
        [range_filter(He.II, w_range), "HeII", 'black'],
        [range_filter(sky.sky, w_range), "Sky lines", '#3498DB'],
    ]


    lambda_buttons(fig_vel, transitions)

    fig_vel.update_layout( width=1200, height=700,
    xaxis=dict( 
        rangeslider=dict( 
            visible=True
        ), 
        ) 
    ) 

    fig_wave.update_layout( width=1200, height=600,
    ) 


    spec_line(fig_wave, transitions) 

   

    return fig_wave.to_html(full_html=False), fig_vel.to_html(full_html=False)



def spec_line(figure, transitions):
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




def lambda_buttons(figure, transitions):
    buttons = []

    for transition in transitions:
        line_list = transition[0]

        for line in line_list:
            label = line[0]
            wavelength = line[1]

            lambda_0 = wavelength * u.AA

            # TODO IDK WHy limit to 3 but otherwise it will not work
            args  = [{"x": [(c * ((trace.x * u.AA - lambda_0) / lambda_0)).to(u.km/u.s).value ]} for trace in figure.data[0:3]] 
            
            button = dict(
                label= label + f" - {wavelength} Å",
                method="update",
                args=args  
            )
            buttons.append(button)

        # Add an initial label to the dropdown menu
        initial_label = "Select λ₀"
        buttons.insert(0, dict(label=initial_label, method="skip", args=[{"visible": False, }]))


        figure.update_layout(
            updatemenus=[
                dict(
                    type="dropdown",
                    buttons=buttons,
                    direction="down",  # Align the buttons horizontally
                    x=0.3,  # Position the buttons in the center
                    y=1.25,  # Adjust the vertical position of the buttons
                    showactive=True,
                    bgcolor='#E5E8E8',
                    borderwidth=0,
                    font=dict(size=14, color="#566573", family="verdana"),

                )
            ]
        )

def range_filter(line_list, w_range):
    filtered = []
    for line in line_list:
        wavelength = line[1]
        if w_range[0] <= wavelength <= w_range[1]:
            filtered.append(line)
    return filtered
