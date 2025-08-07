import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")

st.title("Movies")
st.header('My first movies app')

@st.cache_data(show_spinner=True, ttl=3600*24)
def load_movies(rows=1000):
    movies = pd.read_csv('data/movies.csv', encoding='latin-1', nrows=rows)
    return movies

# Cargar los datos de las películas
movies = load_movies()

st.sidebar.markdown('# Filtros')

# director = st.text_input('Director', 'Enter a director name') # Esta linea permite un solo director

director = st.sidebar.multiselect('Director', options=sorted(movies['director'].unique())) # Esta linea permite seleccionar varios directores

# year = st.number_input('Year', min_value=1900, max_value=2023, value=2023) # para un solo año
year = st.sidebar.slider('Year', min_value=movies['year'].min(), max_value=movies['year'].max(), value=(movies['year'].min(), movies['year'].max()), step=1) # para un rango de años

genre = st.sidebar.multiselect('Genre', options=sorted(movies['genre'].unique())) # Permite seleccionar varios géneros

if director:
    #st.subheader(f'Movies directed by {director}')
    # movies = movies[movies['director'].str.contains(director, case=False, na=False)] # Esta linea es para un solo director
    movies = movies[movies['director'].isin(director)] # Esta linea busca dentro de la lista de directores

if genre:
    #st.subheader(f'Movies of genre {genre}')
    movies = movies[movies['genre'].isin(genre)] # Esta linea busca dentro de la lista de géneros

if year:
    movies = movies[(movies['year'] >= year[0]) & (movies['year'] <= year[1])]


tab_movies_plt, tab_movies_sns, tab_data = st.tabs(['Matplotlib', 'Seaborn', 'Data'])


with tab_data:
    st.dataframe(movies[['name','director','genre','year']], hide_index=True)

    with st.expander("Show total movies"):
        st.write(f"Total movies: **{len(movies)}**")

with tab_movies_plt:
    with st.container():
        col_histogram, col_bar, col_scatter = st.columns(3, gap='small', vertical_alignment='top')

        with col_histogram:
            with st.container(border=True):
                fig, ax = plt.subplots() 
                fig.set_figheight(3)
                ax.hist(movies['year']) 
                st.subheader("Histograma de películas por año") 
                st.pyplot(fig) 

        with col_bar:
            with st.container(border=True):
                if movies['director'].nunique() < 10:
                    fig, ax = plt.subplots() 
                    fig.set_figheight(4)
                    x_pos = movies['director'].value_counts().values
                    y_pos = movies['director'].value_counts().index
                    ax.barh(y_pos, x_pos) 
                    st.subheader("Grafica de Barras") 
                    st.pyplot(fig) 
                else:
                    st.subheader("Grafica de Barras") 
                    st.error("No se puede mostrar la gráfica de barras porque hay demasiados directores.")

        with col_scatter:
            with st.container(border=True):
                # Grafica con matplotlib
                fig, ax = plt.subplots()
                fig.set_figheight(3)
                ax.scatter(movies['rating'], movies['gross'])
                ax.set_xlabel("Rating")
                ax.set_ylabel("Gross Earnings")
                ax.set_xticklabels(movies['rating'], rotation=45)
                st.subheader("Grafica de Dispersión")
                st.pyplot(fig)


with tab_movies_sns:
    seaborn1, seaborn2 = st.columns(2)

    with seaborn1:
        # Grafica con seaborn
        plot = sns.scatterplot(data=movies, x='rating', y='gross', hue='genre', size='year', alpha=0.6, legend=None)
        st.pyplot(plot.get_figure())

    with seaborn2:
        # Grafica de barras con seaborn
        if movies['director'].nunique() < 10:
            plot = sns.barplot(data=movies, x='director', y='rating', ci=None)
            plot.set_xticklabels(plot.get_xticklabels(), rotation=45)
            st.pyplot(plot.get_figure())
        else:
            st.error("No se puede mostrar la gráfica de barras porque hay demasiados directores.")
        
