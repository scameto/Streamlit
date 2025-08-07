import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Producción por Cultivo", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("data/Produccion Por Cultivo.xlsx", sheet_name="Hoja1")
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "Cultivo": "cultivo",
        "Especie": "especie",
        "Campo": "campo",
        "Superficie (ha)": "sup_total",
        "Sup. Cosechada (ha)": "sup_cosechada",
        "% Avance": "avance",
        "Ton Chacra": "ton_chacra",
        "Rinde Chacra (tn/ha)": "rinde_chacra",
        "Ton Destino": "ton_destino",
        "Rinde Destino (tn/ha)": "rinde_destino",
        "Ton Acondicionado": "ton_acondicionado",
        "Rinde Acondicionado (tn/ha)": "rinde_acondicionado"
    })
    for col in ["sup_total", "sup_cosechada", "avance", "ton_chacra", "rinde_chacra",
                "ton_destino", "rinde_destino", "ton_acondicionado", "rinde_acondicionado"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = cargar_datos()

# Filtros
st.sidebar.header("🎛️ Filtros")
campos = st.sidebar.multiselect("Campo", df["campo"].unique(), default=df["campo"].unique())
especies = st.sidebar.multiselect("Especie", df["especie"].unique(), default=df["especie"].unique())
cultivos = st.sidebar.multiselect("Cultivo", df["cultivo"].unique(), default=df["cultivo"].unique())

df_filtrado = df[
    (df["campo"].isin(campos)) &
    (df["especie"].isin(especies)) &
    (df["cultivo"].isin(cultivos))
]

st.title("🌾 Producción por Cultivo")

if df_filtrado.empty:
    st.warning("No hay datos para los filtros seleccionados.")
else:
    st.subheader("📊 Tabla resumen de producción")
    st.dataframe(df_filtrado, use_container_width=True)

    st.subheader("📦 Producción total por cultivo (toneladas)")
    fig = px.bar(
        df_filtrado,
        x="cultivo",
        y="ton_chacra",
        text_auto=".2s",
        labels={"ton_chacra": "Toneladas"},
        title="Producción total por cultivo"
    )
    fig.update_layout(xaxis_title="Cultivo", yaxis_title="Toneladas")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Rendimiento por ha (tn/ha)")
    fig = px.bar(
        df_filtrado,
        x="cultivo",
        y="rinde_acondicionado",
        text_auto=".2f",
        title="Rinde Acondicionado por Cultivo",
        labels={"rinde_acondicionado": "tn/ha"}
    )
    fig.update_layout(xaxis_title="Cultivo", yaxis_title="Rendimiento (tn/ha)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 Participación de producción por especie")
    fig = px.pie(
        df_filtrado,
        names="especie",
        values="ton_chacra",
        title="Distribución de producción por especie"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🥧 Participación de producción por cultivo")
    fig = px.pie(
        df_filtrado,
        names="cultivo",
        values="ton_chacra",
        title="Distribución de producción por cultivo"
    )
    st.plotly_chart(fig, use_container_width=True)
