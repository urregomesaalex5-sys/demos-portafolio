"""
Automatizador de Reportes de Ventas
====================================
Demo de portafolio para Workana.
Lee datos de ventas con errores reales, los limpia, calcula métricas y
exporta un CSV limpio junto con un reporte en PDF con tablas y gráficas.

Uso:
    python automatizador.py
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Modo no interactivo para generar imágenes sin GUI
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)


# ---------------------------------------------------------------------------
# Configuración de codificación para evitar errores con emojis en Windows
# ---------------------------------------------------------------------------
sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# Configuración de rutas relativas al script
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_ENTRADA = BASE_DIR / "datos_ventas.csv"
ARCHIVO_SALIDA_CSV = BASE_DIR / "datos_limpios.csv"
ARCHIVO_SALIDA_PDF = BASE_DIR / "reporte.pdf"
GRAFICA_VENTAS_MES = BASE_DIR / "ventas_por_mes.png"
GRAFICA_TOP_PRODUCTOS = BASE_DIR / "top_productos.png"


# ---------------------------------------------------------------------------
# Funciones de limpieza
# ---------------------------------------------------------------------------
def normalizar_fecha(valor):
    """
    Intenta convertir múltiples formatos de fecha a datetime.
    Retorna NaT si no es posible.
    """
    if pd.isna(valor):
        return pd.NaT

    valor_limpio = str(valor).strip()
    formatos = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ]

    for fmt in formatos:
        try:
            return pd.to_datetime(valor_limpio, format=fmt)
        except ValueError:
            continue

    return pd.NaT


def limpiar_monto(valor):
    """
    Convierte montos con símbolo $, puntos de miles y comas decimales
    a un número flotante. Retorna NaN si el valor no es convertible.
    """
    if pd.isna(valor):
        return float("nan")

    texto = str(valor).strip()
    # Elimina el símbolo $ y los espacios
    texto = texto.replace("$", "").replace(" ", "")

    if not texto:
        return float("nan")

    # Detecta si usa punto como separador de miles y coma decimal
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            # Formato europeo/colombiano: 1.200.000,00
            texto = texto.replace(".", "").replace(",", ".")
        else:
            # Formato inglés: 1,200,000.00
            texto = texto.replace(",", "")
    elif "," in texto:
        # Puede ser separador de miles o decimal
        # Si hay más de una coma, es separador de miles
        if texto.count(",") > 1:
            texto = texto.replace(",", "")
        else:
            # Si la parte después de la coma tiene 1 o 2 dígitos, es decimal
            parte_decimal = texto.split(",")[-1]
            if len(parte_decimal) <= 2:
                texto = texto.replace(",", ".")
            else:
                texto = texto.replace(",", "")

    try:
        return float(texto)
    except ValueError:
        return float("nan")


def limpiar_texto(valor):
    """Elimina espacios al inicio y final y normaliza múltiples espacios."""
    if pd.isna(valor):
        return valor
    return re.sub(r"\s+", " ", str(valor).strip())


def cargar_y_limpiar_datos(ruta_csv):
    """
    Carga el CSV, limpia columnas y devuelve un DataFrame listo para análisis.
    """
    # Leer CSV con codificación UTF-8 (con BOM opcional) o fallback a cp1252
    try:
        df = pd.read_csv(ruta_csv, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(ruta_csv, encoding="cp1252")

    # Normalizar nombres de columnas
    df.columns = [col.strip().lower() for col in df.columns]

    # Limpiar texto en columnas categóricas
    for col in ["cliente", "producto", "ciudad"]:
        if col in df.columns:
            df[col] = df[col].apply(limpiar_texto)

    # Normalizar ciudad a formato de título (Bogotá, Medellín, Cali)
    if "ciudad" in df.columns:
        df["ciudad"] = df["ciudad"].str.title()

    # Normalizar fechas
    df["fecha"] = df["fecha"].apply(normalizar_fecha)

    # Convertir montos a numérico
    df["precio_unitario"] = df["precio_unitario"].apply(limpiar_monto)

    # Convertir cantidad a numérico
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")

    # Eliminar filas duplicadas exactas
    df = df.drop_duplicates()

    # Eliminar filas con fecha nula (dato crítico)
    df = df.dropna(subset=["fecha"])

    # Rellenar o descartar nulos en columnas importantes
    df = df.dropna(subset=["producto", "cantidad", "precio_unitario"])

    # Rellenar ciudad vacía con "No especificada"
    df["ciudad"] = df["ciudad"].fillna("No especificada")

    # Calcular total de venta por fila
    df["total_venta"] = df["cantidad"] * df["precio_unitario"]

    # Ordenar por fecha
    df = df.sort_values("fecha").reset_index(drop=True)

    return df


# ---------------------------------------------------------------------------
# Funciones de análisis
# ---------------------------------------------------------------------------
def calcular_metricas(df):
    """Calcula las métricas principales del reporte."""
    metricas = {}

    # Ventas totales
    metricas["ventas_totales"] = df["total_venta"].sum()

    # Ventas por mes
    df["mes"] = df["fecha"].dt.to_period("M")
    ventas_por_mes = df.groupby("mes")["total_venta"].sum().reset_index()
    ventas_por_mes["mes_str"] = ventas_por_mes["mes"].astype(str)
    metricas["ventas_por_mes"] = ventas_por_mes

    # Top 5 productos
    top_productos = (
        df.groupby("producto")["total_venta"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    metricas["top_productos"] = top_productos

    # Top 5 ciudades
    top_ciudades = (
        df.groupby("ciudad")["total_venta"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .reset_index()
    )
    metricas["top_ciudades"] = top_ciudades

    # Ticket promedio (promedio por transacción)
    metricas["ticket_promedio"] = df["total_venta"].mean()

    # Total de transacciones
    metricas["total_transacciones"] = len(df)

    return metricas


# ---------------------------------------------------------------------------
# Funciones de visualización
# ---------------------------------------------------------------------------
def formatear_pesos(valor):
    """Formatea un número como pesos colombianos."""
    return f"${valor:,.0f}"


def generar_graficas(metricas):
    """Genera y guarda las gráficas del reporte."""
    # Gráfica de ventas por mes
    plt.figure(figsize=(8, 4.5))
    ventas_mes = metricas["ventas_por_mes"]
    plt.bar(ventas_mes["mes_str"], ventas_mes["total_venta"], color="#2E86AB")
    plt.title("Ventas por Mes", fontsize=14, weight="bold")
    plt.xlabel("Mes")
    plt.ylabel("Total Ventas ($)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(GRAFICA_VENTAS_MES, dpi=150)
    plt.close()

    # Gráfica de top 5 productos
    plt.figure(figsize=(8, 4.5))
    top_prod = metricas["top_productos"]
    plt.barh(top_prod["producto"][::-1], top_prod["total_venta"][::-1], color="#A23B72")
    plt.title("Top 5 Productos por Ventas", fontsize=14, weight="bold")
    plt.xlabel("Total Ventas ($)")
    plt.tight_layout()
    plt.savefig(GRAFICA_TOP_PRODUCTOS, dpi=150)
    plt.close()


# ---------------------------------------------------------------------------
# Funciones de generación de PDF
# ---------------------------------------------------------------------------
def crear_pdf(metricas, df):
    """Crea el reporte en PDF con tablas y gráficas."""
    doc = SimpleDocTemplate(
        str(ARCHIVO_SALIDA_PDF),
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )

    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=estilos["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#1B4965"),
        spaceAfter=14,
    )
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2E86AB"),
        spaceAfter=10,
    )

    elementos = []

    # Título y fecha
    elementos.append(Paragraph("Reporte de Ventas", estilo_titulo))
    elementos.append(
        Paragraph(
            f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            estilos["Normal"],
        )
    )
    elementos.append(Spacer(1, 0.2 * inch))

    # Resumen de métricas
    elementos.append(Paragraph("Resumen General", estilo_subtitulo))
    datos_resumen = [
        ["Métrica", "Valor"],
        ["Ventas totales", formatear_pesos(metricas["ventas_totales"])],
        ["Total de transacciones", f"{metricas['total_transacciones']}"],
        ["Ticket promedio", formatear_pesos(metricas["ticket_promedio"])],
    ]
    tabla_resumen = Table(datos_resumen, colWidths=[3 * inch, 3 * inch])
    tabla_resumen.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B4965")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F4F4")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elementos.append(tabla_resumen)
    elementos.append(Spacer(1, 0.3 * inch))

    # Ventas por mes
    elementos.append(Paragraph("Ventas por Mes", estilo_subtitulo))
    datos_mes = [["Mes", "Total Ventas"]]
    for _, fila in metricas["ventas_por_mes"].iterrows():
        datos_mes.append([fila["mes_str"], formatear_pesos(fila["total_venta"])])

    tabla_mes = Table(datos_mes, colWidths=[3 * inch, 3 * inch])
    tabla_mes.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86AB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F4F4")),
            ]
        )
    )
    elementos.append(tabla_mes)
    elementos.append(Spacer(1, 0.2 * inch))
    elementos.append(Image(str(GRAFICA_VENTAS_MES), width=5.5 * inch, height=3.1 * inch))
    elementos.append(Spacer(1, 0.3 * inch))

    # Top 5 productos
    elementos.append(Paragraph("Top 5 Productos", estilo_subtitulo))
    datos_prod = [["Producto", "Total Ventas"]]
    for _, fila in metricas["top_productos"].iterrows():
        datos_prod.append([fila["producto"], formatear_pesos(fila["total_venta"])])

    tabla_prod = Table(datos_prod, colWidths=[3.5 * inch, 2.5 * inch])
    tabla_prod.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#A23B72")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F4F4")),
            ]
        )
    )
    elementos.append(tabla_prod)
    elementos.append(Spacer(1, 0.2 * inch))
    elementos.append(
        Image(str(GRAFICA_TOP_PRODUCTOS), width=5.5 * inch, height=3.1 * inch)
    )
    elementos.append(Spacer(1, 0.3 * inch))

    # Top 5 ciudades
    elementos.append(Paragraph("Top 5 Ciudades", estilo_subtitulo))
    datos_ciudad = [["Ciudad", "Total Ventas"]]
    for _, fila in metricas["top_ciudades"].iterrows():
        datos_ciudad.append([fila["ciudad"], formatear_pesos(fila["total_venta"])])

    tabla_ciudad = Table(datos_ciudad, colWidths=[3.5 * inch, 2.5 * inch])
    tabla_ciudad.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F18F01")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F4F4")),
            ]
        )
    )
    elementos.append(tabla_ciudad)

    # Construir PDF
    doc.build(elementos)


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------
def main():
    print("=" * 50)
    print("Automatizador de Reportes de Ventas")
    print("=" * 50)

    if not ARCHIVO_ENTRADA.exists():
        print(f"ERROR: No se encontró el archivo {ARCHIVO_ENTRADA}")
        return

    print("\n[1/4] Cargando y limpiando datos...")
    df_limpio = cargar_y_limpiar_datos(ARCHIVO_ENTRADA)
    print(f"       Filas limpias: {len(df_limpio)}")

    print("\n[2/4] Calculando metricas...")
    metricas = calcular_metricas(df_limpio)
    print(f"       Ventas totales: {formatear_pesos(metricas['ventas_totales'])}")
    print(f"       Ticket promedio: {formatear_pesos(metricas['ticket_promedio'])}")

    print("\n[3/4] Generando graficas...")
    generar_graficas(metricas)

    print("\n[4/4] Exportando resultados...")
    df_limpio.to_csv(ARCHIVO_SALIDA_CSV, index=False, encoding="utf-8-sig")
    crear_pdf(metricas, df_limpio)

    print(f"\n[OK] CSV limpio guardado en: {ARCHIVO_SALIDA_CSV}")
    print(f"[OK] Reporte PDF guardado en: {ARCHIVO_SALIDA_PDF}")
    print("\nProceso completado exitosamente.")


if __name__ == "__main__":
    main()
