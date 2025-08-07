import streamlit as st

st.set_page_config(page_title="Inicio - Panel Agrícola", layout="wide")

st.image("data/sgagro.jpg", width=500)

st.markdown("""
# 🌱 **Bienvenido a Sistema de Gestión y Análisis Agrícola** 


---

### 🔍 ¿Qué podés hacer desde aquí?
## - **📊 Costos por Cultivo**          
### Explorá en detalle los costos por insumo, labor y tipo.


## - **🚜 Reporte de Cosecha y Mermas**  
### Analizá el flujo de cosecha y las pérdidas por destino.
            
## - **🌾 Producción por Cultivo**
###     Visualizá rindes, superficie y toneladas producidas por lote.

## - **💰 Análisis Económico por Especie**  
###Calculá márgenes netos considerando precios, fletes y arrendamientos.



---

👉 Elegí una sección desde el menú lateral para comenzar.
""")