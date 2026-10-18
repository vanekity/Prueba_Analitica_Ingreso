import pandas as pd
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================================
#Parte A. Comprensión, integración y calidad de datos
# ==========================================================


# PUNTO 1 - MODELO DE DATOS Y VALIDACION DE LLAVES
# ==========================================================

archivo = "Base_ficticia_Prueba_Analista_Datos_Analitica.xlsx"

# Cargar tablas principales
pacientes = pd.read_excel(
    archivo,
    sheet_name="Pacientes",
    engine="openpyxl"
)

prestadores = pd.read_excel(
    archivo,
    sheet_name="Prestadores",
    engine="openpyxl"
)

atenciones = pd.read_excel(
    archivo,
    sheet_name="Atenciones",
    engine="openpyxl"
)

casos = pd.read_excel(
    archivo,
    sheet_name="Casos_Analiticos",
    engine="openpyxl"
)

print("=" * 60)
print("PUNTO 1 - MODELO DE DATOS Y VALIDACION DE LLAVES")
print("=" * 60)

# ==========================================================
# 1. DIMENSIONES
# ==========================================================

print("\n1. DIMENSIONES DE LAS TABLAS")

print("Pacientes:", pacientes.shape)
print("Prestadores:", prestadores.shape)
print("Atenciones:", atenciones.shape)
print("Casos Analiticos:", casos.shape)


# ==========================================================
# 2. VALIDACION DE LLAVES PRIMARIAS
# ==========================================================

print("\n2. VALIDACION DE LLAVES PRIMARIAS")

def validar_pk(df, columna, tabla):

    print(f"\nTabla: {tabla}")

    print("Total registros:", len(df))

    print(
        "Valores nulos en PK:",
        df[columna].isna().sum()
    )

    print(
        "Valores duplicados en PK:",
        df[columna].duplicated().sum()
    )

    print(
        "Valores unicos:",
        df[columna].nunique()
    )


validar_pk(
    pacientes,
    "id_paciente",
    "Pacientes"
)

validar_pk(
    prestadores,
    "id_prestador",
    "Prestadores"
)

validar_pk(
    atenciones,
    "id_atencion",
    "Atenciones"
)

validar_pk(
    casos,
    "id_caso",
    "Casos_Analiticos"
)


# ==========================================================
# 3. VALIDACION DE INTEGRIDAD REFERENCIAL
# ==========================================================

print("\n3. VALIDACION DE INTEGRIDAD REFERENCIAL")


# Atenciones -> Pacientes

atenciones_sin_paciente = atenciones[
    ~atenciones["id_paciente"].isin(
        pacientes["id_paciente"]
    )
]

print(
    "\nAtenciones con paciente inexistente:",
    len(atenciones_sin_paciente)
)


# Atenciones -> Prestadores

atenciones_sin_prestador = atenciones[
    ~atenciones["id_prestador"].isin(
        prestadores["id_prestador"]
    )
]

print(
    "Atenciones con prestador inexistente:",
    len(atenciones_sin_prestador)
)


# Casos Analiticos -> Pacientes

casos_sin_paciente = casos[
    ~casos["id_paciente"].isin(
        pacientes["id_paciente"]
    )
]

print(
    "Casos analiticos con paciente inexistente:",
    len(casos_sin_paciente)
)


# ==========================================================
# RESULTADO FINAL
# ==========================================================

print("\n" + "=" * 60)
print("VALIDACION DEL PUNTO 1 FINALIZADA")
print("=" * 60)

# ==========================================================
# PUNTO 2 - PERFIL DE CALIDAD DE DATOS
# ==========================================================

print("\n")
print("=" * 70)
print("PUNTO 2 - PERFIL DE CALIDAD DE DATOS")
print("=" * 70)


# ----------------------------------------------------------
# FUNCION GENERAL DE PERFILAMIENTO
# ----------------------------------------------------------

