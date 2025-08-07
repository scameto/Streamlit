import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Reporte de Cosecha y Mermas", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("data/ordenes de carga.xlsx", sheet_name=0)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "Fecha": "fecha",
        "Empresa": "empresa",
        "Cultivo": "cultivo",
        "Kg Origen": "kg_origen",
        "Kg Final": "kg_final",
        "Humedad": "humedad",
        "Diferencia Kg": "dif_kg",
        "Diferencia %": "dif_pct"
    })
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["kg_origen"] = pd.to_numeric(df["kg_origen"], errors="coerce")
    df["kg_final"] = pd.to_numeric(df["kg_final"], errors="coerce")
    df["dif_kg"] = pd.to_numeric(df["dif_kg"], errors="coerce")
    df["dif_pct"] = pd.to_numeric(df["dif_pct"], errors="coerce")
    return df.dropna(subset=["fecha", "empresa", "cultivo"])

df = cargar_datos()

# Filtros
st.sidebar.header("🎛️ Filtros")
empresas = st.sidebar.multiselect("Empresa", df["empresa"].unique(), default=df["empresa"].unique())
cultivos = st.sidebar.multiselect("Cultivo", df["cultivo"].unique(), default=df["cultivo"].unique())
rango_fechas = st.sidebar.date_input("Rango de fechas", [df["fecha"].min(), df["fecha"].max()])

df_filtrado = df[
    (df["empresa"].isin(empresas)) &
    (df["cultivo"].isin(cultivos)) &
    (df["fecha"] >= pd.to_datetime(rango_fechas[0])) &
    (df["fecha"] <= pd.to_datetime(rango_fechas[1]))
]

st.title("🚜 Reporte de Rendimiento y Mermas por Cosecha")

if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados.")
else:
    # Resumen diario
    resumen_diario = df_filtrado.groupby("fecha").agg({
        "kg_origen": "sum",
        "kg_final": "sum",
        "dif_kg": "sum"
    }).reset_index()
    resumen_diario["avance_acumulado"] = resumen_diario["kg_final"].cumsum()

    st.subheader("📅 Producción diaria (Kg Final)")
    fig = px.bar(resumen_diario, x="fecha", y="kg_final", text_auto=True, labels={"kg_final": "Kg netos"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Avance acumulado de cosecha")
    fig = px.line(resumen_diario, x="fecha", y="avance_acumulado", markers=True, labels={"avance_acumulado": "Kg acumulados"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📉 Comparación Kg Origen vs Kg Final")
    fig = px.bar(resumen_diario, x="fecha", y=["kg_origen", "kg_final"], barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⚖️ Mermas por día (Kg)")
    fig = px.bar(resumen_diario, x="fecha", y="dif_kg", text_auto=True, labels={"dif_kg": "Merma (Kg)"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Resumen por Cultivo y Empresa")
    resumen_cultivo = df_filtrado.groupby(["empresa", "cultivo"]).agg({
        "kg_origen": "sum",
        "kg_final": "sum",
        "dif_kg": "sum"
    }).reset_index()
    resumen_cultivo["dif_pct"] = resumen_cultivo["dif_kg"] / resumen_cultivo["kg_origen"]

    st.dataframe(resumen_cultivo, use_container_width=True)
