# Automatizador de Reportes de Ventas

Demo de portafolio en Python que simula un flujo real de limpieza, análisis y reporte de datos de ventas.

## ¿Qué hace?

1. Lee un archivo `datos_ventas.csv` con datos reales y sucios: fechas en distintos formatos, montos con `$`, comas y puntos, espacios extra, filas duplicadas y valores vacíos.
2. Limpia los datos con `pandas`: normaliza fechas, convierte montos, elimina duplicados, trata nulos y estandariza texto.
3. Calcula métricas clave: ventas totales, ventas por mes, top 5 productos, top 5 ciudades y ticket promedio.
4. Genera un reporte profesional en PDF con `reportlab`, incluyendo tablas y dos gráficas generadas con `matplotlib`.
5. Exporta el dataset limpio a `datos_limpios.csv`.

## Estructura del proyecto

```
1_Automatizador_Reportes/
├── datos_ventas.csv      # Datos de ejemplo con errores reales
├── automatizador.py      # Script principal
├── requirements.txt      # Dependencias
├── README.md             # Este archivo
├── datos_limpios.csv     # Salida: datos limpios
├── reporte.pdf           # Salida: reporte en PDF
├── ventas_por_mes.png    # Gráfica temporal (se borra al regenerar)
└── top_productos.png     # Gráfica temporal (se borra al regenerar)
```

## Instalación

1. Clona o descarga esta carpeta.
2. Abre una terminal en la carpeta del proyecto.
3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python automatizador.py
```

El script usa rutas relativas, así que debe ejecutarse desde la carpeta donde se encuentra.

## Salidas generadas

- `datos_limpios.csv`: archivo CSV con los datos ya limpios y una columna adicional `total_venta`.
- `reporte.pdf`: reporte ejecutivo con:
  - Título y fecha de generación.
  - Resumen general (ventas totales, transacciones, ticket promedio).
  - Tabla y gráfica de ventas por mes.
  - Tabla y gráfica del top 5 de productos.
  - Tabla del top 5 de ciudades.

## Capturas esperadas

- **Terminal:** mensajes de progreso indicando carga, limpieza, cálculo de métricas y exportación exitosa.
- **PDF:** reporte con tablas formateadas y gráficas de barras.
- **CSV limpio:** datos estandarizados listos para análisis posterior.

## Tecnologías

- Python 3
- pandas
- matplotlib
- reportlab

## Autor

Edwin — Desarrollador Python.
