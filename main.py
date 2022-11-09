# -*- coding: utf-8 -*-

"""
- OK --> Detallar en el gráfico cuál es el punto de inicio y punto de fin de un viaje.*
- OK --> Configurar el zoom automático.
- Poner etiquetas de lugares frecuentes: ej: Marriott, Oficina, York, aeropuertos, etc.
- Correo con notificación de ejecución
- Informe de sitios turísticos.
- OK --> Averiguar cuando se cuenta como Parqueo y cuando no.
- Alison: placas con el tipo de vehículo y creación de carpetas por tipo
"""

import os
os.chdir(r"C:\Z_Proyectos\control_GPS")

import pandas as pd
import numpy as np
import config
import sqldf

import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
from docx import Document
from docx.shared import Inches
from haversine import haversine, haversine_vector, Unit

date = datetime.now() - relativedelta(days=1)
date_str = date.strftime('%Y.%m.%d')

def read_data(report_path: str = config.report_path):
    df = pd.read_excel(report_path, header=3)
    return df
    
def read_param(param_path: str = config.param_path, locations_path: str = config.locations_path):
    df_param = pd.read_excel(param_path)
    df_locations = pd.read_excel(locations_path)

    return df_param, df_locations

def clean_data(df):
    filter_1 = df['Vehicle plate number'].notna()
    filter_2 = df['Vehicle plate number'] != 'Vehicle plate number'
    df = df[filter_1 & filter_2]
    
    df['Start time'] = pd.to_datetime(df['Start time'])
    df['End time'] = pd.to_datetime(df['End time'])
    df['Duration_mins'] = (df['End time'] - df['Start time'])
    df['Duration_mins'] = df['Duration_mins'].apply(lambda x: x.total_seconds() / 60)
    df['Mileage (KM)'] = df['Mileage (KM)'].replace('-', 0).astype(float)
    df['Start location'] = df['Start location'].str.replace('N', '').str.replace('W', '')
    df['End location'] = df['End location'].str.replace('N', '').str.replace('W', '')
    df[['Latitud_Inicio', 'Longitud_Inicio']] = df['Start location'].str.split(',', expand=True)
    df[['Latitud_Fin', 'Longitud_Fin']] = df['End location'].str.split(',', expand=True)
    location_cols = ['Latitud_Inicio', 'Longitud_Inicio', 'Latitud_Fin', 'Longitud_Fin']
    df[location_cols] = df[location_cols].fillna(0.0).replace('-', 0.0).astype(float)
    df[['Longitud_Inicio', 'Longitud_Fin']] = df[['Longitud_Inicio', 'Longitud_Fin']].mul(-1)
    df = df.reset_index(drop=True)
    df.drop(['#', 'Duration', 'Start location', 'End location'], axis=1, inplace=True)
    
    return df

def aggregate_metrics():
    global df_drive_agg, df_park_agg
    
    df_drive_agg = sqldf.run(config.driving_agg)
    df_park_agg = sqldf.run(config.parking_agg)
    df_agg = sqldf.run(config.join_agg)
    df_agg.drop(['index'], axis=1, inplace=True)
    df_agg.to_excel(rf".\trip_metrics\{date_str}_trip_metrics.xlsx")

def common_places(df, df_locations):
    df['Ubicacion'] = list(zip(df['Latitud_Inicio'], df['Longitud_Inicio']))
    df_locations['Ubicacion'] = list(zip(df_locations['Latitud'], df_locations['Longitud']))
    array_1 = df_locations['Ubicacion'].tolist()
    array_2 = df['Ubicacion'].tolist()
    
    dists = haversine_vector(array_1, array_2, unit='km', comb=True)
    df_dists = pd.DataFrame(dists, columns=df_locations['Location'])
    
    df['Closest'] = df_dists.idxmin(axis=1)
    df['Dist'] = df_dists.min(axis=1)
    df = df.merge(df_locations[['Location', 'Perimetro KM']],
                  left_on=['Closest'], right_on=['Location'], how='left')
    df['Closest'] = df.apply(lambda x: x['Closest'] if x['Perimetro KM'] > x['Dist'] else '', axis=1)
    
    
    return df
    
def plot_heatmap_trips(df):
    fig = go.Figure(go.Densitymapbox(lat=df['Latitud_Inicio'], lon=df['Longitud_Inicio'], radius=5))
    
    lat_center = (df['Latitud_Inicio'].max() + df['Latitud_Inicio'].min())/2
    lon_center = (df['Longitud_Inicio'].max() + df['Longitud_Inicio'].min())/2
    fig.update_layout(margin = {'b': 0, 'l': 0, 'r': 0, 't':0},
                      mapbox = {'center': {'lat': lat_center, 'lon': lon_center},
                                'style': "open-street-map", 'zoom': 10})
    
    fig.write_html(r".\trip_metrics\trips_mapa_calor.html")

