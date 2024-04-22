from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import plotly.graph_objects as go
from django.conf import settings
from modules.line_list import H, He, sky
import astropy.units as u
from astropy.constants import c
from modules.io import read_molly
import plotly.graph_objs as go
import os

def skymap_gen(
    ra,
    dec,
    object,
    symbol,
    colors,
    height=None,
    width=None,
    showlegend=True,
    mark_size=12,
):

    # TODO add to hover
    # ra_str = coord.ra.to_string(u.hour, precision=2)
    # dec_str = coord.dec.to_string(u.degree, alwayssign=True, precision=2)

    # text = "<b>"+object+"</b><br> (RA,Dec) : ("+ra_str+','+ dec_str+")</br>"

    ra_wraped = []
    # Need to wrap ra first
    for i, j in zip(ra, dec):
        coord = SkyCoord(ra=i * u.hourangle, dec=j * u.deg, equinox="J2000")
        ra_wraped.append(coord.ra.wrap_at(180 * u.deg).degree)

    # Plot

    grid_ra_x = [-180, -150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150]

    grid_ra_x = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]

    grid_ra_y = [0] * len(grid_ra_x)

    grid_dec_x = [0] * len(grid_ra_x)
    grid_dec_y = [-90, -60, -30, 0, 30, 60, 90]

    # Create a line representing the Galactic plane
    l = np.linspace(0, 360, 1000)
    b = np.zeros_like(l)
    galactic_plane = SkyCoord(l=l * u.deg, b=b * u.deg, frame="galactic")
    icrs_coords = galactic_plane.transform_to("fk5")
    galactic_plane_ra = icrs_coords.ra.wrap_at(180 * u.deg).degree
    galactic_plane_dec = icrs_coords.dec.degree

    # Plot
    # TODO Set diferent legend for new ingested objets and Object in the database
    mytrace = [
        go.Scattergeo(
            mode="markers",
            name="Uploaded objects",
            lon=ra_wraped,
            lat=dec,
            text=object,
            hoverinfo="text",
            marker=dict(
                symbol=symbol,
                size=mark_size,
                color=colors,
            ),
        ),
        # Galactic plane line
        go.Scattergeo(
            mode="lines",
            lon=galactic_plane_ra,
            lat=galactic_plane_dec,
            line=dict(color="black", width=1, dash="dot"),
            name="Galactic Plane",
            # visible='legendonly',  # Set to 'legendonly' to hide by default
        ),
        go.Scattergeo(
            mode="text",
            lon=grid_ra_x,
            lat=grid_ra_y,
            # text=['180°', '150°', '120°', '90°', '60°', '30°', '0°', '330°', '300°', '270°', '240°', '210°'],
            text=[
                "0h",
                "2h",
                "4h",
                "6h",
                "8h",
                "10h",
                "12h",
                "14h",
                "16h",
                "18h",
                "20h",
                "22h",
            ],
            hoverinfo="none",
            textfont=dict(size=8, color="#696969"),
            showlegend=False,
        ),
        go.Scattergeo(
            mode="text",
            lon=grid_dec_x,
            lat=grid_dec_y,
            text=["-90°", "-60°", "-30°", "0°", "+30°", "+60°", "+90°"],
            hoverinfo="none",
            textfont=dict(size=8, color="#696969"),
            showlegend=False,
        ),
    ]

    mylayout = go.Layout(
        # Set height and width of the graph
        height=height,  # Adjust as needed
        width=width,  # Adjust as needed
        # title=dict(text='Object location', y=0.95),
        legend=dict(x=0, y=0.85),
        margin=dict(l=1, r=1, b=0, t=0),  # Adjust margin values as needed
        autosize=True,
        geo=dict(
            projection=dict(type="aitoff"),
            lonaxis=dict(
                showgrid=True, tick0=0, dtick=15, gridcolor="#aaa", gridwidth=1
            ),
            lataxis=dict(
                showgrid=True, tick0=90, dtick=30, gridcolor="#aaa", gridwidth=1
            ),
            showcoastlines=False,
            showland=False,
            showrivers=False,
            showlakes=False,
            showocean=False,
            showcountries=False,
            showsubunits=False,
        ),
        showlegend=showlegend,
    )

    plot_div = go.Figure(data=mytrace, layout=mylayout).to_html(full_html=False)

    return plot_div