def perfil_calidad(df, nombre_tabla):

    total = len(df)

    resultados = []

    for columna in df.columns:

        nulos = df[columna].isna().sum()

        completos = total - nulos

        completitud = (completos / total) * 100

        unicos = df[columna].nunique(dropna=True)

        unicidad = (unicos / total) * 100

        resultados.append({
            "tabla": nombre_tabla,
            "columna": columna,
            "registros": total,
            "nulos": nulos,
            "completitud_pct": round(completitud, 2),
            "valores_unicos": unicos,
            "unicidad_pct": round(unicidad, 2)
        })

    return pd.DataFrame(resultados)


# Generar perfiles

perfil_pacientes = perfil_calidad(
    pacientes,
    "Pacientes"
)

perfil_prestadores = perfil_calidad(
    prestadores,
    "Prestadores"
)

perfil_atenciones = perfil_calidad(
    atenciones,
    "Atenciones"
)

perfil_casos = perfil_calidad(
    casos,
    "Casos_Analiticos"
)


perfil_general = pd.concat(
    [
        perfil_pacientes,
        perfil_prestadores,
        perfil_atenciones,
        perfil_casos
    ],
    ignore_index=True
)


print("\nPERFIL GENERAL")
print(perfil_general.to_string(index=False))

# ==========================================================
# VALIDEZ
# ==========================================================

print("\n")
print("-" * 70)
print("VALIDACION DE VALIDEZ")
print("-" * 70)


# ----------------------------------------------------------
# VALORES NEGATIVOS EN DIAS DE ESPERA
# ----------------------------------------------------------

esperas_negativas = atenciones[
    atenciones["dias_espera"] < 0
]

print(
    "\nDias de espera negativos:",
    len(esperas_negativas)
)

print(
    "Porcentaje:",
    round(
        len(esperas_negativas)
        / len(atenciones)
        * 100,
        2
    ),
    "%"
)


# ----------------------------------------------------------
# COSTOS NEGATIVOS
# ----------------------------------------------------------

costos_negativos = atenciones[
    atenciones["costo"] < 0
]

print(
    "\nCostos negativos:",
    len(costos_negativos)
)


# ----------------------------------------------------------
# EDADES FUERA DE RANGO
# ----------------------------------------------------------

edad_invalida = casos[
    (casos["edad"] < 0)
    |
    (casos["edad"] > 120)
]

print(
    "\nEdades fuera del rango 0-120:",
    len(edad_invalida)
)


# ----------------------------------------------------------
# REINGRESO 30D
# Solo debería contener 0 o 1
# ----------------------------------------------------------

reingreso_invalido = casos[
    ~casos["reingreso_30d"].isin([0, 1])
]

print(
    "\nValores invalidos en reingreso_30d:",
    len(reingreso_invalido)
)

# ==========================================================
# CONSISTENCIA
# ==========================================================

print("\n")
print("-" * 70)
print("VALIDACION DE CONSISTENCIA")
print("-" * 70)


# Fecha de cargue no debería ser anterior
# a la fecha de atención

fecha_inconsistente = atenciones[
    atenciones["fecha_cargue"]
    <
    atenciones["fecha_atencion"]
]

print(
    "\nFecha de cargue anterior a fecha de atencion:",
    len(fecha_inconsistente)
)


# Fecha de afiliación no debería ser
# anterior al nacimiento

afiliacion_inconsistente = pacientes[
    pacientes["fecha_afiliacion"]
    <
    pacientes["fecha_nacimiento"]
]

print(
    "Afiliacion anterior a nacimiento:",
    len(afiliacion_inconsistente)
)

# ==========================================================
# INTEGRIDAD REFERENCIAL
# ==========================================================

print("\n")
print("-" * 70)
print("INTEGRIDAD REFERENCIAL")
print("-" * 70)


impacto_paciente = (
    len(atenciones_sin_paciente)
    / len(atenciones)
    * 100
)

impacto_prestador = (
    len(atenciones_sin_prestador)
    / len(atenciones)
    * 100
)

impacto_casos = (
    len(casos_sin_paciente)
    / len(casos)
    * 100
)


