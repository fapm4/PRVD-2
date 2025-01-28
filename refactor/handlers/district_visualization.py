from dash import html, dcc
import numpy as np
from dash import html, dcc
import numpy as np
import plotly.express as px
from folium.plugins import HeatMap
import folium
from branca.colormap import LinearColormap

from .general_use import add_tourist_spots

class DistrictVisualization:
    def __init__(self, listings, gdf):
        self.listings = listings
        self.gdf = gdf

    def get_district_info(self, distrito):
        df_filtered = self.listings[self.listings['neighbourhood_group'] == distrito]
        avg_price = df_filtered['price'].mean()
        median_price = df_filtered['price'].median()
        avg_min_nights = df_filtered['minimum_nights'].mean()
        avg_n_listings = df_filtered.shape[0]
        room_type_counts = df_filtered['room_type'].value_counts().reset_index()
        room_type_counts.columns = ['room_type', 'count']

        data = html.Div([
            html.H4(f'Estadísticas para el distrito {distrito}', style={
                'color': '#000', 
                'text-align': 'center', 
                'margin-bottom': '20px'
            }),

            html.Div([
                html.H5('Precios', style={
                    'color': '#000', 
                    'margin-top': '20px',
                    'margin-bottom': '10px',
                    'border-bottom': '2px solid #ccc',
                    'padding-bottom': '5px'
                }),
                html.Table([
                    html.Tr([
                        html.Th('Precio promedio', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px',
                            'background-color': '#f4f4f4'
                        }),
                        html.Th('Precio mediano', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px',
                            'background-color': '#f4f4f4'
                        })
                    ]),
                    html.Tr([
                        html.Td(f'{avg_price:.2f}€', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px'
                        }),
                        html.Td(f'{median_price:.2f}€', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px'
                        })
                    ])
                ], style={
                    'border-collapse': 'collapse', 
                    'margin-bottom': '20px', 
                    'width': '100%'
                })
            ]),

            html.Div([
                html.H5('Estadísticas de reservas', style={
                    'color': '#000', 
                    'margin-top': '20px',
                    'margin-bottom': '10px',
                    'border-bottom': '2px solid #ccc',
                    'padding-bottom': '5px'
                }),
                html.Table([
                    html.Tr([
                        html.Th('Noches mínimas promedio', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px',
                            'background-color': '#f4f4f4'
                        }),
                        html.Th('Número de listados', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px',
                            'background-color': '#f4f4f4'
                        })
                    ]),
                    html.Tr([
                        html.Td(f'{avg_min_nights:.2f}', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px'
                        }),
                        html.Td(f'{avg_n_listings}', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px'
                        })
                    ])
                ], style={
                    'border-collapse': 'collapse', 
                    'margin-bottom': '20px', 
                    'width': '100%'
                })
            ]),

            html.Div([
                html.H5('Tipos de habitación', style={
                    'color': '#000', 
                    'margin-top': '20px',
                    'margin-bottom': '10px',
                    'border-bottom': '2px solid #ccc',
                    'padding-bottom': '5px'
                }),
                html.Table([
                    html.Tr([
                        html.Th('Tipo de habitación', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px',
                            'background-color': '#f4f4f4'
                        }),
                        html.Th('Cantidad', style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px',
                            'background-color': '#f4f4f4'
                        })
                    ]),
                    *[html.Tr([
                        html.Td(row['room_type'], style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px'
                        }),
                        html.Td(row['count'], style={
                            'color': '#000', 
                            'border': '1px solid #ddd', 
                            'padding': '10px'
                        })
                    ]) for index, row in room_type_counts.iterrows()]
                ], style={
                    'border-collapse': 'collapse', 
                    'margin-bottom': '20px', 
                    'width': '100%'
                })
            ])
        ])

        
        log_price = np.log1p(df_filtered['price'])

        fig_violin = px.violin(df_filtered, 
                    x='neighbourhood', 
                    y=log_price,
                    color='room_type',
                    box=True, 
                    points="all", 
                    title=f'Distribución de precios en: {distrito}',
                    custom_data=['price', 'room_type'],
                    labels={'neighbourhood': 'Distrito', 'price': 'Precio (€/noche)', 'room_type': 'Tipo de habitación'}
            )
        
        fig_violin.update_traces(
        hovertemplate="<br>".join([
            "Distrito: %{x}",
            "Tipo de habitación: %{customdata[1]}",
            "Log(Precio): %{y:.2f}",
            "Precio Original: %{customdata[0]:,.2f}",
            ])
        )

        fig_violin.update_layout(
            legend_title_text='Tipo de Habitación',
            xaxis=dict(title='Barrio'),
            yaxis=dict(title='Log(Precio)'),
        )

        average = df_filtered.groupby(['neighbourhood'])['price'].mean().reset_index()
        fig_bar = px.bar(
            average,
            x='neighbourhood',
            y='price',
            color='neighbourhood',
            title=f'Precio Promedio por: {distrito} (todos los tipos de alojamiento)',
            labels={
                'price': 'Precio Promedio (€/noche)',
                'neighbourhood': 'Barrio'
            }
        )

        fig_bar.update_traces(
            hovertemplate="<br>".join([
                "Barrio: %{x}",
                "Precio Promedio: %{y:.2f} €/noche"
            ])
        )

        fig_bar.update_layout(
            xaxis=dict(title='Barrio'),
            yaxis=dict(title='Precio Promedio (€/noche)')
        )

        fig_hist = px.histogram(
            df_filtered,
            x='price',
            color='neighbourhood',
            nbins=30,
            title=f'Histograma de precios en: {distrito}',
            labels={'price': 'Precio (€)', 'neighbourhood': 'Barrio'},
            hover_data=['neighbourhood']
        )

        fig_hist.update_traces(
            opacity=0.75,
            hovertemplate="<br>".join([
                "Precio: %{x:.2f}€",
                "Frecuencia: %{y}"
            ])
        )

        fig_hist.update_layout(
            xaxis=dict(title='Precio (€)'),
            yaxis=dict(title='Frecuencia')
        )

        fig_map = px.scatter_mapbox(
            df_filtered,
            lat='latitude',
            lon='longitude',
            color='price',
            size='price',
            hover_name='name',
            hover_data=['price', 'room_type', 'minimum_nights'],
            title=f'Mapa de listados en: {distrito}',
            labels={'price': 'Precio (€)', 'room_type': 'Tipo de habitación', 'minimum_nights': 'Noches mínimas'},
            zoom=10
        )

        fig_map.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 30, "l": 0, "b": 0}
        )

        return html.Div([
            data,
            dcc.Graph(figure=fig_violin),
            dcc.Graph(figure=fig_bar),
            dcc.Graph(figure=fig_hist),
            dcc.Graph(figure=fig_map)
        ])
    
    def get_district_cloropleth(self, distrito):
        # Filtrar los datos por distrito
        df_filtered = self.listings[self.listings['neighbourhood_group'] == distrito]

        # Calcular el precio promedio por barrio
        avg_price_by_neighbourhood = df_filtered.groupby('neighbourhood')['price'].mean().reset_index()

        # Filtrar el GeoDataFrame por distrito y unirlo con los precios promedio
        gdf_filtered = self.gdf[self.gdf['neighbourhood_group'] == distrito]
        gdf_filtered = gdf_filtered.merge(avg_price_by_neighbourhood, left_on='neighbourhood', right_on='neighbourhood')
        gdf_filtered['price'] = gdf_filtered['price'].round(2)

        # Crear el mapa base
        m = folium.Map(
            location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()],
            zoom_start=13,
            tiles="CartoDB positron"
        )

        # Título del mapa
        title_html = '''
        <h3 style="font-size:16px; text-align:center; margin-top:10px; margin-bottom:10px;">
            <b>Mapa de Cloropletas de los Precios de los Alojamientos en {distrito}</b>
        </h3>
        '''.format(distrito=distrito)
        m.get_root().html.add_child(folium.Element(title_html))

        # Crear el choropleth usando folium
        folium.Choropleth(
            geo_data=gdf_filtered,
            name='choropleth',
            data=gdf_filtered,
            columns=['neighbourhood', 'price'],
            key_on='feature.properties.neighbourhood',
            fill_color='YlGnBu',  # Esquema de colores
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Precio Promedio (€/noche)',
            highlight=True
        ).add_to(m)

        # Agregar un GeoJson con tooltips para mostrar información detallada
        folium.GeoJson(
            gdf_filtered,
            name='Barrios',
            style_function=lambda feature: {
                'fillColor': 'transparent',  # Sin relleno adicional
                'color': 'black',  # Borde de los polígonos
                'weight': 1,
                'fillOpacity': 0  # Sin relleno
            },
            tooltip=folium.features.GeoJsonTooltip(
                fields=['neighbourhood', 'price'],
                aliases=['Barrio:', 'Precio promedio (€/noche):'],
                localize=True,
                sticky=True
            )
        ).add_to(m)

        # Agregar puntos turísticos
        add_tourist_spots(m)

        # Agregar control de capas
        folium.LayerControl(collapsed=False).add_to(m)

        return m

    def get_district_heatmap(self, distrito):
        df_filtered = self.listings[self.listings['neighbourhood_group'] == distrito]
        gdf_filtered = self.gdf[self.gdf['neighbourhood_group'] == distrito]

        if df_filtered.empty:
            return html.Div(f"No hay datos disponibles para el distrito: {distrito}.")
        
        m = folium.Map(
            location=[df_filtered['latitude'].mean(), df_filtered['longitude'].mean()],
            zoom_start=13,
            tiles="CartoDB positron"
        )

        title_html = '''
        <h3 style="font-size:16px; text-align:center; margin-top:10px; margin-bottom:10px;">
            <b>Mapa de Calor de los Precios de los Alojamientos en {distrito}</b>
        </h3>
        '''.format(distrito=distrito)

        m.get_root().html.add_child(folium.Element(title_html))
        
        HeatMap(
            data=df_filtered[['latitude', 'longitude', 'price']].groupby(['latitude', 'longitude']).mean().reset_index().values.tolist(),
            radius=10,
            blur=15,
            max_zoom=1,
            min_opacity=0.5,
        ).add_to(m)

        avg_price_by_neighbourhood = df_filtered.groupby('neighbourhood')['price'].mean().reset_index()
        gdf_filtered = gdf_filtered.merge(avg_price_by_neighbourhood, on='neighbourhood')
        gdf_filtered['price'] = gdf_filtered['price'].round(2)

        folium.GeoJson(
            gdf_filtered,
            name='Barrios',
            style_function=lambda feature: {
                'fillOpacity': 0,
                'color': 'black', 
                'weight': 1
            },
            tooltip=folium.features.GeoJsonTooltip(
                fields=['neighbourhood', 'price'],
                aliases=['Barrio:', 'Precio promedio (€/noche):'],
                localize=True,
                sticky=True 
            )
        ).add_to(m)

        add_tourist_spots(m)

        return m
