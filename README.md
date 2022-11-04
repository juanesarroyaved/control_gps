# Control de vehículos por GPS

Este repositorio contiene el código en Python de un control periódico de viajes, ubicaciones, tiempos y kilómetros recorridos, de cierta cantidad de vehículos.

## Datos de entrada:

Los datos de entrada es un reporte de viajes de una plataforma de monitoreo satelital que arroja para cada vehículo el detalle de los viajes realizados:
- Estado del viaje: Conducción o Parqueo
- Hora de inicio
- Hora de finalización
- Cantidad de Kilómetros
- Latitud y Longitud de inicio
- Latitud y Longitud de finalización

## Resultados:
El código genera, para cada vehículo:
- Archivo con métricas de Total de viajes, total de horas de manejo, Promedio de minutos de manejo, Total de horas de parqueo, Promedio minutos de parqueo
- Documento de word con un gráfico de todos los viajes y un gráfico para cada viaje realizado.
