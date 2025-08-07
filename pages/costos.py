import streamlit as st
import pandas as pd
import uuid

import plotly.express as px

st.set_page_config(page_title="Costos por Cultivo en USD/ha", layout="wide")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("data/InformeOtRealizadas_al_2025-07-18.xlsx", sheet_name="Worksheet")
    df.columns = df.columns.str.strip()
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    df["Superficie"] = pd.to_numeric(df["Superficie"], errors="coerce")
    df["Precio"] = pd.to_numeric(df["Precio"], errors="coerce")
    df["USD_ha"] = df["Total"] / df["Superficie"]
    df["Cultivo"] = df["Cultivo"].astype(str)
    return df

df = cargar_datos()

@st.cache_data
def cargar_presupuesto():
    # Fixed: Specify the correct sheet name "Hoja1" where the data is located
    df = pd.read_excel("data/CultivosPresupuestados.xlsx", sheet_name="Hoja1", index_col=None)
    df.columns = df.columns.str.strip()
    df["Total"] = pd.to_numeric(df["TotalUSD"], errors="coerce")
    df["USD_presupuestado"] = df["TotalUSD"]
    df["Cultivo"] = df["Cultivo"].astype(str)
    df["Tipo Insumo"] = df["TipoInsumo"].astype(str)
    df["Especie"] = df["Especie"].astype(str)  # Aseguramos que Especie sea string
    return df

# Removed the debugging line that was causing issues
df_presupuesto = cargar_presupuesto()

# Sidebar: filtros
st.sidebar.header("🎛️ Filtros")
empresas = st.sidebar.multiselect("Empresa", df["Empresa"].unique(), default=df["Empresa"].unique())
especies = st.sidebar.multiselect("Especie", df["Especie"].unique(), default=df["Especie"].unique())

df_filtrado = df[
    (df["Empresa"].isin(empresas)) &
    (df["Especie"].isin(especies))
]

campos = st.sidebar.multiselect("Campo", df_filtrado["Campo"].unique(), default=df_filtrado["Campo"].unique())
df_filtrado = df_filtrado[df_filtrado["Campo"].isin(campos)]

cultivos = st.sidebar.multiselect("Cultivo", df_filtrado["Cultivo"].unique(), default=df_filtrado["Cultivo"].unique())
df_filtrado = df_filtrado[df_filtrado["Cultivo"].isin(cultivos)]

# Tabs
tab1, tab2, tab3 = st.tabs([
    "📄 Informe por Cultivo",
    "📊 Comparación por Tipo Insumo",
    "📉 Presupuesto vs Ejecutado"
])

