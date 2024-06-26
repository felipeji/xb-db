import glob
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
    
from modules.plotutils import skymap_gen
from .models import Spect, Object 

import numpy as np

from trm.molly import rmolly
from astropy.coordinates import SkyCoord
import astropy.units as u
import pandas as pd
import plotly.graph_objects as go
import pandas as pd

from django.contrib import messages
from django.shortcuts import render, redirect


def upload(request):
    if request.method == 'POST':
        spectra_files = request.FILES.getlist('spectraFile')  # Get a list of uploaded files
        save_directory = os.path.join(settings.BASE_DIR, 'dotmol', 'uploaded')
        for spectra_file in spectra_files:
            with open(os.path.join(save_directory, spectra_file.name), 'wb+') as destination:
                for chunk in spectra_file.chunks():
                    destination.write(chunk)    
        return redirect('data_ingestion:upload')
    uploaded_files = []

    save_directory = os.path.join(settings.BASE_DIR, 'dotmol', 'uploaded')

    dotmol_list = glob.glob(save_directory+"/*.mol")
    

    for filename in os.listdir(save_directory):
        file_path = os.path.join(save_directory, filename)
        uploaded_files.append({
            'name': filename,
            'url': f"/dotmol/uploaded{filename}",
        })



    # Blank version of the web
    if not dotmol_list:
        context = {'uploaded_files': '', 
        'skymap_div': '',
        'wl_range_div': '',
        'timeline_div': '', 
        'total_files': '',
        'total_spect': '',
        'total_objects': '',
        'total_obs': '',
        'button_disabled': True,  

        }


    else:
        # Extract all the metadata    
        metadata_df = gen_metadata_df(dotmol_list)

        # 1) Sky maps

        # New ingested sources
        
        # Unique RA-Dec 
        df_ingested = metadata_df.drop_duplicates(subset=['ra', 'dec'])


        ra_deg_new = df_ingested['ra'].tolist()
        dec_deg_new = df_ingested['dec'].tolist()        
        object_new = df_ingested['object'].tolist()
        color_new = ['red' for _ in object_new]
        symbol_new = ['circle-open' for _ in object_new]


        # Objects in the database        
        # Query all objects and extract RA, Dec, and pretty_name
        objects_data = Object.objects.values_list('ra', 'dec', 'pretty_name')

        ra_deg_db = [obj[0] for obj in objects_data]
        dec_deg_db = [obj[1] for obj in objects_data]
        object_db = [obj[2] for obj in objects_data]
        color_db =  ['black' for _ in object_db]
        symbol_db = ['star' for _ in object_db]

        ra_deg = ra_deg_new + ra_deg_db
        dec_deg = dec_deg_new + dec_deg_db
        object = object_new + object_db
        symbol = symbol_new + symbol_db
        color = color_new + color_db

        # Generate sky map
        skymap_div = skymap_gen(ra_deg, dec_deg, object, symbol, color)


        # 2) Wavelength ranges
        # Function for clustering by wavelenght
        def cluster_wavelength_ranges(metadata_df, threshold=30):
            min_wls = metadata_df['min_wl'].values
            max_wls = metadata_df['max_wl'].values

            min_values = []
            max_values = []

            min_wl_0, max_wl_0 = min_wls[0], max_wls[0]

            current_range = [min_wl_0, max_wl_0]

            for min_wl, max_wl in zip(min_wls, max_wls):
                if (np.abs(min_wl_0 - min_wl) > threshold) or (np.abs(max_wl_0 - max_wl) > threshold):
                    # Start a new range if the difference exceeds the threshold
                    min_values.append(current_range[0])
                    max_values.append(current_range[1])
                    min_wl_0, max_wl_0 = min_wl, max_wl
                    current_range = [min_wl_0, max_wl_0]
                else:
                    # Update the current range
                    current_range[1] = max_wl

            # Append the last range after the loop
            min_values.append(current_range[0])
            max_values.append(current_range[1])

            return [min_values, max_values]

        wl_ranges = cluster_wavelength_ranges(metadata_df, threshold=30)


        # Generate the plot
        wl_range_div = wl_range_gen(wl_ranges)


        # 3) Date of observations
        # Observation of the same object from the same site
        metadata_df['site-object'] = metadata_df.groupby(['object', 'site']).ngroup()

        metadata_df.sort_values(by='jd', inplace=True)

        

        # Lets now define the OB clustering over JD
        site_objects = metadata_df['site-object'].unique()  


        threshold = 0.5 # 12hs diferences

        ob = 1
        obs = []

        for site_object in site_objects:
            # Extracting the selected columns
            JDs = metadata_df.loc[metadata_df['site-object'] == site_object, 'jd'].values

            JD_0 = JDs[0]

            for JD in JDs:
                if np.abs(JD-JD_0) < threshold:
                    obs.append(ob)
                else:
                    ob += 1
                    obs.append(ob)
                JD_0 = JD

            ob += 1

        metadata_df['OB'] = obs

        timeline_div = timeline_gen(metadata_df)


        # 4) Sumary info 
        # Total spectra readed
        total_files = len(dotmol_list)

        # Total spectra readed
        total_spect = len(metadata_df)
        # Total spectra read
        total_objects = len(np.unique(metadata_df['object']))


        # Total OBs detected
        total_obs = len(np.unique(metadata_df['OB']))


        context = {'uploaded_files': uploaded_files, 
                'skymap_div': skymap_div,
                'wl_range_div': wl_range_div,
                'timeline_div': timeline_div, 
                'total_files': total_files,
                'total_spect': total_spect,
                'total_objects': total_objects,
                'total_obs': total_obs,
                'button_disabled': False,  
                }


    # Check for success messages
    success_messages = [str(message) for message in messages.get_messages(request)]
    if success_messages:
        context['success_message'] = success_messages[0]

    return render(request, 'data_ingestion/upload.html', context)

