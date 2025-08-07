import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import os
import json

st.set_page_config(page_title="Análisis Económico por Especie", layout="wide")

# Ruta donde se guardan los parámetros
PARAMS_FILE = "data/parametros_por_especie.json"

# Crear archivo JSON si no existe
if not os.path.exists(PARAMS_FILE):
    with open(PARAMS_FILE, "w") as f:
        json.dump({}, f)

def cargar_parametros():
    with open(PARAMS_FILE, "r") as f:
        return json.load(f)

def guardar_parametros(parametros_actualizados):
    with open(PARAMS_FILE, "w") as f:
        json.dump(parametros_actualizados, f, indent=2)

@st.cache_data
def cargar_produccion():
    df = pd.read_excel("data/Produccion Por Cultivo.xlsx", sheet_name="Hoja1")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "Cultivo": "cultivo",
        "Especie": "especie",
        "Campo": "campo",
        "Superficie (ha)": "sup_total",
        "Sup. Cosechada (ha)": "sup_cosechada",
        "Ton Chacra": "ton_chacra",
        "Rinde Acondicionado (tn/ha)": "rinde_ha"
    })
    for col in ["rinde_ha", "ton_chacra", "sup_cosechada"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

@st.cache_data
def cargar_costos():
    df = pd.read_excel("data/InformeOtRealizadas_al_2025-07-19.xlsx")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"Cultivo": "cultivo", "Total": "costo_total", "Tipo Insumo": "tipo"})
    df["costo_total"] = pd.to_numeric(df["costo_total"], errors="coerce")
    return df

# Cargar datos
df_prod = cargar_produccion()
df_costos = cargar_costos()

# Filtros en sidebar
st.sidebar.header("🔎 Filtros de análisis")

empresa_opciones = df_prod["empresa"] if "empresa" in df_prod.columns else ["Sin empresa"]
campo_opciones = df_prod["campo"].unique()
especie_opciones = df_prod["especie"].unique()

empresa_seleccionada = st.sidebar.selectbox("Empresa", sorted(empresa_opciones))
campo_seleccionado = st.sidebar.multiselect("Campo", sorted(campo_opciones), default=campo_opciones)
especies_seleccionadas = st.sidebar.multiselect("Especie", sorted(especie_opciones), default=especie_opciones)

# Aplicar filtros a df_prod
df_prod = df_prod[
    (df_prod["campo"].isin(campo_seleccionado)) &
    (df_prod["especie"].isin(especies_seleccionadas))
]

# También filtrar costos a los cultivos resultantes
df_costos = df_costos[df_costos["cultivo"].isin(df_prod["cultivo"])]


# Agrupación de costos por cultivo
df_costos_agg = df_costos.groupby(["cultivo", "tipo"])["costo_total"].sum().reset_index()
df_costos_totales = df_costos.groupby("cultivo")["costo_total"].sum().reset_index()

# Merge con producción
df = pd.merge(df_prod, df_costos_totales, on="cultivo", how="left")
df["costo_total"] = df["costo_total"].fillna(0)

st.title("💰 Análisis Económico por Especie")

especies_unicas = df["especie"].unique()
parametros_json = cargar_parametros()
parametros = {}

st.sidebar.header("📥 Ingresá parámetros por especie")

for especie in especies_unicas:
    especie_params = parametros_json.get(especie, {
        "arrendamiento": 360.0,
        "flete": 17.0,
        "precio_bruto": 360.0,
        "precio_neto": 352.0
    })

    with st.sidebar.expander(f"⚙️ Parámetros - {especie}"):
        arr = st.number_input(f"Arrendamiento (USD/ha) - {especie}", min_value=0.0, value=especie_params["arrendamiento"], step=1.0, key=f"arr_{especie}")
        flete = st.number_input(f"Flete (USD/ton) - {especie}", min_value=0.0, value=especie_params["flete"], step=1.0, key=f"flt_{especie}")
        precio_bruto = st.number_input(f"Precio Bruto (USD/tn) - {especie}", min_value=0.0, value=especie_params["precio_bruto"], step=1.0, key=f"bruto_{especie}")
        precio_neto = st.number_input(f"Precio Neto (USD/tn) - {especie}", min_value=0.0, value=especie_params["precio_neto"], step=1.0, key=f"neto_{especie}")

        parametros[especie] = {
            "arrendamiento": arr,
            "flete": flete,
            "precio_bruto": precio_bruto,
            "precio_neto": precio_neto
        }

