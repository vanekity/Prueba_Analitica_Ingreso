# ==========================================================
# TABLERO EJECUTIVO
# PARTE C - VOLUMEN, COSTO, CALIDAD,
# OPORTUNIDAD Y PRIORIZACION
# ==========================================================

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ==========================================================
# CONFIGURACION GENERAL
# ==========================================================

st.set_page_config(
    page_title="Tablero ejecutivo de atención",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# ESTILO VISUAL
# ==========================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #F7F7FA;
    }

    .titulo-principal {
        color: #5D1854;
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitulo {
        color: #666666;
        font-size: 15px;
        margin-bottom: 20px;
    }

    .hallazgo {
        background-color: #F3E8F2;
        border-left: 5px solid #7A1F78;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    .recomendacion {
        background-color: #EEF5F2;
        border-left: 5px solid #31856B;
        padding: 12px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# ARCHIVOS
# ==========================================================

ARCHIVO_BASE = (
    "Base_ficticia_Prueba_Analista_Datos_Analitica.xlsx"
)

ARCHIVO_PRIORIZACION = (
    "priorizacion_reingreso_30d.xlsx"
)


# ==========================================================
# CARGA DE INFORMACION
# ==========================================================

@st.cache_data
def cargar_datos():

    pacientes = pd.read_excel(
        ARCHIVO_BASE,
        sheet_name="Pacientes",
        engine="openpyxl"
    )

    prestadores = pd.read_excel(
        ARCHIVO_BASE,
        sheet_name="Prestadores",
        engine="openpyxl"
    )

    atenciones = pd.read_excel(
        ARCHIVO_BASE,
        sheet_name="Atenciones",
        engine="openpyxl"
    )

    casos = pd.read_excel(
        ARCHIVO_BASE,
        sheet_name="Casos_Analiticos",
        engine="openpyxl"
    )

    priorizacion = pd.read_excel(
        ARCHIVO_PRIORIZACION,
        engine="openpyxl"
    )

    return (
        pacientes,
        prestadores,
        atenciones,
        casos,
        priorizacion
    )


try:

    (
        pacientes,
        prestadores,
        atenciones,
        casos,
        priorizacion
    ) = cargar_datos()

except FileNotFoundError as error:

    st.error(
        "No se encontró uno de los archivos requeridos. "
        "Verifica que el Excel original y el archivo de "
        "priorización estén en la misma carpeta que tablero.py."
    )

    st.code(str(error))

    st.stop()


# ==========================================================
# PREPARACION DE DATOS
# ==========================================================

atenciones["fecha_atencion"] = pd.to_datetime(
    atenciones["fecha_atencion"],
    errors="coerce"
)

atenciones["periodo"] = (
    atenciones["fecha_atencion"]
    .dt.to_period("M")
    .astype(str)
)

atenciones["costo"] = pd.to_numeric(
    atenciones["costo"],
    errors="coerce"
)

atenciones["dias_espera"] = pd.to_numeric(
    atenciones["dias_espera"],
    errors="coerce"
)

casos["reingreso_30d"] = pd.to_numeric(
    casos["reingreso_30d"],
    errors="coerce"
)

priorizacion["probabilidad_reingreso"] = pd.to_numeric(
    priorizacion["probabilidad_reingreso"],
    errors="coerce"
)


# ==========================================================
# INTEGRAR PRESTADORES
# ==========================================================

atenciones = atenciones.merge(
    prestadores[
        [
            "id_prestador",
            "nombre_prestador",
            "municipio"
        ]
    ],
    on="id_prestador",
    how="left",
    suffixes=(
        "",
        "_prestador"
    )
)


# ==========================================================
# FILTROS
# ==========================================================

st.markdown(
    '<div class="titulo-principal">'
    'Tablero ejecutivo de atención y riesgo de reingreso'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Volumen, costo, calidad, oportunidad y priorización'
    '</div>',
    unsafe_allow_html=True
)


filtro_1, filtro_2, filtro_3 = st.columns(3)


periodos_disponibles = sorted(
    atenciones["periodo"]
    .dropna()
    .unique()
    .tolist()
)

with filtro_1:

    periodos_seleccionados = st.multiselect(
        "Periodo",
        options=periodos_disponibles,
        default=periodos_disponibles
    )


canales_disponibles = sorted(
    atenciones["canal"]
    .dropna()
    .unique()
    .tolist()
)

with filtro_2:

    canales_seleccionados = st.multiselect(
        "Canal",
        options=canales_disponibles,
        default=canales_disponibles
    )


prestadores_disponibles = sorted(
    atenciones["nombre_prestador"]
    .dropna()
    .unique()
    .tolist()
)

with filtro_3:

    prestadores_seleccionados = st.multiselect(
        "Prestador",
        options=prestadores_disponibles,
        default=prestadores_disponibles
    )


# Aplicar filtros

atenciones_filtradas = atenciones[
    atenciones["periodo"].isin(
        periodos_seleccionados
    )
    &
    atenciones["canal"].isin(
        canales_seleccionados
    )
    &
    (
        atenciones["nombre_prestador"].isin(
            prestadores_seleccionados
        )
        |
        atenciones["nombre_prestador"].isna()
    )
].copy()


# ==========================================================
# CALCULO DE INDICADORES
# VISUAL 1 - TARJETAS EJECUTIVAS
# ==========================================================

total_atenciones = len(
    atenciones_filtradas
)

costo_total = (
    atenciones_filtradas["costo"]
    .sum()
)

atenciones_validas_espera = atenciones_filtradas[
    (
        atenciones_filtradas["dias_espera"] >= 0
    )
    &
    (
        atenciones_filtradas["estado_atencion"]
        == "Atendida"
    )
]

espera_promedio = (
    atenciones_validas_espera[
        "dias_espera"
    ]
    .mean()
)

tasa_reingreso = (
    casos["reingreso_30d"]
    .mean()
    * 100
)

total_priorizados = (
    priorizacion["priorizar"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("si")
    .sum()
)

porcentaje_priorizado = (
    total_priorizados
    /
    len(priorizacion)
    *
    100
)


st.subheader(
    "Indicadores esenciales"
)

kpi_1, kpi_2, kpi_3, kpi_4, kpi_5 = (
    st.columns(5)
)

with kpi_1:

    st.metric(
        label="Atenciones",
        value=f"{total_atenciones:,.0f}"
    )

with kpi_2:

    st.metric(
        label="Costo total",
        value=f"${costo_total:,.0f}"
    )

with kpi_3:

    st.metric(
        label="Espera promedio válida",
        value=(
            f"{espera_promedio:.1f} días"
            if pd.notna(espera_promedio)
            else "Sin datos"
        )
    )

with kpi_4:

    st.metric(
        label="Reingreso observado",
        value=f"{tasa_reingreso:.1f}%"
    )

with kpi_5:

    st.metric(
        label="Casos priorizados",
        value=f"{total_priorizados:,.0f}",
        delta=(
            f"{porcentaje_priorizado:.1f}% "
            "de evaluados"
        )
    )


st.divider()


# ==========================================================
# VISUAL 2
# TENDENCIA MENSUAL DE ATENCIONES Y COSTO
# ==========================================================

tendencia = (
    atenciones_filtradas
    .groupby(
        "periodo",
        as_index=False
    )
    .agg(
        total_atenciones=(
            "id_atencion",
            "count"
        ),
        costo_total=(
            "costo",
            "sum"
        )
    )
    .sort_values("periodo")
)


fig_tendencia = make_subplots(
    specs=[
        [
            {
                "secondary_y": True
            }
        ]
    ]
)


fig_tendencia.add_trace(
    go.Bar(
        x=tendencia["periodo"],
        y=tendencia["total_atenciones"],
        name="Atenciones",
        marker_color="#7A1F78"
    ),
    secondary_y=False
)


fig_tendencia.add_trace(
    go.Scatter(
        x=tendencia["periodo"],
        y=tendencia["costo_total"],
        name="Costo total",
        mode="lines+markers",
        line=dict(
            color="#E28A36",
            width=3
        )
    ),
    secondary_y=True
)


fig_tendencia.update_layout(
    title="Evolución mensual de atenciones y costo",
    height=380,
    margin=dict(
        l=20,
        r=20,
        t=60,
        b=20
    ),
    legend=dict(
        orientation="h",
        y=1.12
    ),
    plot_bgcolor="white"
)


fig_tendencia.update_yaxes(
    title_text="Número de atenciones",
    secondary_y=False
)

fig_tendencia.update_yaxes(
    title_text="Costo total",
    tickprefix="$",
    separatethousands=True,
    secondary_y=True
)


# ==========================================================
# VISUAL 3
# ESTADO DE LAS ATENCIONES
# ==========================================================

estado_atenciones = (
    atenciones_filtradas[
        "estado_atencion"
    ]
    .value_counts()
    .rename_axis(
        "estado_atencion"
    )
    .reset_index(
        name="cantidad"
    )
)


columna_izquierda, columna_derecha = (
    st.columns(2)
)


with columna_izquierda:

    st.plotly_chart(
        fig_tendencia,
        width="stretch"
    )


with columna_derecha:

    fig_estado = px.bar(
        estado_atenciones,
        x="cantidad",
        y="estado_atencion",
        orientation="h",
        text="cantidad",
        title="Distribución de atenciones por estado",
        color="estado_atencion",
        color_discrete_map={
            "Atendida": "#31856B",
            "Cancelada": "#D97835",
            "No asistió": "#B33A3A"
        }
    )

    fig_estado.update_layout(
        height=380,
        showlegend=False,
        xaxis_title="Número de atenciones",
        yaxis_title="",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        plot_bgcolor="white"
    )

    fig_estado.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_estado,
        width="stretch"
    )


# ==========================================================
# VISUAL 4
# CALIDAD Y OPORTUNIDAD
# ==========================================================

diagnosticos_faltantes = (
    atenciones_filtradas[
        "diagnostico_cie10"
    ]
    .isna()
    .sum()
)

esperas_negativas = (
    atenciones_filtradas[
        "dias_espera"
    ]
    .lt(0)
    .sum()
)

prestadores_huerfanos = (
    atenciones_filtradas[
        "nombre_prestador"
    ]
    .isna()
    .sum()
)

motivos_cierre_faltantes = (
    casos[
        "motivo_cierre_caso"
    ]
    .isna()
    .sum()
)


calidad = pd.DataFrame(
    {
        "hallazgo": [
            "Diagnóstico faltante",
            "Espera negativa",
            "Motivo cierre faltante",
            "Prestador inexistente"
        ],
        "registros": [
            diagnosticos_faltantes,
            esperas_negativas,
            motivos_cierre_faltantes,
            prestadores_huerfanos
        ],
        "tipo": [
            "Completitud",
            "Validez",
            "Completitud",
            "Integridad"
        ]
    }
)


# ==========================================================
# VISUAL 5
# PRIORIZACION DE RIESGO
# ==========================================================

orden_riesgo = [
    "Bajo",
    "Medio",
    "Alto",
    "Muy alto"
]

priorizacion["nivel_riesgo"] = pd.Categorical(
    priorizacion["nivel_riesgo"],
    categories=orden_riesgo,
    ordered=True
)

riesgo = (
    priorizacion[
        "nivel_riesgo"
    ]
    .value_counts()
    .reindex(
        orden_riesgo,
        fill_value=0
    )
    .rename_axis(
        "nivel_riesgo"
    )
    .reset_index(
        name="casos"
    )
)


columna_izquierda_2, columna_derecha_2 = (
    st.columns(2)
)


with columna_izquierda_2:

    fig_calidad = px.bar(
        calidad.sort_values(
            "registros"
        ),
        x="registros",
        y="hallazgo",
        orientation="h",
        text="registros",
        color="tipo",
        title=(
            "Registros afectados por problemas "
            "de calidad"
        ),
        color_discrete_map={
            "Completitud": "#E28A36",
            "Validez": "#B33A3A",
            "Integridad": "#7256A5"
        }
    )

    fig_calidad.update_layout(
        height=380,
        xaxis_title="Registros afectados",
        yaxis_title="",
        legend_title="Dimensión",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        plot_bgcolor="white"
    )

    fig_calidad.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_calidad,
        width="stretch"
    )


with columna_derecha_2:

    fig_riesgo = px.bar(
        riesgo,
        x="nivel_riesgo",
        y="casos",
        text="casos",
        title="Casos por nivel de riesgo de reingreso",
        color="nivel_riesgo",
        category_orders={
            "nivel_riesgo": orden_riesgo
        },
        color_discrete_map={
            "Bajo": "#5CA98C",
            "Medio": "#E9C46A",
            "Alto": "#E28A36",
            "Muy alto": "#B33A3A"
        }
    )

    fig_riesgo.update_layout(
        height=380,
        showlegend=False,
        xaxis_title="Nivel de riesgo",
        yaxis_title="Número de casos",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        plot_bgcolor="white"
    )

    fig_riesgo.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_riesgo,
        width="stretch"
    )