def plot_all_trips(df_plate):
    longs = df_plate['Longitud_Inicio'].tolist()
    longs.append(df_plate['Longitud_Fin'].tolist()[-1])
    lats = df_plate['Latitud_Inicio'].tolist()
    lats.append(df_plate['Latitud_Fin'].tolist()[-1])
    fig = go.Figure(go.Scattermapbox(mode = "markers+lines", marker = {'size': 9},
                                    lon = longs, lat = lats))
    row = {'Latitud_Inicio': df_plate['Latitud_Inicio'].max(),
           'Latitud_Fin': df_plate['Latitud_Inicio'].min(),
           'Longitud_Inicio': df_plate['Longitud_Inicio'].max(),
           'Longitud_Fin': df_plate['Longitud_Inicio'].min()}
    zoom = set_plot_zoom(row)
    
    lat_center = (df_plate['Latitud_Inicio'].max() + df_plate['Latitud_Inicio'].min())/2
    lon_center = (df_plate['Longitud_Inicio'].max() + df_plate['Longitud_Inicio'].min())/2
    fig.update_layout(margin = {'b': 0, 'l': 0, 'r': 0, 't':0},
                      mapbox = {'center': {'lat': lat_center, 'lon': lon_center},
                                'style': "open-street-map", 'zoom': zoom})
    fig_png = BytesIO(fig.to_image(format="png"))
    
    document.add_picture(fig_png, width=Inches(6.0))

def plot_single_trips(df_plate):
    trip_num = 0
    for index, row in df_plate.iterrows():
        trip_num += 1
        document.add_page_break()
        p = document.add_paragraph()
        p.add_run(f'Viaje {trip_num}').bold = True
        document.add_paragraph(f'Desde {row["Start time"]} hasta {row["End time"]}')
        document.add_paragraph('Duración del viaje: %.1f minutos.' %row["Duration_mins"])
        document.add_paragraph('Total KM: %.1f' %row["Mileage (KM)"])
        fig = go.Figure(go.Scattermapbox(mode = "markers+lines",
                                         marker = {'size': [12,12], 'opacity': 1,
                                                   'color': ['blue', 'red']},
                                         line = {'color': 'black'},
                                         lon = [row['Longitud_Inicio'], row['Longitud_Fin']],
                                         lat = [row['Latitud_Inicio'], row['Latitud_Fin']]))
        lat_center = (row['Latitud_Inicio'] + row['Latitud_Fin'])/2
        lon_center = (row['Longitud_Inicio'] + row['Longitud_Fin'])/2
        zoom = set_plot_zoom(row)
        fig.update_layout(margin = {'b': 0, 'l': 0, 'r': 0, 't':0},
                          mapbox = {'center': {'lat': lat_center,'lon': lon_center},
                                    'style': "open-street-map", 'zoom': zoom})
        fig_png = BytesIO(fig.to_image(format="png"))
        
        document.add_picture(fig_png, width=Inches(6.0))

def set_plot_zoom(row):
    cat_1 = np.square(row['Latitud_Inicio'] - row['Latitud_Fin'])
    cat_2 = np.square(row['Longitud_Inicio'] - row['Longitud_Fin'])
    hipotenusa = np.sqrt(cat_1 + cat_2)
    
    zoom = 10
    for i in config.zoom_list:
        if hipotenusa < i[0]:
            zoom = i[1]
            break
    
    return zoom

def create_trips_docx(df):
    global document
    
    for plate in df['Vehicle plate number'].unique():
        document = Document()
        p = document.add_paragraph()
        p.add_run(f'GPS {plate} del {date_str}').bold = True
        
        plate_path = os.path.join(config.control_path, f'{plate}')
        if not os.path.isdir(plate_path):
            os.mkdir(plate_path)
        
        day_path = os.path.join(plate_path, f'{date_str}')
        if not os.path.isdir(day_path):
            os.mkdir(day_path)
        
        df_plate = df[(df['Vehicle plate number']==plate) & (df['Trip State']=='Driving')]
        
        if df_plate.shape[0] > 0:
            plot_all_trips(df_plate)
            plot_single_trips(df_plate)    
            document.save(os.path.join(day_path, f'{date_str}_{plate}.docx'))
        
        print('Procesada: ', plate)

def main_gps():
    df = read_data()
    df_param, df_locations = read_param()
    
    aggregate_metrics()
    plot_heatmap_trips(df)
    create_trips_docx(df)
    
if __name__ == '__main__':
    #main_gps()
    df = read_data()
    df_param, df_locations = read_param()
    df = clean_data(df)
    aggregate_metrics()
    plot_heatmap_trips(df)
    df = df[df['Vehicle plate number']=='WMQ691'] ### BORRAR
    create_trips_docx(df)