import os

def push_button(request):
    
    save_directory = os.path.join(settings.BASE_DIR, 'dotmol', 'uploaded')
    database_dir = os.path.join(settings.BASE_DIR, 'dotmol', 'database')

    dotmol_list = glob.glob(save_directory+"/*.mol")
    metadata_df = gen_metadata_df(dotmol_list)

    # Move files to databed directory
    
    os.system('mv ' + save_directory + '/*.mol '+ database_dir + '/.')



    # All the detected objects
    objects = metadata_df['object'].unique()

    total_spect = 0
    for object in objects:
        # Filter the metadata table by object
        selected_metadata_df = metadata_df[metadata_df['object'] == object]
        # RA and Dec should be the same for the same object, so we take the first one
        ra = selected_metadata_df['ra'].iloc[0]
        dec = selected_metadata_df['dec'].iloc[0]

        # TODO set proper name and pretty name by user
        name = object
        pretty_name = object

        try:
            # Try to retrieve the object if it already exists
            object_instance = Object.objects.get(name=name)
            
        except ObjectDoesNotExist:
            # If the object doesn't exist, create a new one
            object_instance = Object.objects.create(
                name=name,
                pretty_name=pretty_name,
                ra=ra,
                dec=dec,
            )
        
        for index, row in metadata_df.iterrows():

            try:
                # Assuming you have already read these values in your view
                exptime = row['exptime']  # Your exptime value
                min_wavelength = row['min_wl']  # Your min_wavelength value
                max_wavelength = row['max_wl']  # Your max_wavelength value
                file = row['file']  # Your file value
                header_value = 'long header'  # Your header value
                jd = row['jd']  # Your jd value
                hjd = row['hjd']  # Your hjd value
                index = row['index']  # Your hjd value

                # Create a Spect
                Spect.objects.create(
                    object=object_instance,
                    exptime=exptime,
                    min_wavelenght=min_wavelength,
                    max_wavelenght=max_wavelength,
                    file=file,
                    header=header_value,
                    jd=jd,
                    hjd=hjd,
                    index=index,
                )
                
                # Count the spectra
                total_spect += 1

            except IntegrityError:
                pass
            
    # Use Django messages framework to store a success message
    messages.success(request, str(total_spect) + ' spectra successfully ingested in the database!')

    # Return an HTTP response indicating success
    return redirect('data_ingestion:upload')





def timeline_gen(df):
    # Ensure the 'jd' column is in datetime format
    ob = np.array(df['OB'].tolist())

    # Create figure
    fig = go.Figure()

    # Add individual scatter points for each OB
    for unique_ob in set(ob):
        ob_df = df[df['OB'] == unique_ob]
        fig.add_trace(
            go.Scatter(
                x=ob_df['jd'] - 2400000.5,
                y=[unique_ob] * len(ob_df),
                mode='markers',
                marker=dict(
                    size=8,
                ),
                name=f'OB {unique_ob}',
                text=f'OB {unique_ob} ({len(ob_df)} spectra)',
                hoverinfo='text'
            )
        )

    # Create layout
        fig.update_layout(
        title=dict(text='Timeline-OBs', y=0.95),
        legend=dict(x=0, y=1.2),  
        margin=dict(l=0, r=0, b=100, t=100),  # Adjust margin values as needed
        autosize=True,
        xaxis=dict(title='Date (MJD)',
                   exponentformat='none',
        ),
        yaxis=dict(title='OB number'),
        showlegend=False
    )

    # Generate HTML div
    plot_div = fig.to_html(full_html=False)
    
    return plot_div


