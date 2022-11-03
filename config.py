# -*- coding: utf-8 -*-

report_path = r"C:\Z_Proyectos\control_GPS\reportes\Trip report(20221102-20221102).xlsx"
param_path = r"C:\Z_Proyectos\control_GPS\parametros_control\Parametros.xlsx"
control_path = r"C:\Z_Proyectos\control_GPS\control"

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