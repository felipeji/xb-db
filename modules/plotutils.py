from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
import plotly.graph_objects as go


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