print(
    "\nAtenciones sin paciente:",
    len(atenciones_sin_paciente),
    "-",
    round(impacto_paciente, 2),
    "%"
)

print(
    "Atenciones sin prestador:",
    len(atenciones_sin_prestador),
    "-",
    round(impacto_prestador, 2),
    "%"
)

print(
    "Casos sin paciente:",
    len(casos_sin_paciente),
    "-",
    round(impacto_casos, 2),
    "%"
)

# ==========================================================
# PUNTO 3 - TRATAMIENTO DE DATOS
# ==========================================================

print("\n")
print("=" * 70)
print("PUNTO 3 - TRATAMIENTO DE DATOS")
print("=" * 70)


# Crear copias para preservar los datos originales

pacientes_tratado = pacientes.copy()
prestadores_tratado = prestadores.copy()
atenciones_tratado = atenciones.copy()
casos_tratado = casos.copy()


# ----------------------------------------------------------
# ESTANDARIZAR CAMPOS DE TEXTO
# ----------------------------------------------------------

for columna in pacientes_tratado.select_dtypes(
    include="object"
).columns:

    pacientes_tratado[columna] = (
        pacientes_tratado[columna]
        .astype("string")
        .str.strip()
    )


for columna in atenciones_tratado.select_dtypes(
    include="object"
).columns:

    atenciones_tratado[columna] = (
        atenciones_tratado[columna]
        .astype("string")
        .str.strip()
    )


# ----------------------------------------------------------
# DIAS DE ESPERA INVALIDOS
# ----------------------------------------------------------

atenciones_tratado.loc[
    atenciones_tratado["dias_espera"] < 0,
    "dias_espera"
] = pd.NA


# ----------------------------------------------------------
# DUPLICADOS EXACTOS
# ----------------------------------------------------------

pacientes_tratado = pacientes_tratado.drop_duplicates()

prestadores_tratado = prestadores_tratado.drop_duplicates()

atenciones_tratado = atenciones_tratado.drop_duplicates()

casos_tratado = casos_tratado.drop_duplicates()


print(
    "\nTratamiento de calidad finalizado."
)

# ==========================================================
# PUNTO 4 - CONSULTAS SQL
# ==========================================================

print("\n")
print("=" * 70)
print("PUNTO 4 - CONSULTAS SQL")
print("=" * 70)

# Crear base de datos SQLite en memoria
conexion = sqlite3.connect(":memory:")

# Cargar los DataFrames como tablas SQL
pacientes.to_sql(
    "Pacientes",
    conexion,
    if_exists="replace",
    index=False
)

prestadores.to_sql(
    "Prestadores",
    conexion,
    if_exists="replace",
    index=False
)

atenciones.to_sql(
    "Atenciones",
    conexion,
    if_exists="replace",
    index=False
)

casos.to_sql(
    "Casos_Analiticos",
    conexion,
    if_exists="replace",
    index=False
)

print("Tablas cargadas correctamente en SQLite.")

# ==========================================================
# CONSULTA 1
# Tendencia mensual de atenciones y costos
# ==========================================================

consulta_1 = """

SELECT
    strftime('%Y-%m', fecha_atencion) AS periodo,
    COUNT(*) AS total_atenciones,
    ROUND(SUM(costo), 2) AS costo_total,
    ROUND(AVG(costo), 2) AS costo_promedio
FROM Atenciones
GROUP BY strftime('%Y-%m', fecha_atencion)
ORDER BY periodo;

"""

resultado_1 = pd.read_sql_query(
    consulta_1,
    conexion
)

print("\nCONSULTA 1 - TENDENCIA MENSUAL")
print(resultado_1.to_string(index=False))

# ==========================================================
# CONSULTA 2
# Tasa de cancelacion e inasistencia
# ==========================================================

