import streamlit as st
import pandas as pd
import sqlite3
import folium
from streamlit_folium import st_folium 
import plotly.graph_objects as go
# Autor: Marcos D. Ibarra 
# Github: https://github.com/MRCSIBR


# Cargar los datos
df_vial = pd.read_csv('data/df_vial.csv')

def create_map():
    """ Funcion: create_map: Usa la libreria Folium para mostrar mapa """
    
    st.title("Mapa de Accidentes / CABA")
    
    # Para centrar el mapa uso el metodo .sample
    map_center = [df_vial.sample()['LATITUD'].values[0], df_vial.sample()['LONGITUD'].values[0]]
    m = folium.Map(location=map_center, zoom_start=14)

    # Marcador rojo para cada accidente
    for index, row in df_vial.iterrows():
        lat = row['LATITUD']
        lon = row['LONGITUD']
        dirnorm = row['DIRNORM']
        n_victimas = row['N_VICTIMAS']
        tooltip = f"DIRNORM: {dirnorm}<br>N_VICTIMAS: {n_victimas}"
        folium.Marker([lat, lon], icon=folium.Icon(color='red'), tooltip=tooltip).add_to(m)

    # Mostrar el mapa: https://folium.streamlit.app/static_map
    st_folium(m, width=1000, height=700, returned_objects=[])
    
