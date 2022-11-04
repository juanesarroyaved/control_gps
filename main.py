# -*- coding: utf-8 -*-
import os
os.chdir(r"C:\Z_Proyectos\control_GPS")

import pandas as pd
import config
import sqldf

import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
from docx import Document
from docx.shared import Inches

date = datetime.now() - relativedelta(days=1)
date_str = date.strftime('%Y.%m.%d')

df = pd.read_excel(config.report_path, header=3)
df_param = pd.read_excel(config.param_path)

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
df.drop(['#', 'Duration', 'Start location', 'End location'], axis=1, inplace=True)


df_drive_agg = sqldf.run(config.driving_agg)
df_park_agg = sqldf.run(config.parking_agg)
final_agg = sqldf.run(config.join_agg)
final_agg.drop(['index'], axis=1, inplace=True)


for plate in df['Vehicle plate number'].unique():
    
    document = Document()
    document.add_heading(f'GPS {plate} del {date_str}')
    
    plate_path = os.path.join(config.control_path, f'{plate}')
    if not os.path.isdir(plate_path):
        os.mkdir(plate_path)
    
    day_path = os.path.join(plate_path, f'{date_str}')
    if not os.path.isdir(day_path):
        os.mkdir(day_path)
    
    df_plate = df[(df['Vehicle plate number']==plate) & (df['Trip State']=='Driving')]
    
    if df_plate.shape[0] > 0:
        fig = go.Figure(go.Scattermapbox(mode = "markers+lines",
                                        lon = df_plate['Longitud_Inicio'],
                                        lat = df_plate['Latitud_Inicio'],
                                        marker = {'size': 7}))
        lat_center = (df_plate['Latitud_Inicio'].max() + df_plate['Latitud_Inicio'].min())/2
        lon_center = (df_plate['Longitud_Inicio'].max() + df_plate['Longitud_Inicio'].min())/2
        fig.update_layout(margin ={'l':0,'t':0,'b':0,'r':0},
                mapbox = {'center': {'lat': lat_center,
                                     'lon': lon_center},
                          'style': "open-street-map",
                          'zoom': 11})
        fig_png = BytesIO(fig.to_image(format="png"))
        
        document.add_picture(fig_png, width=Inches(6.0))
        
    trip_num = 0
    for index, row in df_plate.iterrows():
        trip_num += 1
        document.add_paragraph(f'Viaje {trip_num}: desde {row["Start time"]} hasta {row["End time"]}')
        document.add_paragraph(f'Duración del viaje: {row["Duration_mins"]} minutos.')
        
        fig = go.Figure(go.Scattermapbox(mode = "markers+lines",
                                        lon = [row['Longitud_Inicio'], row['Longitud_Fin']],
                                        lat = [row['Latitud_Inicio'], row['Latitud_Fin']],
                                        marker = {'size': 7}))
        lat_center = (row['Latitud_Inicio'] + row['Latitud_Fin'])/2
        lon_center = (row['Longitud_Inicio'] + row['Longitud_Fin'])/2
        fig.update_layout(margin ={'l':0,'t':0,'b':0,'r':0},
                mapbox = {'center': {'lat': lat_center,
                                     'lon': lon_center},
                          'style': "open-street-map",
                          'zoom': 11})
        fig_png = BytesIO(fig.to_image(format="png"))
        
        document.add_picture(fig_png, width=Inches(6.0))
        
    document.save(os.path.join(day_path, f'{date_str}_{plate}.docx'))
    
    print('Procesada: ', plate)