consulta_2 = """

SELECT

    COUNT(*) AS total_atenciones,

    SUM(
        CASE
            WHEN estado_atencion = 'Cancelada'
            THEN 1
            ELSE 0
        END
    ) AS canceladas,

    SUM(
        CASE
            WHEN estado_atencion = 'No asistió'
            THEN 1
            ELSE 0
        END
    ) AS inasistencias,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN estado_atencion = 'Cancelada'
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS tasa_cancelacion_pct,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN estado_atencion = 'No asistió'
                THEN 1
                ELSE 0
            END
        )
        / COUNT(*),
        2
    ) AS tasa_inasistencia_pct

FROM Atenciones;

"""

resultado_2 = pd.read_sql_query(
    consulta_2,
    conexion
)

print("\nCONSULTA 2 - CANCELACION E INASISTENCIA")
print(resultado_2.to_string(index=False))

# ==========================================================
# CONSULTA 3
# Prestadores con mayor costo promedio
# ==========================================================

consulta_3 = """

SELECT

    p.id_prestador,
    p.nombre_prestador,

    COUNT(a.id_atencion) AS total_atenciones,

    ROUND(
        AVG(a.costo),
        2
    ) AS costo_promedio,

    ROUND(
        SUM(a.costo),
        2
    ) AS costo_total

FROM Atenciones a

INNER JOIN Prestadores p
    ON a.id_prestador = p.id_prestador

WHERE a.estado_atencion = 'Atendida'

GROUP BY
    p.id_prestador,
    p.nombre_prestador

ORDER BY costo_promedio DESC;

"""

resultado_3 = pd.read_sql_query(
    consulta_3,
    conexion
)

print("\nCONSULTA 3 - COSTO PROMEDIO POR PRESTADOR")
print(resultado_3.to_string(index=False))

# ==========================================================
# CONSULTA 4
# Pacientes con uso recurrente
# ==========================================================

consulta_4 = """

SELECT

    p.id_paciente,
    p.nombre,
    p.apellido,

    COUNT(a.id_atencion) AS total_atenciones,

    ROUND(
        SUM(a.costo),
        2
    ) AS costo_total,

    ROUND(
        AVG(a.costo),
        2
    ) AS costo_promedio

FROM Pacientes p

INNER JOIN Atenciones a
    ON p.id_paciente = a.id_paciente

WHERE a.estado_atencion = 'Atendida'

GROUP BY
    p.id_paciente,
    p.nombre,
    p.apellido

HAVING COUNT(a.id_atencion) >= 5

ORDER BY total_atenciones DESC;

"""

resultado_4 = pd.read_sql_query(
    consulta_4,
    conexion
)

print("\nCONSULTA 4 - PACIENTES CON USO RECURRENTE")
print(resultado_4.to_string(index=False))

# ==========================================================
# CONSULTA 5
# Oportunidad de atencion
# ==========================================================

consulta_5 = """

SELECT

    p.id_prestador,
    p.nombre_prestador,

    COUNT(a.id_atencion) AS total_atenciones,

    ROUND(
        AVG(a.dias_espera),
        2
    ) AS espera_promedio,

    MIN(a.dias_espera) AS espera_minima,

    MAX(a.dias_espera) AS espera_maxima

FROM Atenciones a

INNER JOIN Prestadores p
    ON a.id_prestador = p.id_prestador

WHERE
    a.estado_atencion = 'Atendida'

    AND a.dias_espera >= 0

GROUP BY
    p.id_prestador,
    p.nombre_prestador

ORDER BY espera_promedio DESC;

"""

resultado_5 = pd.read_sql_query(
    consulta_5,
    conexion
)

print("\nCONSULTA 5 - OPORTUNIDAD POR PRESTADOR")
print(resultado_5.to_string(index=False))

# ==========================================================
# CONSULTA 6
# Costos y utilizacion por canal
# ==========================================================

consulta_6 = """

SELECT

    canal,

    COUNT(*) AS total_atenciones,

    ROUND(
        AVG(costo),
        2
    ) AS costo_promedio,

    ROUND(
        SUM(costo),
        2
    ) AS costo_total

FROM Atenciones

WHERE estado_atencion = 'Atendida'

GROUP BY canal

ORDER BY costo_total DESC;

"""