def spect_plot(spect_objects, wavelength):
    traces_wave = []
    traces_vel = []
    w_range = [np.inf, -np.inf]


    if spect_objects is not None:
        for selected_spect in spect_objects:
            # Get the next color from the cycle

            file = str(selected_spect.file)
            file_path = os.path.join(settings.BASE_DIR, "dotmol", "database", file)
            index = selected_spect.index
            wave, flux = read_molly(file_path, index)

            # Check max and min wavelength
            w_range[0] = min(w_range[0], min(wave))
            w_range[1] = max(w_range[1], max(wave))

            name = f"File: {file}    Index: {index}"

            # Wavelength plot
            trace_wave = go.Scatter(
                x=wave, y=flux, mode="lines", line_shape="hvh", name=name
            )
            traces_wave.append(trace_wave)

            # Velocity plot
            trace_vel = go.Scatter(
                x=wave, y=flux, mode="lines", line_shape="hvh", name=name
            )
            traces_vel.append(trace_vel)

    # Layouts
    layout_wave = go.Layout(
        xaxis=dict(title="Wavelength (Å)"),
        yaxis=dict(title="Intensity"),
        showlegend=False, 
    )
    layout_vel = go.Layout(
        xaxis=dict(
            title="Velocity (km/s)",
        ),
        yaxis=dict(title="Intensity"),
    )

    # Figures
    fig_wave = go.Figure(data=traces_wave, layout=layout_wave)
    fig_vel = go.Figure(data=traces_vel, layout=layout_vel)

    # Plot reference lines in wavelenght representation
    # List of transitions
    transitions = [
        [range_filter(H.balmer, w_range), "Balmer", "black"],
        [range_filter(H.paschen, w_range), "Pashen", "black"],
        [range_filter(He.I, w_range), "HeI", "black"],
        [range_filter(He.II, w_range), "HeII", "black"],
        [range_filter(sky.sky, w_range), "Sky lines", "#3498DB"],
    ]


    fig_vel.update_layout(
        margin=dict(l=20, r=20, t=10, b=0),
        modebar=dict(remove=["zoomout", "zoomin",],orientation='v',visible=True,),
        width=610,
        height=410,
        xaxis=dict(
            rangeslider=dict(visible=True),
        ),
    )

    fig_wave.update_layout(
        margin=dict(l=20, r=20, t=100, b=0),
        modebar=dict(remove=["zoomout", "zoomin",],orientation='v'),
        width=610,
        height=500,
    )


    # lambda_buttons(fig_vel, transitions)
    spec_line(fig_wave, transitions)
    wave_to_vel(fig_vel, wavelength)


    fig_wave.update_traces(showlegend=False)  
    fig_vel.update_traces(showlegend=False)  

    return fig_wave.to_html(full_html=False), fig_vel.to_html(full_html=False)




def spec_line(figure, transitions):
    buttons = [dict(label="None", method="relayout", args=["shapes", []])]

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
                    type="line",
                    x0=wavelength,
                    y0=0,
                    x1=wavelength,
                    y1=1,
                    line=dict(color=color, width=2, dash="dash"),
                    yref="paper",
                    label=dict(
                        text=label,
                        textposition="end",
                        textangle="0",
                        font=dict(size=15, color=color),
                    ),
                )
            )

        button = dict(label=button_label, method="relayout", args=["shapes", lines])

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
                direction="left",  # Align the buttons horizontally
                x=0.96,  # Position the buttons in the center
                y=1.25,  # Adjust the vertical position of the buttons
                showactive=True,
                bgcolor="#E5E8E8",
                borderwidth=0,
                font=dict(size=14, color="#566573", family="verdana"),
            )
        ],
        annotations=[
                dict(
                    text="Line marks",
                    x=-0.1,
                    xref="paper",
                    y=1.24,
                    yref="paper",
                    align="left",
                    showarrow=False,
                    font=dict(size=16, color="#566573", family="verdana"),
                )
            ],    
    )



def range_filter(line_list, w_range):
    filtered = []
    for line in line_list:
        wavelength = line[1]
        if w_range[0] <= wavelength <= w_range[1]:
            filtered.append(line)
    return filtered



def wave_to_vel(figure, wavelength):
        try:
            lambda_0 = float(wavelength) * u.AA
        except:
            lambda_0 = 6562.8 * u.AA

        for trace in figure.data:
            trace.x = (c * ((trace.x * u.AA - lambda_0) / lambda_0)).to(u.km / u.s).value


    # # Add an initial label to the dropdown menu
    # initial_label = "Select λ₀"
    # buttons.insert(
    #     0,
    #     dict(
    #         label=initial_label,
    #         method="skip",
    #         args=[
    #             {
    #                 "visible": False,
    #             }
    #         ],
    #     ),
    # )

    # figure.update_layout(
    #     updatemenus=[
    #         dict(
    #             type="dropdown",
    #             buttons=buttons,
    #             direction="down",  # Align the buttons horizontally
    #             x=0.42,  # Position the buttons in the center
    #             y=1.25,  # Adjust the vertical position of the buttons
    #             showactive=True,
    #             bgcolor="#E5E8E8",
    #             borderwidth=0,
    #             font=dict(size=14, color="#566573", family="verdana"),
    #         )
    #     ]
    # )