# Botón para guardar parámetros
if st.sidebar.button("💾 Guardar parámetros"):
    guardar_parametros(parametros)
    st.sidebar.success("Parámetros guardados correctamente ✅")

# Cálculos económicos
resultados = []

for _, row in df.iterrows():
    especie = row["especie"]
    cultivo = row["cultivo"]
    sup = row["sup_cosechada"]
    rinde = row["rinde_ha"]
    costo_total = row["costo_total"]

    p = parametros.get(especie, parametros_json.get(especie, {
        "arrendamiento": 360.0,
        "flete": 17.0,
        "precio_bruto": 360.0,
        "precio_neto": 352.0
    }))

    ingreso_bruto_ha = rinde * p["precio_bruto"]
    ingreso_neto_ha = rinde * p["precio_neto"]
    flete_ha = rinde * p["flete"]
    ingreso_final_ha = ingreso_neto_ha - flete_ha - p["arrendamiento"] - (costo_total / sup if sup > 0 else 0)
    ingreso_final_total = ingreso_final_ha * sup

    resultados.append({
        "Especie": especie,
        "Cultivo": cultivo,
        "Campo": row["campo"],
        "Sup. Cosechada": sup,
        "Rinde (tn/ha)": rinde,
        "Ingreso Bruto (USD/ha)": ingreso_bruto_ha,
        "Ingreso Neto (USD/ha)": ingreso_neto_ha,
        "Costo Total OC (USD)": costo_total,
        "Flete (USD/ha)": flete_ha,
        "Arrendamiento (USD/ha)": p["arrendamiento"],
        "Ingreso Final (USD/ha)": ingreso_final_ha,
        "Ingreso Final Total (USD)": ingreso_final_total
    })

resumen_df = pd.DataFrame(resultados)

# Desglose de costos
resumen_df["Costo Unitario (USD/ha)"] = resumen_df["Costo Total OC (USD)"] / resumen_df["Sup. Cosechada"]
resumen_df["Costo Total (USD/ha)"] = (
    resumen_df["Costo Unitario (USD/ha)"]
    + resumen_df["Arrendamiento (USD/ha)"]
    + resumen_df["Flete (USD/ha)"]
)
resumen_df["Margen (USD/ha)"] = resumen_df["Ingreso Neto (USD/ha)"] - resumen_df["Costo Total (USD/ha)"]

cultivos_ordenados = resumen_df.sort_values("Ingreso Final Total (USD)", ascending=False)["Cultivo"].tolist()


# Mostrar resultados
st.subheader("📋 Tabla Resumen Económico")
st.dataframe(resumen_df, use_container_width=True)

st.subheader("📈 Ingreso Final por ha")
fig = px.bar(resumen_df, x="Cultivo", y="Ingreso Final (USD/ha)", color="Especie", text_auto=".2f", category_orders={"Cultivo": cultivos_ordenados}
)


st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Ingreso Final Total por Cultivo")
fig2 = px.bar(resumen_df, x="Cultivo", y="Ingreso Final Total (USD)", color="Especie", text_auto=".2s", category_orders={"Cultivo": cultivos_ordenados}
)


st.plotly_chart(fig2, use_container_width=True)

st.subheader("📊 Composición de Costos y Margen por Cultivo")

# Preparar datos para gráfico apilado
stack_data = resumen_df[[
    "Cultivo",
    "Costo Unitario (USD/ha)",
    "Arrendamiento (USD/ha)",
    "Flete (USD/ha)",
    "Margen (USD/ha)"
]].copy()

stack_data = stack_data.melt(id_vars="Cultivo", 
                              var_name="Componente", 
                              value_name="USD/ha")

fig_stack = px.bar(
    stack_data,
    x="Cultivo",
    y="USD/ha",
    color="Componente",
    title="Composición de Costos y Margen (USD/ha)",
    text_auto=".2f",
    category_orders={"Cultivo": cultivos_ordenados}

)


fig_stack.update_layout(barmode="stack", xaxis_title="Cultivo", yaxis_title="USD/ha")
st.plotly_chart(fig_stack, use_container_width=True)


# Exportar a Excel
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    resumen_df.to_excel(writer, index=False, sheet_name='Resumen')
    df_costos_agg.to_excel(writer, index=False, sheet_name='Costos Desglosados')
    excel_data = output.getvalue()

st.download_button(
    label="📥 Descargar Excel",
    data=excel_data,
    file_name="analisis_economico_especie.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
