import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="EDA Empleados", layout="wide")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/employees.csv")
    df.columns = df.columns.str.strip()  # Eliminar espacios accidentales
    return df

df = cargar_datos()

# Sidebar de filtros
st.sidebar.header("🎛️ Filtros")
generos = st.sidebar.multiselect("Género", df["Gender"].unique(), default=df["Gender"].unique())
unidades = st.sidebar.multiselect("Unidad", df["Unit"].unique(), default=df["Unit"].unique())
edad_min, edad_max = st.sidebar.slider("Edad", int(df["Age"].min()), int(df["Age"].max()), (int(df["Age"].min()), int(df["Age"].max())))

# Aplicar filtros
df_filtrado = df[
    (df["Gender"].isin(generos)) &
    (df["Unit"].isin(unidades)) &
    (df["Age"] >= edad_min) &
    (df["Age"] <= edad_max)
]

# Pestañas
tab1, tab2, tab3 = st.tabs(["📊 General", "📈 Univariado", "📉 Bivariado"])

with tab1:
    st.title("📊 Visión General de Empleados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Empleados", df_filtrado.shape[0])
    col2.metric("Edad Promedio", round(df_filtrado["Age"].mean(), 1))
    col3.metric("Años de Servicio Promedio", round(df_filtrado["Time_of_service"].mean(), 1))
    
    st.dataframe(df_filtrado.head(20), use_container_width=True)

with tab2:
    st.title("📈 Análisis Univariado")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de Edad")
        fig, ax = plt.subplots()
        sns.histplot(df_filtrado["Age"], kde=True, bins=15, ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("Distribución del Salario (Pay_Scale)")
        fig, ax = plt.subplots()
        sns.countplot(data=df_filtrado, x="Pay_Scale", ax=ax)
        st.pyplot(fig)

    st.subheader("Unidades más frecuentes")
    fig, ax = plt.subplots(figsize=(10, 4))
    df_filtrado["Unit"].value_counts().plot(kind='barh', ax=ax)
    st.pyplot(fig)

with tab3:
    st.title("📉 Análisis Bivariado")

    st.subheader("Edad vs Tasa de atrición")
    fig, ax = plt.subplots()
    sns.scatterplot(data=df_filtrado, x="Age", y="Attrition_rate", hue="Gender", ax=ax)
    st.pyplot(fig)

    st.subheader("Tasa de atrición por unidad")
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df_filtrado, x="Unit", y="Attrition_rate", ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    st.subheader("Balance vida-trabajo por nivel de puesto")
    fig, ax = plt.subplots()
    sns.boxplot(data=df_filtrado, x="Post_Level", y="Work_Life_balance", ax=ax)
    st.pyplot(fig)
