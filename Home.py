import pandas as pd
import folium
from folium import Marker
import os
from folium.plugins import HeatMap
from plotly import express as px
import kagglehub
import streamlit as st
from streamlit_folium import st_folium
import numpy as np

data_path = kagglehub.dataset_download("rusiano/madrid-airbnb-data")

def load_data():
    return pd.read_csv(os.path.join(data_path, 'listings_clean.csv'))

def plot_scatter(df, x, y, color, hover_data, labels, title):
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        hover_data=hover_data,
        labels=labels,
        title=title
    )
    fig.update_traces(marker=dict(size=8, opacity=0.7), selector=dict(mode='markers'))
    fig.update_layout(
        legend_title_text=color,
        xaxis=dict(title=labels[x]),
        yaxis=dict(title=labels[y]),
        height=600,
        width=800
    )
    return fig

def plot_bar(df, x, y, color, title, labels):
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        labels=labels
    )
    return fig

def plot_box(df, x, y, color, title):
    fig = px.box(
        df,
        x=x,
        y=y,
        color=color,
        title=title,
        points='all'
    )
    fig.update_yaxes(title='Logaritmo del Precio')
    fig.update_layout(
        legend_title_text=color,
        xaxis=dict(title=x)
    )
    return fig

tourist_spots = [
    {"name": "Museo Reina Sofía", "lat": 40.408735, "lon": -3.694137},
    {"name": "Plaza Mayor", "lat": 40.415365, "lon": -3.707398},
    {"name": "Puerta del Sol", "lat": 40.416775, "lon": -3.703790},
    {"name": "Palacio Real", "lat": 40.417994, "lon": -3.714344},
    {"name": "Museo del Prado", "lat": 40.413782, "lon": -3.692127},
    {"name": "Parque del Retiro", "lat": 40.415260, "lon": -3.684416},
    {"name": "Gran Vía", "lat": 40.420347, "lon": -3.705774},
    {"name": "Templo de Debod", "lat": 40.424021, "lon": -3.717570},
    {"name": "Santiago Bernabéu", "lat": 40.453054, "lon": -3.688344},
    {"name": "Plaza de Cibeles", "lat": 40.419722, "lon": -3.693333},
    {"name": "Mercado de San Miguel", "lat": 40.415363, "lon": -3.708416},
    {"name": "Catedral de la Almudena", "lat": 40.415364, "lon": -3.714451},
    {"name": "El Rastro", "lat": 40.407792, "lon": -3.707177},
    {"name": "Museo Thyssen-Bornemisza", "lat": 40.416873, "lon": -3.694475},
    {"name": "Casa de Campo", "lat": 40.409750, "lon": -3.745571}
]

def create_heatmap(df, lat_col, lon_col, zoom_start=15):
    map_ = folium.Map(location=[df.iloc[0][lat_col], df.iloc[0][lon_col]], tiles='OpenStreetMap', zoom_start=zoom_start)
    HeatMap(data=df[[lat_col, lon_col]], radius=10).add_to(map_)
    for spot in tourist_spots:
        Marker([spot["lat"], spot["lon"]], popup=spot["name"], icon=folium.Icon(color='red')).add_to(map_)
    return map_

def create_marker_map(df, lat_col, lon_col, popup_info):
    map_ = folium.Map(location=[df.iloc[0][lat_col], df.iloc[0][lon_col]], tiles='OpenStreetMap', zoom_start=15)
    for i in range(len(df)):
        Marker([df.iloc[i][lat_col], df.iloc[i][lon_col]], popup=popup_info(df.iloc[i])).add_to(map_)
    for spot in tourist_spots:
        Marker([spot["lat"], spot["lon"]], popup=spot["name"], icon=folium.Icon(color='red')).add_to(map_)
    return map_

