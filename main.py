import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from funciones.produc import j, j_darcy, q_darcy, aof, Qb, qo_darcy, IPR_curve_methods

# Ruta al archivo Excel
file_path = "Data/Volve production data.xlsx"

# Lista de pozos
wells = [
    "15_9-F-1 C",
    "15_9-F-11",
    "15_9-F-12",
    "15_9-F-14",
    "15_9-F-15 D",
    "15_9-F-4",
    "15_9-F-5",
]

# Título de la aplicación
st.set_page_config(page_title="Oil & Gas Company", page_icon="\U0001f702")

# Agregar el logo
logo_path = "Data/logo.jpg"
st.sidebar.image(logo_path, use_container_width=True)

st.sidebar.markdown("<h2 style='text-align: center;'>Menú</h2>", unsafe_allow_html=True)

# Menú lateral con iconos
menu = st.sidebar.radio(
    "",
    [
        "Inicio \U0001f3e0",
        "Visualización de Producción 📊",
        "Potencial de produccion\U0001f4a7",
        "Análisis nodal para flujo monofásico \u2699\ufe0f",
    ]
)

if menu == "Inicio \U0001f3e0":
    # Mostrar el logo en el centro
    st.image(logo_path, use_column_width=True)

    # Descripción de la aplicación
    st.title("Bienvenidos a la aplicación Oil & Gas")
    st.write(""" 
    Esta aplicación está diseñada para optimizar el análisis de datos de producción y realizar cálculos avanzados en ingeniería de petróleo. 

    funcionalidades:

    - Visualización de datos de producción de pozos.
    - Cálculo del índice de productividad (J) y caudales (Q).
    - Estimación del flujo absoluto abierto (AOF).
    - Análisis nodal para flujo monofásico.

    """)

    # Mostrar una foto de los fundadores debajo
    founders_image_path = "Data/fundadores.jpg"  # Ruta a la foto de los fundadores
    st.subheader("Fundadores")
    st.image(founders_image_path, caption="Equipo fundador de la aplicación: Jean Pierre Mendia y Joel Alcivar",
             use_column_width=True)

elif menu == "Visualización de Producción 📊":
    st.title("Visualización de Produccion")
    try:
        excel_data = pd.ExcelFile(file_path)
        sheet_name = "Monthly Production Data"
        df = excel_data.parse(sheet_name)

        selected_columns = ['Wellbore name', 'Year', 'Month', 'Oil', 'Water']
        extracted_data = df[selected_columns]

        wells_data = {pozo: data for pozo, data in extracted_data.groupby('Wellbore name')}

        pozo_seleccionado = st.selectbox("Selecciona un pozo:", list(wells_data.keys()))

        data_seleccionada = wells_data[pozo_seleccionado]
        annual_data = data_seleccionada.groupby('Year').agg({'Oil': 'sum', 'Water': 'sum'}).reset_index()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(annual_data['Year'], annual_data['Oil'], label='Oil', marker='o')
        ax.plot(annual_data['Year'], annual_data['Water'], label='Water', marker='s')

        ax.set_title(f"Producción del pozo {pozo_seleccionado} por Año")
        ax.set_xlabel('Año')
        ax.set_ylabel('Producción total (bbl/año o m3/año)')
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")