def main():
    
    st.sidebar.title("Data Analisis / P.I. #2")
    st.sidebar.subheader("Autor: Marcos D. Ibarra")
    
    st.sidebar.write("Este proyecto es mi solucion a las consignas propuestas en: https://github.com/soyHenry/PI_DA/")
    st.sidebar.subheader("Navegacion")
    
    page = st.sidebar.selectbox("Elegir pagina", ["Data", "Mapa_CABA", "Consultas_SQL"])

    if page == "Mapa_CABA":
        
        create_map()
    
    elif page == "Data":
        
        # ---------------------------------
        # Titulo y parrafo de introduccion
        
        st.title("Data Analytics")
        st.subheader("Proyecto Individual N.2 / Data Science")

        st.write("Mi rol como data analyst es encontrar indicios o patrones en los datos que luego sirvan para la toma de decisiones.")
        st.write("En este caso el dataset a estudiar incluye información de accidentes viales en la zona de la ***Ciudad Autónoma de Buenos Aires CABA*** ocurridos entre 2016 y 2021.")
        st.write("Las conclusiones de este análisis podrán servir para mejorar la seguridad vial en esa área.")
        st.write("Fuente de datos: https://data.buenosaires.gob.ar/dataset/victimas-siniestros-viales")
        st.write(df_vial.head())

        # Visualizar graficos
        import plotly.express as px
        # Data Analysis
        st.header("Visualizar datos")

        
        # -------------------
        # Grafico Porcentajes
        
        st.subheader("Porcentajes de Víctimas por Categoría")

        import plotly.graph_objects as go

        # Agrupa los datos por la columna 'VICTIMA' y suma el número de víctimas en cada categoría
        data_grouped = df_vial.groupby('VICTIMA')['N_VICTIMAS'].sum().reset_index()

        # Ordenar los datos por el número de víctimas de forma descendente
        data_grouped.sort_values('N_VICTIMAS', ascending=False, inplace=True)

        # Obtener los 4 valores más importantes y el resto
        top_4 = data_grouped.head(4)
        rest = data_grouped.iloc[4:]

        # Crear el gráfico de torta para los 4 valores más importantes
        fig1 = go.Figure(data=[go.Pie(labels=top_4['VICTIMA'], values=top_4['N_VICTIMAS'])])
        fig1.update_layout(title='Víctimas por Categoría (Top 4)')

        # Crear el gráfico de torta para el resto de valores
        fig2 = go.Figure(data=[go.Pie(labels=rest['VICTIMA'], values=rest['N_VICTIMAS'])])
        fig2.update_layout(title='Víctimas por Categoría (Resto)')

        # Mostrar los gráficos
        #fig1.show()
        #fig2.show()
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)
        
        st.markdown("#### OBSERVACIÓN: / Tarta de Porcentajes:")

        st.write("La gran mayoria de los accidentes fatales son de motociclistas en primer lugar y luego peatones.") 
        
        #----------------
        # Indicadores KPI
        

        # KPI 1: Analizar la distribucion mensual de accidentes 
        st.subheader("KPI 1: Distribucion mensual de accidentes.")

        # Convert the 'FECHA' column to datetime format
        df_vial['FECHA'] = pd.to_datetime(df_vial['FECHA'])

        # Extract the month from the 'FECHA' column and create a new column 'MONTH'
        df_vial['MES'] = df_vial['FECHA'].dt.month

        # Group the data by 'MONTH' and calculate the total number of accidents in each month
        monthly_accidents = df_vial.groupby('MES')['N_VICTIMAS'].sum().reset_index()

        # Plot the trend of monthly accidents
        fig = px.line(monthly_accidents, x='MES', y='N_VICTIMAS', title='Tendencia de accidentes por Mes')
        fig.update_xaxes(title='Mes')
        fig.update_yaxes(title='Numero Accidentes')

        # Show the plot
        st.plotly_chart(fig)

        st.markdown("#### OBSERVACIÓN: / Tendencia de accidentes por mes:")

        st.write("Hay una aumento de accidentes entre el mes ***octubre y diciembre***, relacionado quizas con las fiestas de navidad y año nuevo.") 


        # KPI 2: Tendencia diaria de Accidentes
        st.subheader("KPI 2: Distribución de accidentes por dia de la semana.")

        # Convert the 'FECHA' column to datetime format
        df_vial['FECHA'] = pd.to_datetime(df_vial['FECHA'])

        # Extract the day of the week from the 'FECHA' column and create a new column 'DAY_OF_WEEK'
        df_vial['DAY_OF_WEEK'] = df_vial['FECHA'].dt.dayofweek

        # Map the day of the week values to their respective names
        day_names = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
        df_vial['DAY_OF_WEEK'] = df_vial['DAY_OF_WEEK'].map(lambda x: day_names[x])

        # Group the data by 'DAY_OF_WEEK' and calculate the total number of accidents on each day
        daily_accidents = df_vial.groupby('DAY_OF_WEEK')['N_VICTIMAS'].sum().reset_index()

        # Plotear la distribucion
        fig = px.histogram(daily_accidents, x='DAY_OF_WEEK', y='N_VICTIMAS', title='Distribucion de accidentes por dia de la semana')
        fig.update_xaxes(title='Dias de la semana')
        fig.update_yaxes(title='Numero de Accidentes')

        # Mostrar el plot
        st.plotly_chart(fig)

        st.markdown("#### OBSERVACIÓN: / Tendencia diaria: ")
        st.markdown("Buscando un patron en la distribucion de accidentes por dia podemos notar que: ")
        st.write("***Los dias con mas accidentes son sabado, domingo y lunes, pero no hay una diferencia significativa con el resto de la semana.***")

        # Accidentes año por año
        # Calcular el numero total de victimas en CABA
        st.subheader("TOTAL de victimas anuales")
        yearly_accidents = df_vial.groupby('AAAA')['N_VICTIMAS'].sum().reset_index()

        
        fig = px.bar(yearly_accidents, x='AAAA', y='N_VICTIMAS', color='N_VICTIMAS', color_discrete_sequence=['red'], title='Numero Total de Accidentes en CABA Año por Año')
        fig.update_xaxes(title='Año')
        fig.update_yaxes(title='Numero de Accidentes')

        # Mostrar el plot
        st.plotly_chart(fig)

        st.markdown("#### OBSERVACIÓN: / Tendencia año por año:")

        st.write("Entre 2019 y 2020 el numero de accidentes baja considerablemente, debido a las restricciones implementadas en el marco de la cuarentena.")
    
    
    elif page == "Consultas_SQL":
        
        # Conectar a SQL
        conn = sqlite3.connect("data/accidentes.db")
        cursor = conn.cursor()

        
        st.title("Consultas SQL")
        st.write("Podemos consultar la base de datos:")

        # Consulta para el total de accidentes
        st.header("1. Total de Accidentes")
        total_accidents_query = cursor.execute("SELECT COUNT(*) FROM accidents")
        total_accidents = total_accidents_query.fetchone()[0]
        st.write(f"Total accidents: {total_accidents}")

        # Consulta para accidentes en una fecha especifica
        st.header("2. Accidentes en una fecha especifica")
        specific_date = st.text_input("Ingrese una fecha especifica (ej. 2021-09-12):")
        if specific_date:
            specific_date_query = cursor.execute("SELECT * FROM accidents WHERE FECHA = ?", (specific_date,))
            specific_date_accidents = specific_date_query.fetchall()
            st.write(f"Accidents on {specific_date}:")
            st.write(specific_date_accidents)

        # Consulta para accidentes de Motocicleta
        st.header("3 . Accidentes de 'MOTO'")
        moto_accidents_query = cursor.execute("SELECT * FROM accidents WHERE VICTIMA = 'MOTO'")
        moto_accidents = moto_accidents_query.fetchall()
        st.write("Accidents involving 'MOTO' victims:")
        st.write(moto_accidents)
        
        
        # Cerrar la conexion
        conn.close()


if __name__ == "__main__":
    main()
