# -*- coding: utf-8 -*-
import re
import pandas as pd
from datetime import datetime

today = datetime.now().strftime('%Y.%m.%d')

param_path = r".\parametros_control\Parametros.xlsx"

df_params = pd.read_excel(param_path, sheet_name='PARAMETROS', index_col=0)
report_path = df_params.loc['Ruta reporte','Valor']
control_path = df_params.loc['Ruta resultados','Valor']
report_dates = re.findall(r'[0-9]{8}', report_path)
start_date = report_dates[0][:4] + '.' + report_dates[0][4:6] + '.' + report_dates[0][6:]
end_date = start_date
if len(report_dates) > 1:
    end_date = report_dates[1][:4] + '.' + report_dates[1][4:6] + '.' + report_dates[1][6:]

df_locations = pd.read_excel(param_path, sheet_name='UBICACIONES')
df_vehicles = pd.read_excel(param_path, sheet_name='VEHICULOS')
df_schedules = pd.read_excel(param_path, sheet_name='CRONOGRAMA')

vehicle_types = list(df_vehicles['Tipo'].dropna().unique())

zoom_list = [(2.2, 14), (4.5, 13), (8, 12), (20, 11), (50, 10), (150, 9), (500, 8)]

driving_agg = """SELECT "Vehicle plate number" AS Placa, COUNT("Vehicle plate number") AS Total_Viajes,
                SUM("Mileage (KM)") AS Total_KM, SUM("Duration_mins")/60 AS Total_Horas_Manejo,
                AVG("Duration_mins") AS Prom_Mins_Manejo
                FROM df
                WHERE "Trip State" = "Driving"
                GROUP BY "Vehicle plate number"
                """

parking_agg = """SELECT "Vehicle plate number" AS Placa,
                SUM("Duration_mins")/60 AS Total_Horas_Parqueo, AVG("Duration_mins") AS Prom_Mins_Parqueo
                FROM df
                WHERE "Trip State" = "Parking"
                GROUP BY "Vehicle plate number"
                """

join_agg = """SELECT D.*, P.Total_Horas_Parqueo, P.Prom_Mins_Parqueo
            FROM df_drive_agg AS D LEFT JOIN df_park_agg AS P
            ON D.Placa = P.Placa
            ORDER BY Total_Viajes DESC
            """

query_places = """SELECT "Vehicle plate number" Placa, GROUP_CONCAT(Closest, ", ") AS Locations
                FROM df_unique
                GROUP BY Placa
                """

spa_eng_cols = {'Número de placa del vehículo': 'Vehicle plate number',
                'Estado de viaje': 'Trip State', 'Tiempo de Inicio': 'Start time',
                'Tiempo Final': 'End time', 'Kilometraje (KM)': 'Mileage (KM)',
                'Duración': 'Duration', 'Lugar de inicio': 'Start location',
                'Fin Localización': 'End location'}