elif menu == "Análisis nodal para flujo monofásico \u2699\ufe0f":
    st.header("Cálculo del Índice de Productividad Darcy (J)")

    ko = st.number_input("Permeabilidad del reservorio (ko) [mD]", min_value=0.0)
    h = st.number_input("Espesor del reservorio (h) [ft]", min_value=0.0)
    bo = st.number_input("Factor de formación de petróleo (bo) [bbl/stb]", min_value=0.0)
    uo = st.number_input("Viscosidad del petróleo (uo) [cp]", min_value=0.0)
    re = st.number_input("Radio externo del reservorio (re) [ft]", min_value=0.0)
    rw = st.number_input("Radio del pozo (rw) [ft]", min_value=0.0)
    s = st.number_input("Factor de skin (s)", min_value=0.0)

    flow_regime = st.selectbox("Selecciona el régimen de flujo:", ["seudocontinuo", "continuo"])

    if st.button("Calcular J Darcy"):
        J_value = j_darcy(ko, h, bo, uo, re, rw, s, flow_regime)
        st.write(f"El índice de productividad Darcy (J) es: {J_value:.2f} [bbl/stb/psi]")

    st.header("Cálculo del Caudal Darcy (Q)")

    pr = st.number_input("Presión de reservorio (pr) [psi]", min_value=0.0)
    pwf = st.number_input("Presión de fondo del pozo (pwf) [psi]", min_value=0.0)

    if st.button("Calcular Q Darcy"):
        Q_value = q_darcy(ko, h, pr, pwf, s, uo, bo, re, rw, flow_regime)
        st.write(f"El caudal Darcy (Q) es: {Q_value:.2f} [bbl/día]")

elif menu == "Potencial de produccion\U0001f4a7":
    st.title("Potencial de Producción")

    st.write("Ingresa los parámetros necesarios para calcular el potencial de producción:")

    # Entrada de parámetros comunes
    q_test = st.number_input("Caudal de prueba (bpd)", value=500.0)
    pwf_test = st.number_input("Presión de fondo fluyente durante la prueba (psia)", value=3000.0)
    pr = st.number_input("Presión inicial del yacimiento (psia)", value=4000.0)
    pb = st.number_input("Presión de burbuja (psia)", value=2500.0)
    ef = st.number_input("Factor de eficiencia (ef)", value=1.0)
    ef2 = st.number_input("Segundo factor de eficiencia (ef2)", value=None)

    metodo = st.selectbox("Método para cálculo de Qo", ["Darcy", "Vogel", "Standing", "IPR_compuesto"])

    # Calcular el índice de productividad J
    if st.button("Calcular J"):
        try:
            J_value = j(q_test, pwf_test, pr, pb)
            st.write(f"El índice de productividad (J) es: {J_value:.4f} stb/d/psi")
        except Exception as e:
            st.error(f"Error en el cálculo de J: {e}")

    # Calcular el AOF y Qb
    if st.button("Calcular AOF y Qb"):
        try:
            AOF_value = aof(q_test, pwf_test, pr, pb)
            Qb_value = Qb(q_test, pwf_test, pr, pb)
            st.write(f"El flujo absoluto abierto (AOF) es: {AOF_value:.2f} bpd")
            st.write(f"El flujo a la presión de burbuja (Qb) es: {Qb_value:.2f} bpd")
        except Exception as e:
            st.error(f"Error en el cálculo de AOF o Qb: {e}")

    # Ingresar valores de Pwf para calcular Qo y mostrar la curva IPR
    st.subheader("Cálculo de Qo y Curva IPR")
    num_pwf = st.slider("Selecciona cuántos valores de Pwf usar (máximo 5):", min_value=1, max_value=5, value=3)

    pwf_values = []
    for i in range(num_pwf):
        pwf_input = st.number_input(f"Ingresa el valor de Pwf #{i + 1} (psia):", min_value=0.0, max_value=pr,
                                    key=f"pwf_{i}")
        pwf_values.append(pwf_input)

    if st.button("Calcular Qo y generar curva IPR"):
        try:
            qo_values = []
            for pwf in pwf_values:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb)
                qo_values.append(qo)
                st.write(f"Para Pwf = {pwf:.2f} psia, Qo = {qo:.2f} bpd")

            # Generar la curva IPR
            st.subheader("Curva IPR")
            IPR_curve_methods(q_test, pwf_test, pr, np.array(pwf_values), pb, method=metodo)
            st.pyplot(plt.gcf())  # Mostrar el gráfico actual

        except Exception as e:
            st.error(f"Error en el cálculo de Qo o en la generación de la curva IPR: {e}")

# Generar archivo requirements.txt
with open('requirements.txt', 'w') as f:
    f.write("streamlit\n")
    f.write("pandas\n")
    f.write("plotly\n")
    f.write("Pillow\n")
    f.write("numpy\n")
    f.write("matplotlib\n")