def handle_general_data(df):
    df_by_distrito = df.groupby('distrito')['host_id'].count().reset_index()
    df_by_distrito.columns = ['Distrito', 'Alojamientos']

    st.write('Total de distritos:', df_by_distrito['Distrito'].nunique())
    st.dataframe(df_by_distrito, use_container_width=True)

    with st.expander("Distribución de Alojamientos por Distrito"):
        st.text("En el siguiente gráfico se muestra la distribución de alojamientos por distrito en Madrid.")
        fig = plot_scatter(
            df,
            x='longitude',
            y='latitude',
            color='distrito',
            hover_data=['name', 'price', 'room_type', 'barrio'],
            labels={'longitude': 'Longitud', 'latitude': 'Latitud', 'barrio': 'Barrio', 'distrito': 'Distrito'},
            title='Distribución de Alojamientos por Distrito'
        )
        st.plotly_chart(fig)

    with st.expander("Distribución de Alojamientos por Tipo de Habitación"):
        st.text("En el siguiente gráfico se muestra la distribución de alojamientos por tipo de habitación en Madrid.")
        fig = plot_scatter(
            df,
            x='longitude',
            y='latitude',
            color='room_type',
            hover_data=['name', 'price', 'room_type', 'barrio', 'distrito'],
            labels={'longitude': 'Longitud', 'latitude': 'Latitud', 'room_type': 'Tipo de Habitación', 'barrio': 'Barrio', 'distrito': 'Distrito'},
            title='Tipos de habitación por Distrito'
        )
        st.plotly_chart(fig)

    with st.expander("Precio Promedio por Tipo de Habitación y Distrito"):
        st.text("En este gráfico se muestra el precio promedio por tipo de habitación en cada distrito de Madrid.")
        average = df.groupby(['room_type', 'distrito'])['price'].mean().reset_index()
        fig = px.bar(
            average,
            x='distrito',
            y='price',
            color='room_type',
            labels={'room_type': 'Tipo de Habitación', 'price': 'Precio Promedio (€)', 'distrito': 'Distrito'},
            title='Precio Promedio por Tipo de Habitación y Distrito',
            facet_row='room_type',
            category_orders={'distrito': sorted(df['distrito'].unique())},
            height=2000,
            text_auto=True
        )
        fig.update_traces(
            textfont_size=10,
            textangle=0,
            textposition="outside",
            marker=dict(line=dict(width=0.5, color='DarkSlateGrey')),
        )
        fig.update_layout(
            title={'text': 'Precio Promedio por Tipo de Habitación y Distrito', 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'font': {'color': 'white'}},
            legend_title='Tipo de Habitación',
            xaxis_title='Distrito',
            yaxis_title='Precio Promedio (€)',
            margin=dict(l=50, r=50, t=80, b=50),
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Número de Alojamientos por Distrito"):
        df_by_distrito = df.groupby('distrito')['host_id'].count().reset_index()
        df_by_distrito.columns = ['Distrito', 'Alojamientos']
        fig = plot_bar(
            df_by_distrito,
            x='Distrito',
            y='Alojamientos',
            color='Distrito',
            title='Número de Alojamientos por Distrito',
            labels={'Distrito': 'Distrito', 'Alojamientos': 'Número de Alojamientos'}
        )
        st.plotly_chart(fig, use_container_width=True)

def handle_district_data(df, distrito):
    df_by_distrito = df[df['distrito'] == distrito].reset_index(drop=True)
    st.write(f'El distrito seleccionado es: **{distrito}**. Este contiene {len(df_by_distrito["host_id"].unique())} alojamientos y un total de {len(df_by_distrito)} registros.')

    barrios_distrito = df_by_distrito.groupby('barrio')['host_id'].count().reset_index()
    barrios_distrito.columns = ['Barrio', 'Alojamientos']
    st.write(f'Hay {barrios_distrito["Barrio"].nunique()} barrios en el distrito {distrito}.')
    st.dataframe(barrios_distrito, use_container_width=True)

    fig = plot_bar(
        barrios_distrito,
        x='Barrio',
        y='Alojamientos',
        color='Barrio',
        title=f'Número de alojamientos por barrio en el distrito {distrito}',
        labels={'Barrio': 'Barrios', 'Alojamientos': 'Número de alojamientos'}
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Mapa de calor con los alojamientos en el distrito {distrito}"):
        map_ = create_heatmap(df_by_distrito, 'latitude', 'longitude')
        st_folium(map_, width=700)

    with st.expander(f"Boxplot de precios de alojamientos en el distrito {distrito}"):
        df_by_distrito['log_price'] = np.log1p(df_by_distrito['price'])
        fig = plot_box(
            df_by_distrito,
            x='barrio',
            y='log_price',
            color='room_type',
            title=f'Precios por tipo de habitación en el distrito {distrito} (escala logarítmica)'
        )
        st.plotly_chart(fig)

    with st.expander(f"Mapa de alojamientos en el distrito {distrito}"):
        map_ = create_marker_map(df_by_distrito, 'latitude', 'longitude', lambda row: f"""<b>Nombre</b>: {row['name']}<br><b>Barrio</b>: {row['barrio']}<br><b>Precio</b>: {row['price']}€<br><b>Tipo de Habitación</b>: {row['room_type']}""")
        st_folium(map_, width=700)

def handle_neighborhood_data(df, barrio):
    df_by_barrio = df[df['barrio'] == barrio].reset_index(drop=True)
    st.write(f'El barrio seleccionado es: **{barrio}**. Este contiene {len(df_by_barrio["host_id"].unique())} alojamientos y un total de {len(df_by_barrio)} registros.')

    with st.expander(f"Mapa de calor con los alojamientos en el barrio {barrio}"):
        map_ = create_heatmap(df_by_barrio, 'latitude', 'longitude')
        st_folium(map_, width=700)

    with st.expander(f"Boxplot de precios de alojamientos en el barrio {barrio}"):
        df_by_barrio['log_price'] = np.log1p(df_by_barrio['price'])
        fig = plot_box(
            df_by_barrio,
            x='room_type',
            y='log_price',
            color='room_type',
            title=f'Precios por tipo de habitación en el barrio {barrio} (escala logarítmica)'
        )
        st.plotly_chart(fig)

    with st.expander(f"Mapa de alojamientos en el barrio {barrio}"):
        map_ = create_marker_map(df_by_barrio, 'latitude', 'longitude', lambda row: f"""<b>Nombre</b>: {row['name']}<br><b>Barrio</b>: {row['barrio']}<br><b>Precio</b>: {row['price']}€<br><b>Tipo de Habitación</b>: {row['room_type']}""")
        st_folium(map_, width=700)

def main():
    df = load_data()

    st.title('Madrid Airbnb Data')
    st.markdown("""
        ## Análisis de Datos de Airbnb en Madrid
        Este proyecto analiza los datos de **Airbnb** en la ciudad de Madrid, con detalles sobre precios, ubicaciones y tipos de habitaciones.
                
        ---
        ### Información general
    """)

    handle_general_data(df)

    st.markdown("""
    ---
    ### Información por Distrito
    **Distritos de Madrid:**
    - Centro
    - Chamartín
    - Salamanca
    - Tetuán
    - Chamberí
    - Retiro
    - Moncloa - Aravaca
    - Latina
    - Carabanchel
    - Arganzuela
    - Puente de Vallecas
    - San Blas - Canillejas
    - Ciudad Lineal
    - Hortaleza
    - Villaverde
    - Usera
    - Barajas
    - Moratalaz
    - Vicálvaro
    - Fuencarral - El Pardo
    - Villa de Vallecas

    Los distritos son áreas clave para la visualización y análisis de los datos. Puedes explorar estos **distritos** en el menú desplegable.
                                
    #### Selección de Distrito
    """)

    options = df['distrito'].unique()
    distrito = st.selectbox('Distrito', options)

    if distrito:
        handle_district_data(df, distrito)

        options_barrios = df[df['distrito'] == distrito]['barrio'].unique()
        barrio = st.selectbox('Barrio', options_barrios)

        if barrio:
            handle_neighborhood_data(df, barrio)

if __name__ == '__main__':
    main()