resultado_6 = pd.read_sql_query(
    consulta_6,
    conexion
)

print("\nCONSULTA 6 - ANALISIS POR CANAL")
print(resultado_6.to_string(index=False))

# ==========================================================
# PARTE B - ANALITICA Y MODELO PREDICTIVO
# PUNTO 5 - ANALISIS EXPLORATORIO
# ==========================================================

print("\n")
print("=" * 70)
print("PARTE B - ANALITICA Y MODELO PREDICTIVO")
print("=" * 70)

# Se crea una copia para no modificar el DataFrame original

df_modelo = casos.copy()

print("\nDIMENSIONES DE CASOS_ANALITICOS")
print(df_modelo.shape)

print("\nTIPOS DE DATOS")
print(df_modelo.dtypes)

print("\nVALORES FALTANTES")
print(df_modelo.isna().sum())

print("\nDUPLICADOS EXACTOS")
print(df_modelo.duplicated().sum())

print("\nDISTRIBUCION DE LA VARIABLE OBJETIVO")

distribucion_objetivo = (
    df_modelo["reingreso_30d"]
    .value_counts()
    .sort_index()
)

porcentaje_objetivo = (
    df_modelo["reingreso_30d"]
    .value_counts(normalize=True)
    .sort_index()
    * 100
)

print("Frecuencia:")
print(distribucion_objetivo)

print("\nPorcentaje:")
print(porcentaje_objetivo.round(2))

# ==========================================================
# ESTADISTICA DESCRIPTIVA POR REINGRESO
# ==========================================================

variables_numericas = [
    "edad",
    "atenciones_6m",
    "condiciones_cronicas",
    "urgencias_6m",
    "costo_promedio_6m",
    "inasistencias_6m",
    "dias_espera_promedio"
]

resumen_por_reingreso = (
    df_modelo
    .groupby("reingreso_30d")[variables_numericas]
    .mean()
    .round(2)
    .T
)

resumen_por_reingreso.columns = [
    "No_reingresa",
    "Reingresa"
]

resumen_por_reingreso["diferencia"] = (
    resumen_por_reingreso["Reingresa"]
    -
    resumen_por_reingreso["No_reingresa"]
)

print("\nPROMEDIOS SEGUN REINGRESO")
print(resumen_por_reingreso)

# Grafico_1: Exploratorio:

plt.figure(figsize=(7, 5))

sns.countplot(
    data=df_modelo,
    x="reingreso_30d",
    color="#7A1F78"
)

plt.title("Distribucion del reingreso a 30 dias")
plt.xlabel("Reingreso en 30 dias")
plt.ylabel("Numero de casos")
plt.xticks(
    ticks=[0, 1],
    labels=["No", "Si"]
)

plt.tight_layout()
plt.savefig(
    "01_distribucion_reingreso.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Grafico 1 generado correctamente.")

# Grafico_2: Comparación de Variables:

fig, ejes = plt.subplots(
    2,
    3,
    figsize=(16, 9)
)

variables_grafico = [
    "atenciones_6m",
    "condiciones_cronicas",
    "urgencias_6m",
    "inasistencias_6m",
    "dias_espera_promedio",
    "costo_promedio_6m"
]

for eje, variable in zip(
    ejes.flatten(),
    variables_grafico
):

    sns.boxplot(
        data=df_modelo,
        x="reingreso_30d",
        y=variable,
        ax=eje,
        color="#B76AAD"
    )

    eje.set_title(variable)

    eje.set_xlabel(
        "Reingreso en 30 dias"
    )

plt.tight_layout()
plt.savefig(
    "02_variables_reingreso.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Grafico 2 generado correctamente.")

# Grafico_3: Matriz de correlación:

plt.figure(figsize=(11, 8))

matriz_correlacion = (
    df_modelo[
        variables_numericas
        +
        ["reingreso_30d"]
    ]
    .corr()
)