# TAB 1
with tab1:
    st.title("🌱 Costos por Cultivo (USD/ha)")

    if df_filtrado.empty:
        st.warning("No hay datos para los filtros seleccionados.")
    else:
        resumen = []

        for cultivo, grupo in df_filtrado.groupby("Cultivo"):
            superficie = grupo["Superficie"].dropna().iloc[0] if grupo["Superficie"].notna().any() else None
            if superficie and superficie > 0:
                total = grupo["Total"].sum()
                usd_ha = total / superficie
                resumen.append({
                    "Cultivo": cultivo,
                    "Superficie (ha)": superficie,
                    "Costo Total (USD)": total,
                    "Costo USD/ha": usd_ha
                })

                st.subheader(f"🌾 {cultivo}")
                st.dataframe(grupo[["Labor / Insumo", "Tipo Insumo", "Cantidad Ejecutada", "Precio", "Total", "USD_ha"]],
                             use_container_width=True)

                st.markdown("##### Costo por insumo (USD/ha)")

                # Calcular USD/ha por insumo según criterio correcto (total / superficie del cultivo)
                resumen_insumo = (
                    grupo.groupby("Labor / Insumo")["Total"]
                    .sum()
                    .reset_index()
                )
                resumen_insumo["USD_ha"] = resumen_insumo["Total"] / superficie
                plot_data = resumen_insumo[["Labor / Insumo", "USD_ha"]].sort_values("USD_ha", ascending=False)

                # Mostrar los 15 principales y agrupar el resto en "Otros"
                top_n = 15
                if len(plot_data) > top_n:
                    top_data = plot_data.iloc[:top_n].copy()
                    otros_total = plot_data.iloc[top_n:]["USD_ha"].sum()
                    otros_fila = pd.DataFrame([{"Labor / Insumo": "Otros", "USD_ha": otros_total}])
                    plot_data = pd.concat([top_data, otros_fila], ignore_index=True)

                # Ordenar para mejor visualización
                plot_data = plot_data.sort_values("USD_ha", ascending=True)

                fig = px.bar(
                    plot_data,
                    x="Labor / Insumo",
                    y="USD_ha",
                    orientation="v",
                    text_auto=".2f",
                    title=f"Costo por insumo (USD/ha) - {cultivo}"
                )
                fig.update_layout(xaxis_title="Insumo", yaxis_title="USD/ha")
                st.plotly_chart(fig, use_container_width=True)

        # Resumen general
        st.markdown("## 📋 Comparativa entre cultivos")
        resumen_df = pd.DataFrame(resumen)
        st.dataframe(resumen_df, use_container_width=True)

        st.markdown("### 📊 Gráfico de costos por cultivo (USD/ha)")
        fig = px.bar(
            resumen_df.sort_values("Costo USD/ha"),
            x="Costo USD/ha",
            y="Cultivo",
            orientation="h",
            text_auto=".2f",
            color_discrete_sequence=["green"]
        )
        fig.update_layout(xaxis_title="USD/ha", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

# TAB 2
with tab2:
    st.title("📊 Comparación de Costos por Tipo de Insumo")

    if df_filtrado.empty:
        st.warning("No hay datos para mostrar.")
    else:
        df_agrupado = []
        for cultivo, grupo in df_filtrado.groupby("Cultivo"):
            superficie = grupo["Superficie"].dropna().iloc[0] if grupo["Superficie"].notna().any() else None
            if superficie and superficie > 0:
                resumen_tipo = grupo.groupby("Tipo Insumo")["Total"].sum() / superficie
                for tipo, usd_ha in resumen_tipo.items():
                    df_agrupado.append({
                        "Cultivo": cultivo,
                        "Tipo Insumo": tipo,
                        "USD/ha": usd_ha
                    })

        df_tipo_insumo = pd.DataFrame(df_agrupado)
        st.dataframe(df_tipo_insumo, use_container_width=True)

        fig = px.bar(
            df_tipo_insumo,
            x="Cultivo",
            y="USD/ha",
            color="Tipo Insumo",
            title="Costos por tipo de insumo en cultivos seleccionados",
            text_auto=".2f",
            hover_data=["USD/ha"]
        )
        fig.update_layout(barmode='stack', xaxis_title="Cultivo", yaxis_title="USD/ha")
        st.plotly_chart(fig, use_container_width=True)

# TAB 3
with tab3:
    # st.title("📉 Comparativa Presupuesto vs Ejecutado por Especie")
    # if df_filtrado.empty:
    #     st.warning("No hay datos para mostrar.")
    # else:
    #     comparativo = []

    #       # Homogeneizar nombres para merge
    #     df_presupuesto["Tipo Insumo"] = df_presupuesto["Tipo Insumo"].str.strip().str.lower()
    #     df_filtrado["Tipo Insumo"] = df_filtrado["Tipo Insumo"].str.strip().str.lower()


    #     for especie, grupo in df_filtrado.groupby("Especie"):
    #         # Para cada cultivo dentro de la especie, calcular USD/ha
    #         ejecutado_por_cultivo = []
            
    #         for cultivo, subgrupo in grupo.groupby("Cultivo"):
    #             superficie_cultivo = subgrupo["Superficie"].dropna().iloc[0] if subgrupo["Superficie"].notna().any() else None
    #             if superficie_cultivo and superficie_cultivo > 0:
    #                 # Calcular USD/ha por tipo de insumo para este cultivo específico
    #                 usd_ha_por_insumo = subgrupo.groupby("Tipo Insumo")["Total"].sum() / superficie_cultivo
    #                 ejecutado_por_cultivo.append(usd_ha_por_insumo)
            
    #         if ejecutado_por_cultivo:
    #             # Promediar los USD/ha entre todos los cultivos de la especie
    #             ejecutado_promedio = pd.concat(ejecutado_por_cultivo, axis=1).mean(axis=1)
    #             ejecutado_df = ejecutado_promedio.reset_index()
    #             ejecutado_df.columns = ["Tipo Insumo", "USD_ejecutado"]
    #             ejecutado_df["Especie"] = especie

    #             # Obtener datos de presupuesto para esta especie
    #             presup = df_presupuesto[df_presupuesto["Especie"] == especie].copy()
                
    #             # Agrupar presupuesto por tipo de insumo (promediando si hay múltiples registros)
    #             presup_agrupado = presup.groupby("Tipo Insumo")["USD_presupuestado"].sum().reset_index()

    #             # Hacer merge entre ejecutado y presupuestado
    #             comparado = pd.merge(ejecutado_df, presup_agrupado, on="Tipo Insumo", how="outer")
    #             comparado["Especie"] = especie
    #             comparado = comparado.fillna(0)

    #             comparado["Diferencia"] = comparado["USD_ejecutado"] - comparado["USD_presupuestado"]
    #             comparado["% Ejecutado"] = comparado.apply(
    #                 lambda row: (row["USD_ejecutado"] / row["USD_presupuestado"] * 100) if row["USD_presupuestado"] > 0 else 0,
    #                 axis=1
    #             ).round(1)

    #             comparativo.append(comparado)

    #         if comparativo:
    #             df_comparativo = pd.concat(comparativo, ignore_index=True)
    #             st.dataframe(df_comparativo, use_container_width=True)

    #             especies_disponibles = df_comparativo["Especie"].unique()
    #             especie_sel = st.selectbox("Seleccionar Especie", especies_disponibles)

    #             df_especie = df_comparativo[df_comparativo["Especie"] == especie_sel]

    #             if not df_especie.empty:
    #                 fig = px.bar(
    #                     df_especie.melt(id_vars="Tipo Insumo", value_vars=["USD_presupuestado", "USD_ejecutado"],
    #                                     var_name="Tipo", value_name="USD/ha"),
    #                     x="Tipo Insumo",
    #                     y="USD/ha",
    #                     color="Tipo",
    #                     barmode="group",
    #                     title=f"Presupuesto vs Ejecutado - {especie_sel}",
    #                     text_auto=".2f"
    #                 )
    #                 fig.update_layout(xaxis_title="Tipo Insumo", yaxis_title="USD/ha")
    #                 st.plotly_chart(fig, use_container_width=True, key=f"chart_{especie_sel}")
    #             else:
    #                 st.warning(f"No hay datos disponibles para la especie {especie_sel}")
    #         else:
    #             st.warning("No hay datos para mostrar en la comparativa.")
    #     else:
    #         st.warning("No hay datos de comparación disponibles.")

    
    st.title("📉 Comparativa Presupuesto vs Ejecutado por Especie")
    if df_filtrado.empty:
        st.warning("No hay datos para mostrar.")
    else:
        comparativo = []

        # Homogeneizar nombres para merge
        df_presupuesto["Tipo Insumo"] = df_presupuesto["Tipo Insumo"].str.strip().str.lower()
        df_filtrado["Tipo Insumo"] = df_filtrado["Tipo Insumo"].str.strip().str.lower()

        for especie, grupo in df_filtrado.groupby("Especie"):
            ejecutado_por_cultivo = []
            for cultivo, subgrupo in grupo.groupby("Cultivo"):
                superficie_cultivo = subgrupo["Superficie"].dropna().iloc[0] if subgrupo["Superficie"].notna().any() else None
                if superficie_cultivo and superficie_cultivo > 0:
                    usd_ha_por_insumo = subgrupo.groupby("Tipo Insumo")["Total"].sum() / superficie_cultivo
                    ejecutado_por_cultivo.append(usd_ha_por_insumo)

            if ejecutado_por_cultivo:
                ejecutado_promedio = pd.concat(ejecutado_por_cultivo, axis=1).mean(axis=1)
                ejecutado_df = ejecutado_promedio.reset_index()
                ejecutado_df.columns = ["Tipo Insumo", "USD_ejecutado"]
                ejecutado_df["Especie"] = especie

                presup = df_presupuesto[df_presupuesto["Especie"] == especie].copy()
                presup_agrupado = presup.groupby("Tipo Insumo")["USD_presupuestado"].sum().reset_index()

                comparado = pd.merge(ejecutado_df, presup_agrupado, on="Tipo Insumo", how="outer")
                comparado["Especie"] = especie
                comparado = comparado.fillna(0)
                comparado["Diferencia"] = comparado["USD_ejecutado"] - comparado["USD_presupuestado"]
                comparado["% Ejecutado"] = comparado.apply(
                    lambda row: (row["USD_ejecutado"] / row["USD_presupuestado"] * 100) if row["USD_presupuestado"] > 0 else 0,
                    axis=1
                ).round(1)

                comparativo.append(comparado)

        if comparativo:
            df_comparativo = pd.concat(comparativo, ignore_index=True)
            st.dataframe(df_comparativo, use_container_width=True)

            especies_disponibles = df_comparativo["Especie"].unique()
            especie_sel = st.selectbox("Seleccionar Especie", especies_disponibles)

            df_especie = df_comparativo[df_comparativo["Especie"] == especie_sel]

            if not df_especie.empty:
                fig = px.bar(
                    df_especie.melt(id_vars="Tipo Insumo", value_vars=["USD_presupuestado", "USD_ejecutado"],
                                    var_name="Tipo", value_name="USD/ha"),
                    x="Tipo Insumo",
                    y="USD/ha",
                    color="Tipo",
                    barmode="group",
                    title=f"Presupuesto vs Ejecutado - {especie_sel}",
                    text_auto=".2f"
                )
                fig.update_layout(xaxis_title="Tipo Insumo", yaxis_title="USD/ha")
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{especie_sel}_{uuid.uuid4()}")
            else:
                st.warning(f"No hay datos disponibles para la especie {especie_sel}")
        else:
            st.warning("No hay datos de comparación disponibles.")