# ==========================================================
# HALLAZGOS Y RECOMENDACIONES
# ==========================================================

st.divider()

st.subheader(
    "Hallazgos y recomendaciones de negocio"
)


canceladas = (
    atenciones_filtradas[
        "estado_atencion"
    ]
    .eq("Cancelada")
    .sum()
)

inasistencias = (
    atenciones_filtradas[
        "estado_atencion"
    ]
    .eq("No asistió")
    .sum()
)

tasa_no_efectiva = (
    (
        canceladas
        +
        inasistencias
    )
    /
    total_atenciones
    *
    100
    if total_atenciones > 0
    else 0
)


hallazgos, recomendaciones = st.columns(2)


with hallazgos:

    st.markdown(
        "#### Evidencia e interpretación"
    )

    st.markdown(
        f"""
        <div class="hallazgo">
        <strong>1. Atención no efectiva</strong><br>
        Las cancelaciones y las inasistencias representan
        <strong>{tasa_no_efectiva:.2f}%</strong> de los
        registros filtrados. El resultado evidencia una
        proporción relevante de registros que no termina
        en atención efectiva.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="hallazgo">
        <strong>2. Calidad y oportunidad</strong><br>
        Se identifican
        <strong>{esperas_negativas}</strong> registros con
        días de espera negativos. Su inclusión reduciría
        artificialmente el indicador promedio de oportunidad.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="hallazgo">
        <strong>3. Priorización preventiva</strong><br>
        El modelo prioriza
        <strong>{total_priorizados}</strong> de
        <strong>{len(priorizacion)}</strong> casos evaluados
        con el umbral inicial de 0,50.
        </div>
        """,
        unsafe_allow_html=True
    )


with recomendaciones:

    st.markdown(
        "#### Decisión sugerida"
    )

    st.markdown(
        """
        <div class="recomendacion">
        <strong>1. Gestionar atención no efectiva</strong><br>
        Analizar cancelaciones e inasistencias por periodo,
        prestador y canal, y focalizar las acciones en los
        segmentos con mayor concentración.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="recomendacion">
        <strong>2. Implementar control de calidad</strong><br>
        Marcar automáticamente los tiempos negativos,
        excluirlos del KPI de oportunidad y conservarlos
        para validación y trazabilidad.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="recomendacion">
        <strong>3. Priorizar según capacidad</strong><br>
        Iniciar el seguimiento con los casos de riesgo muy
        alto y alto. Ajustar el umbral de 0,50 según la
        capacidad real del equipo y monitorizar falsos
        positivos y falsos negativos.
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# NOTA METODOLOGICA
# ==========================================================

st.caption(
    "Nota: el archivo de priorización corresponde al conjunto "
    "evaluado por el modelo. La probabilidad apoya la "
    "priorización y no constituye una decisión clínica "
    "automática."
)