sns.heatmap(
    matriz_correlacion,
    annot=True,
    cmap="RdPu",
    fmt=".2f"
)

plt.title(
    "Correlacion entre variables numericas"
)

plt.tight_layout()
plt.savefig(
    "03_matriz_correlacion.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Grafico 3 generado correctamente.")

# ==========================================================
# PUNTO 7: Construcción del modelo
# # ==========================================================

from sklearn.model_selection import train_test_split

from sklearn.compose import ColumnTransformer

from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler
)

from sklearn.pipeline import Pipeline

from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    precision_recall_curve,
    RocCurveDisplay,
    PrecisionRecallDisplay,
    ConfusionMatrixDisplay
)

# ==========================================================
# PREPARACION DEL MODELO
# ==========================================================

variables_numericas_modelo = [
    "edad",
    "atenciones_6m",
    "condiciones_cronicas",
    "urgencias_6m",
    "costo_promedio_6m",
    "inasistencias_6m",
    "dias_espera_promedio"
]

variables_categoricas_modelo = [
    "segmento_operativo"
]

variables_modelo = (
    variables_numericas_modelo
    +
    variables_categoricas_modelo
)

X = df_modelo[variables_modelo].copy()

y = (
    df_modelo["reingreso_30d"]
    .astype(int)
)

# Identificadores separados para trazabilidad

identificadores = df_modelo[
    [
        "id_caso",
        "id_paciente",
        "fecha_corte"
    ]
].copy()

# División entrenamiento/prueba

X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = (
    train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )
)

print("\nTAMANO DE LOS CONJUNTOS")

print(
    "Entrenamiento:",
    X_entrenamiento.shape
)

print(
    "Prueba:",
    X_prueba.shape
)

print(
    "\nDistribucion en entrenamiento:"
)

print(
    y_entrenamiento
    .value_counts(normalize=True)
    .round(3)
)

print(
    "\nDistribucion en prueba:"
)

print(
    y_prueba
    .value_counts(normalize=True)
    .round(3)
)

# ==========================================================
# PREPROCESAMIENTO
# ==========================================================

proceso_numerico = Pipeline(
    steps=[
        (
            "imputacion",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "escalado",
            StandardScaler()
        )
    ]
)

