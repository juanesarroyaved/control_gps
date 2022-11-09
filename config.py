# -*- coding: utf-8 -*-

report_path = r"C:\Z_Proyectos\control_GPS\reportes\Trip report(20221102-20221102).xlsx"
param_path = r"C:\Z_Proyectos\control_GPS\parametros_control\Parametros.xlsx"
control_path = r"C:\Z_Proyectos\control_GPS\control"
locations_path = r"C:\Z_Proyectos\control_GPS\parametros_control\Ubicaciones.xlsx"

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

zoom_list = [(0.013, 14), (0.03, 13), (0.08, 12), (0.1, 11), (0.18, 10)]

"""
Lugares a listar (priorizar por tours):
    - Marriott, York, Click-Clack, San Fernando, Hashtag, El Cielo, El Bin,
    Intercontinental
    - Pueblito Paisa, Plaza Botero, Comuna 13, Alpujarra, Pies descalzos,
    Pq. Poblado, Lleras, Provenza, Parques del río-edif inteligente,
    Jardín Botánico, Estadio, Museo de la memoria, Ciudad del Río, Parque Arví.
    - Tunel de oriente y occidente, EOH, JMC, Club Campestre-Rodeo-Country,
    Pq. Envigado-Sabaneta-La Estrella, Centros Comerciales, Hospitales.
    - Oficina, Guatapé
"""

"""
ZOOM:
    
Calcular hipotenusa (trayecto)

Hipot	Zoom
0.1100	10
0.1831	10
0.0832	11
0.1000	11
0.0442	12
0.0637	12
0.0750	12
0.0140	13
0.0188	13
0.0274	13
0.0300	13
0.0000	14
0.0129	14
0.0130	14

"""