def gen_metadata_df(dotmol_list):
    
    metadata = []
        
    for i, dotmol in enumerate(dotmol_list):
        file = dotmol.split("/")[-1]

        # Read spectra
        mol = rmolly(dotmol)
        for index, i in enumerate(mol):
            # Requiered files
            # exptime = models.FloatField()
            # min_wavelenght = models.FloatField()
            # max_wavelenght = models.FloatField()
            # file = models.FileField()
            # header = models.TextField()
            # jd = models.FloatField()
            # hjd = models.FloatField()
            # index = models.IntergerField()


            object = i.head['Object']

            # Coordinates o
            ra = float(i.head['RA']) # Right ascension (decimal hours)
            dec = float(i.head['DEC']) # Declination (decimal degrees)
            equinox = 'J2000'# i.head['Equinox'] TODO

            # Create SkyCoord instance
            coord = SkyCoord(ra=ra * u.hourangle, dec=dec * u.deg, equinox=equinox)

            jd = i.head['RJD']
            hjd = i.head['HJD']
            exptime = i.head['Dwell'] 
            site = i.head['Site'] 
            min_wavelength = min(i.wave)
            max_wavelength = max(i.wave)

            item_dict = {
                'object': object,
                'ra': ra,
                'dec': dec,
                'equinox': equinox,
                'jd': jd,
                'hjd': hjd,
                'exptime': exptime,
                'min_wl': min_wavelength,
                'max_wl': max_wavelength,
                'coord': coord,
                'site': site,
                'file': file,
                'index': int(index), # Start in 1 instead of 0

            }

            # Append the dictionary to the list
            metadata.append(item_dict)

        # Create metadata data frame 
        metadata_df = pd.DataFrame(metadata)

        # Sort DataFrame by JD
        metadata_df.sort_values(by='jd', inplace=True)



    return metadata_df





def wl_range_gen(wl_ranges):

    min_wl = wl_ranges[0]
    max_wl = wl_ranges[1]

    spect_number = np.arange(len(min_wl)) + 1

    min_limit = min(min_wl) * 0.9
    max_limit = max(max_wl) * 1.1


    # Create a figure
    fig = go.Figure()



    # Define wavelength ranges
    uv_range = (1000, 3800)
    visible_range = (3800, 7500)
    nir_ir_range = (7500, 25000)

    # Add colored background for UV range
    fig.add_shape(
        type='rect',
        x0=uv_range[0],
        x1=uv_range[1],
        y0=-1,
        y1=len(min_wl),
        fillcolor='#E8DAEF',
        opacity=1,
        layer='below',
        line=dict(width=0),
    )

    # Add colored background for visible range
    fig.add_shape(
        type='rect',
        x0=visible_range[0],
        x1=visible_range[1],
        y0=-1,
        y1=len(min_wl),
        fillcolor='#F8F9F9',
        opacity=1,
        layer='below',
        line=dict(width=0),
    )

    # Add colored background for NIR/IR range
    fig.add_shape(
        type='rect',
        x0=nir_ir_range[0],
        x1=nir_ir_range[1],
        y0=-1,
        y1=len(min_wl),
        fillcolor='#FADBD8',
        opacity=1,
        layer='below',
        line=dict(width=0),
    )


    # # Add title annotations for each range
    # uv_title = f"UV"
    # visible_title = f"Visible"
    # nir_ir_title = f"NIR/IR"

    # fig.add_annotation(
    #     text=uv_title,
    #     xref='x',
    #     yref='paper',
    #     x=(uv_range[0] + uv_range[1]) / 2,
    #     y=1.05,
    #     showarrow=False,
    #     font=dict(size=16),
    # )

    # fig.add_annotation(
    #     text=visible_title,
    #     xref='x',
    #     yref='paper',
    #     x=(visible_range[0] + visible_range[1]) / 2,
    #     y=1.05,
    #     showarrow=False,
    #     font=dict(size=16),
    # )

    # fig.add_annotation(
    #     text=nir_ir_title,
    #     xref='x',
    #     yref='paper',
    #     x=(nir_ir_range[0] + nir_ir_range[1]) / 2,
    #     y=1.05,
    #     showarrow=False,
    #     font=dict(size=16),
    # )



    # Add horizontal segments for each wavelength range
    for i in range(len(min_wl)):
        fig.add_trace(
            go.Scatter(
                x=[min_wl[i], max_wl[i]],
                y=[i, i],
                mode='lines',  # Change mode to 'lines'
                line=dict(width=2),  # Use different color and thinner lines
                hoverinfo='x',  # Exclude 'text' from hover information
                name=f'{spect_number[i]} spectr{"a" if spect_number[i] != 1 else "um"}',
                error_y=dict(
                    type='constant',  # Add vertical constant error bars
                    value=0.05,  # Adjust the length of the vertical caps
                    width=0,
                    thickness=2,  # Thickness of the caps
                )
            )
        )

    # Customize layout
    fig.update_layout(
        title=dict(text='Wavelenght range', y=0.95),
        legend=dict(x=0, y=1.2),  
        margin=dict(l=0, r=0, b=100, t=100),  # Adjust margin values as needed
        autosize=True,
 
         yaxis=dict(
            showticklabels=False,  # Hide y-axis tick labels
            tickmode='array',
        ),
        xaxis=dict(title='Wavelength (Å)',
        exponentformat='none',
        range=[min_limit, max_limit],  # Set x-axis limits
),
    )

    plot_div = fig.to_html(full_html=False)
    return plot_div



def remove(request, filename):
    save_directory = os.path.join(settings.BASE_DIR, 'dotmol', 'uploaded')
    file_path = os.path.join(save_directory, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect('data_ingestion:upload')
