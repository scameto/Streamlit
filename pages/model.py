import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class MlModel:
    """
    Simulación de un modelo de aprendizaje de regresión lineal simple.
    """
    def fit(self, X, y):
        pass

    def predict(self, X):
        b = sum(X)/len(X)  # Simulación de un modelo simple
        return b + X[0] * 0.1 + X[1] * 0.2

regresor = MlModel()

with st.form("model_form"):
    st.write("### Ingresos y Puntuación")
    gross = st.number_input("Gross Income", value=1000, step=100)
    score = st.number_input("Score", value=500, step=50)

    submitted = st.form_submit_button("Predecir Ingresos")
    if submitted:
        # Simulación de entrenamiento del modelo
        prediccion = regresor.predict([gross, score])
        st.write("El modelo predice que el ingreso será de:", prediccion)