proceso_categorico = Pipeline(
    steps=[
        (
            "imputacion",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "codificacion",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

preprocesador = ColumnTransformer(
    transformers=[
        (
            "numericas",
            proceso_numerico,
            variables_numericas_modelo
        ),
        (
            "categoricas",
            proceso_categorico,
            variables_categoricas_modelo
        )
    ]
)

# ==========================================================
# REGRESION LOGISTICA
# ==========================================================

modelo_logistico = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)

pipeline_modelo = Pipeline(
    steps=[
        (
            "preprocesamiento",
            preprocesador
        ),
        (
            "modelo",
            modelo_logistico
        )
    ]
)

pipeline_modelo.fit(
    X_entrenamiento,
    y_entrenamiento
)

probabilidad_reingreso = (
    pipeline_modelo
    .predict_proba(X_prueba)[:, 1]
)

print(
    "\nModelo entrenado correctamente."
)

# PUNTO 8. Métricas y umbral
# Calcular métricas

roc_auc = roc_auc_score(
    y_prueba,
    probabilidad_reingreso
)

pr_auc = average_precision_score(
    y_prueba,
    probabilidad_reingreso
)

print("\nMETRICAS SIN DEPENDER DEL UMBRAL")

print(
    "ROC-AUC:",
    round(roc_auc, 3)
)

print(
    "PR-AUC:",
    round(pr_auc, 3)
)

# ==========================================================
# EVALUACION DE UMBRALES
# ==========================================================

def evaluar_umbral(
    y_real,
    probabilidades,
    umbral
):

    prediccion = (
        probabilidades >= umbral
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_real,
        prediccion
    ).ravel()

    return {
        "umbral": umbral,
        "casos_priorizados": int(
            prediccion.sum()
        ),
        "precision": round(
            precision_score(
                y_real,
                prediccion,
                zero_division=0
            ),
            3
        ),
        "recall": round(
            recall_score(
                y_real,
                prediccion
            ),
            3
        ),
        "f1": round(
            f1_score(
                y_real,
                prediccion
            ),
            3
        ),
        "verdaderos_positivos": int(tp),
        "falsos_positivos": int(fp),
        "falsos_negativos": int(fn),
        "verdaderos_negativos": int(tn)
    }


resultados_umbrales = pd.DataFrame(
    [
        evaluar_umbral(
            y_prueba,
            probabilidad_reingreso,
            umbral
        )
        for umbral in [
            0.40,
            0.50,
            0.60,
            0.70
        ]
    ]
)

print("\nCOMPARACION DE UMBRALES")
print(
    resultados_umbrales
    .to_string(index=False)
)

# ==========================================================
# RESULTADOS CON UMBRAL SELECCIONADO
# ==========================================================

# ==========================================================
# RESULTADOS CON UMBRAL SELECCIONADO
# ==========================================================

print("\n" + "=" * 70)
print("RESULTADOS CON UMBRAL SELECCIONADO")
print("=" * 70)

umbral_seleccionado = 0.50

# Convertir probabilidades en una clasificación 0 / 1
prediccion_final = (
    probabilidad_reingreso >= umbral_seleccionado
).astype(int)


# ==========================================================
# METRICAS DEL MODELO CON UMBRAL 0.50
# ==========================================================

precision_final = precision_score(
    y_prueba,
    prediccion_final,
    zero_division=0
)

recall_final = recall_score(
    y_prueba,
    prediccion_final
)

f1_final = f1_score(
    y_prueba,
    prediccion_final
)

matriz = confusion_matrix(
    y_prueba,
    prediccion_final
)

tn, fp, fn, tp = matriz.ravel()


print("\nMETRICAS CON UMBRAL 0.50")

print(
    "Precision:",
    round(precision_final, 3)
)

print(
    "Recall:",
    round(recall_final, 3)
)

print(
    "F1:",
    round(f1_final, 3)
)

print("\nMATRIZ DE CONFUSION")

print(
    "Verdaderos negativos:",
    tn
)

print(
    "Falsos positivos:",
    fp
)

print(
    "Falsos negativos:",
    fn
)

print(
    "Verdaderos positivos:",
    tp
)

# ==========================================================
# REPORTE DE CLASIFICACION
# ==========================================================

print("\nREPORTE DE CLASIFICACION")

reporte = classification_report(
    y_prueba,
    prediccion_final,
    target_names=[
        "No reingresa",
        "Reingresa"
    ],
    zero_division=0
)

print(reporte)

# ==========================================================
# GRAFICO 4 - MATRIZ DE CONFUSION
# ==========================================================

print(
    "\nGenerando matriz de confusion..."
)

fig, ax = plt.subplots(
    figsize=(7, 5)
)

ConfusionMatrixDisplay.from_predictions(
    y_prueba,
    prediccion_final,
    display_labels=[
        "No reingresa",
        "Reingresa"
    ],
    cmap="Purples",
    ax=ax
)

ax.set_title(
    "Matriz de confusion - Umbral 0.50"
)

fig.tight_layout()

fig.savefig(
    "04_matriz_confusion.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

print(
    "Grafico 4 generado correctamente."
)

#Curva ROC

# ==========================================================
# GRAFICO 5 - CURVA ROC
# ==========================================================

print(
    "\nGenerando curva ROC..."
)

fig, ax = plt.subplots(
    figsize=(7, 5)
)

RocCurveDisplay.from_predictions(
    y_prueba,
    probabilidad_reingreso,
    ax=ax
)

ax.set_title(
    "Curva ROC - Reingreso a 30 dias"
)

fig.tight_layout()

fig.savefig(
    "05_curva_roc.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

print(
    "Grafico 5 generado correctamente."
)

# ==========================================================
# GRAFICO 6 - CURVA PRECISION RECALL
# ==========================================================

print(
    "\nGenerando curva Precision-Recall..."
)

fig, ax = plt.subplots(
    figsize=(7, 5)
)

PrecisionRecallDisplay.from_predictions(
    y_prueba,
    probabilidad_reingreso,
    ax=ax
)

ax.set_title(
    "Curva Precision-Recall - Reingreso a 30 dias"
)

fig.tight_layout()

fig.savefig(
    "06_precision_recall.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close(fig)

print(
    "Grafico 6 generado correctamente."
)

# ==========================================================
# TABLA FINAL DE PRIORIZACION
# ==========================================================

print("\n" + "=" * 70)
print("GENERANDO TABLA DE PRIORIZACION")
print("=" * 70)


# Recuperar identificadores correspondientes
# únicamente al conjunto de prueba

identificadores_prueba = (
    identificadores
    .loc[X_prueba.index]
    .copy()
)


# Reiniciar índice

priorizacion = (
    identificadores_prueba
    .reset_index(drop=True)
)


# Agregar probabilidad calculada

priorizacion[
    "probabilidad_reingreso"
] = probabilidad_reingreso


# Agregar clasificación

priorizacion[
    "priorizar"
] = np.where(
    priorizacion[
        "probabilidad_reingreso"
    ] >= umbral_seleccionado,
    "Si",
    "No"
)


# Ordenar del mayor al menor riesgo

priorizacion = (
    priorizacion
    .sort_values(
        by="probabilidad_reingreso",
        ascending=False
    )
    .reset_index(drop=True)
)

# ==========================================================
# CLASIFICACION DEL NIVEL DE RIESGO
# ==========================================================

priorizacion[
    "nivel_riesgo"
] = pd.cut(
    priorizacion[
        "probabilidad_reingreso"
    ],
    bins=[
        0,
        0.40,
        0.50,
        0.70,
        1.00
    ],
    labels=[
        "Bajo",
        "Medio",
        "Alto",
        "Muy alto"
    ],
    include_lowest=True
)

# ==========================================================
# CASOS CON MAYOR RIESGO
# ==========================================================

print(
    "\nPRIMEROS 20 CASOS PRIORIZADOS"
)

print(
    priorizacion[
        [
            "id_caso",
            "id_paciente",
            "fecha_corte",
            "probabilidad_reingreso",
            "nivel_riesgo",
            "priorizar"
        ]
    ]
    .head(20)
    .to_string(index=False)
)

# ==========================================================
# RESUMEN DE PRIORIZACION
# ==========================================================

total_evaluados = len(
    priorizacion
)

total_priorizados = (
    priorizacion["priorizar"]
    .eq("Si")
    .sum()
)

porcentaje_priorizado = (
    total_priorizados
    /
    total_evaluados
    *
    100
)


print("\nRESUMEN DE PRIORIZACION")

print(
    "Casos evaluados:",
    total_evaluados
)

print(
    "Casos priorizados:",
    total_priorizados
)

print(
    "Porcentaje priorizado:",
    round(
        porcentaje_priorizado,
        2
    ),
    "%"
)

# ==========================================================
# DISTRIBUCION POR NIVEL DE RIESGO
# ==========================================================

distribucion_riesgo = (
    priorizacion[
        "nivel_riesgo"
    ]
    .value_counts()
    .sort_index()
)

print(
    "\nDISTRIBUCION POR NIVEL DE RIESGO"
)

print(
    distribucion_riesgo
)

# ==========================================================
# EXPORTAR RESULTADOS
# ==========================================================

priorizacion.to_excel(
    "priorizacion_reingreso_30d.xlsx",
    index=False,
    engine="openpyxl"
)

print(
    "\nArchivo priorizacion_reingreso_30d.xlsx "
    "generado correctamente."
)

    # ==========================================================
# FINALIZACION
# ==========================================================

print("\n" + "=" * 70)

print(
    "PARTE B FINALIZADA CORRECTAMENTE"
)

print("=" * 70)