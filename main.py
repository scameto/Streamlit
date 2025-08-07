import streamlit as st




# pg = st.navigation(
#     [
#     # st.Page("pages/page1.py", title = "Movies", icon = "📽️"), 
#     # st.Page("pages/page2.py", title = "Employees", icon = "📊"),
#     # st.Page("pages/model.py", title = "ML Model", icon = "🤖"),
#     st.Page("pages/inicio.py", title = "Inicio", icon = "🏠"),
#     st.Page("pages/costos.py", title = "Costos", icon = "📊"),
#     st.Page("pages/reporte_cosecha.py", title = "Cosecha", icon = "🚜"),
#     st.Page("pages/produccion_cultivo.py", title = "Producción por Cultivo", icon = "🌾"),
#     st.Page("pages/analisis_economico.py", title = "Análisis Económico", icon = "💰"),


#     ]
#     #https://symbl.cc/en/collections/     iconos
# )
# pg.run()



st.set_page_config(
    page_title="SGAgro App",
    page_icon="🌱",
    layout="wide"
)

st.title("Bienvenido a SGAgro App 🌱")
st.markdown("Seleccioná una sección desde el menú lateral.")

