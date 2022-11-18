# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

date = datetime.now() - relativedelta(days=1)
date_str = date.strftime('%Y.%m.%d')

param_path = r".\parametros_control\Parametros.xlsx"

df_params = pd.read_excel(param_path, sheet_name='PARAMETROS', index_col=0)
report_path = df_params.loc['Ruta reporte','Valor']
control_path = df_params.loc['Ruta resultados','Valor']

df_locations = pd.read_excel(param_path, sheet_name='UBICACIONES')
df_vehicles = pd.read_excel(param_path, sheet_name='VEHICULOS')
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
