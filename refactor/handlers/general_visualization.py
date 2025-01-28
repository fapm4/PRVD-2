from shapely.geometry import Polygon, MultiPolygon
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from dash import html, dcc
from geopy.distance import geodesic
import folium
from folium.plugins import HeatMap
from .general_use import add_tourist_spots

class GeneralVisualization:
    def __init__(self, listings, gdf):
        self.listings = listings
        self.gdf = gdf

    def get_all_graphs(self):
        fig1 = self.get_alojamientos_por_distrito()
        fig2 = self.get_tipo_de_habitacion_por_distrito()
        fig3 = self.get_precio_promedio_por_distrito()
        fig4 = self.get_violins_plot()
        fig5 = self.get_dist_precio_por_hab()
        fig6 = self.get_rel_precio_tam()
        fig7 = self.get_rel_cal_precio()

        fig_8_1, fig_8_2, fig_8_3 = self.get_rel_precio_dist()

        fig_9 = self.get_corr_matrix()

        return html.Div([
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3),
            dcc.Graph(figure=fig4),
            dcc.Graph(figure=fig5),
            dcc.Graph(figure=fig6),
            dcc.Graph(figure=fig7),
            dcc.Graph(figure=fig_8_1),
            dcc.Graph(figure=fig_8_2),
            dcc.Graph(figure=fig_8_3),
            dcc.Graph(figure=fig_9)
        ])


    def get_alojamientos_por_distrito(self):
        fig = px.scatter(
            self.listings,
            x='longitude',
            y='latitude',
            color='neighbourhood_group',
            hover_data=['name', 'price', 'room_type', 'neighbourhood'],
            labels={
                'neighbourhood_group': 'Distrito',
                'neighbourhood': 'Barrio',
                'price': 'Precio',
                'room_type': 'Tipo de Habitación',
                'name': 'Nombre'
            },
            title='Distribución de Alojamientos por Distrito'
        )

        for _, row in self.gdf.iterrows():
            geometry = row['geometry']
            if isinstance(geometry, MultiPolygon):
                for polygon in geometry.geoms:
                    lon, lat = polygon.exterior.xy
                    fig.add_trace(
                        go.Scatter(
                            x=list(lon),
                            y=list(lat),
                            mode='lines',
                            line=dict(width=1, color='black'),
                            name=row['neighbourhood_group'],
                            hoverinfo='none'
                        )
                    )
            elif isinstance(geometry, Polygon):
                lon, lat = geometry.exterior.xy
                fig.add_trace(
                    go.Scatter(
                        x=list(lon),
                        y=list(lat),
                        mode='lines',
                        line=dict(width=1, color='black'),
                        name=row['neighbourhood_group'],
                        hoverinfo='none'
                    )
                )

        fig.update_traces(marker=dict(size=8, opacity=0.7), selector=dict(mode='markers'))
        fig.update_layout(
            legend_title_text='Distrito',
            xaxis=dict(title='Longitud'),
            yaxis=dict(title='Latitud'),
            height=600,
            width=800
        )

        return fig
    
    def get_tipo_de_habitacion_por_distrito(self):
        fig = px.scatter(
            self.listings,
            x='longitude',
            y='latitude',
            color='room_type',
            hover_data=['name', 'price', 'room_type'],
            labels={
                'room_type': 'Tipo de Habitación',
                'price': 'Precio',
                'name': 'Nombre'
            },
            title='Tipos de habitación por Distrito'
        )

        fig.update_traces(marker=dict(size=8, opacity=0.5), selector=dict(mode='markers'))

        for _, row in self.gdf.iterrows():
            geometry = row['geometry']
            name = row['neighbourhood_group'] if 'neighbourhood_group' in row else "Desconocido"
            
            if isinstance(geometry, MultiPolygon):
                polygons = geometry.geoms
            else:
                polygons = [geometry]
            
            for polygon in polygons:
                x, y = polygon.exterior.xy

                fig.add_trace(
                    go.Scatter(
                        x=list(x),
                        y=list(y), 
                        mode='lines',
                        line=dict(color='rgba(0, 0, 255, 0.3)', width=1),
                        name=name,
                        hoverinfo='none'
                    )
                )

        fig.update_layout(
            legend_title_text='Tipo de Habitación',
            xaxis=dict(title='Longitud'),
            yaxis=dict(title='Latitud'),
            height=600,
            width=800,
            showlegend=True
        )

        return fig

    def get_precio_promedio_por_distrito(self):
        average = self.listings.groupby(['room_type','neighbourhood_group'])['price'].mean().reset_index()
        fig = px.bar(
            average,
            x='neighbourhood_group',
            y='price',
            color='room_type',
            labels={
                'room_type': 'Tipo de Habitación',
                'price': 'Precio Promedio (€)',
                'neighbourhood_group': 'Distrito'
            },
            title='Precio Promedio por Tipo de Habitación y Distrito',
            facet_row='room_type',
            category_orders={'distrito': sorted(self.listings['neighbourhood_group'].unique())}, 
            height=1000,
            text_auto=True
        )

        fig.update_traces(
            textfont_size=10, 
            textangle=0, 
            textposition="outside", 
            marker=dict(line=dict(width=0.5, color='DarkSlateGrey'))
        )

        fig.update_layout(
            title={
                'text': 'Precio Promedio por Tipo de Habitación y Distrito',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            legend_title='Tipo de Habitación',
            xaxis_title='Distrito',
            yaxis_title='Precio Promedio (€)',
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='whitesmoke',
            plot_bgcolor='white'
        )

        return fig
    
    def get_violins_plot(self):
        self.listings['log_price'] = np.log1p(self.listings['price'])

        fig = px.box(self.listings, 
                    x='neighbourhood_group', 
                    y='log_price',
                    color='room_type',
                    title='Precios por tipo de habitación por distrito (escala logarítmica)', 
                    points='all',
                    width=1200,
                    custom_data=['price', 'room_type'],
                    labels={'neighbourhood_group': 'Distrito', 'log_price': 'Log(Precio)', 'room_type': 'Tipo de Habitación'}
                )

        fig.update_traces(
            hovertemplate="<br>".join([
                "Distrito: %{x}",
                "Tipo de habitación: %{customdata[1]}",
                "Log(Precio): %{y:.2f}",
                "Precio Original: %{customdata[0]:,.2f}",
            ])
        )

        fig.update_layout(
            legend_title_text='Tipo de Habitación',
            xaxis=dict(title='Distrito'),
        )
        
        return fig
    
    def get_precio_promedio_por_distrito(self):
        average = self.listings.groupby(['neighbourhood_group'])['price'].mean().reset_index()

        fig = px.bar(
            average,
            x='neighbourhood_group',
            y='price',
            color='neighbourhood_group',
            title='Precio Promedio por Distrito (todos los tipos de alojamiento)',
            labels={
                'price': 'Precio Promedio (€)',
                'neighbourhood_group': 'Distrito'
            }
        )

        fig.update_traces(
            hovertemplate="<br>".join([
                "Distrito: %{x}",
                "Precio Promedio: %{y:.2f}"
            ])
        )

        fig.update_layout(
            xaxis=dict(title='Distrito'),
            yaxis=dict(title='Precio Promedio (€)')
        )

        return fig
    
    def get_dist_precio_por_hab(self):
        fig = px.histogram(
            self.listings, 
            x='price', 
            color='room_type', 
            marginal='box',
            title='Distribución de Precios por Tipo de Habitación',
            labels={'price': 'Precio (€)', 'room_type': 'Tipo de Habitación', 'count': 'Número de Alojamientos'}
        )
        
        return fig
    
    def get_rel_precio_tam(self):
        fig = px.scatter(
            self.listings, 
            x='m2', 
            y='log_price', 
            color='room_type',
            hover_data=['name', 'neighbourhood_group', 'neighbourhood'],
            labels={'m2': 'Tamaño (m²)', 'log_price': 'Log(Precio)', 'room_type': 'Tipo de Habitación', 'neighbourhood_group': 'Distrito', 'neighbourhood': 'Barrio'},
            title='Relación entre Precio y Tamaño de los Alojamientos',
            custom_data=['price']  
        )

        fig.update_traces(
            hovertemplate="<br>".join([
                "Tamaño (m²): %{x:.2f}", 
                "Log(Precio): %{y:.2f}€",
                "Precio Original: %{customdata[0]:,.2f}€",
            ])
        )

        fig.update_layout(
            legend_title_text='Tipo de Habitación',
            xaxis=dict(title='Tamaño (m²)'),
            yaxis=dict(title='Log(Precio)'),
            height=600
        )

        return fig
    
    def get_rel_cal_precio(self):
        fig = px.scatter(
            self.listings, 
            x='review_scores_rating', 
            y='log_price', 
            color='room_type',
            labels={'review_scores_rating': 'Calificación', 'price': 'Precio (€)', 'room_type': 'Tipo de Habitación', 'log_price': 'Log(Precio)'},
            title='Relación entre Calificación y Precio'
        )
        
        return fig
    
    def get_rel_precio_dist(self):
        puerta_del_sol = (40.416775, -3.703790)
        retiro = (40.415260, -3.684416)
        gran_via = (40.420347, -3.705774)

        self.listings['distance_to_sol'] = self.listings.apply(lambda row: geodesic(puerta_del_sol, (row['latitude'], row['longitude'])).km, axis=1)
        self.listings['distance_to_retiro'] = self.listings.apply(lambda row: geodesic(retiro, (row['latitude'], row['longitude'])).km, axis=1)
        self.listings['distance_to_gran_via'] = self.listings.apply(lambda row: geodesic(gran_via, (row['latitude'], row['longitude'])).km, axis=1)

        fig_1 = px.scatter(
            self.listings, 
            x='distance_to_sol', 
            y='price', 
            color='room_type', 
            title='Relación entre Precio y Distancia a la Puerta del Sol',
            labels={'distance_to_sol': 'Distancia a Puerta del Sol (km)', 'price': 'Precio (€)', 'room_type': 'Tipo de Habitación'}
        )

        fig_2 = px.scatter(
            self.listings, 
            x='distance_to_retiro', 
            y='price', 
            color='room_type', 
            title='Relación entre Precio y Distancia al Parque del Retiro',
            labels={'distance_to_retiro': 'Distancia al Parque del Retiro (km)', 'price': 'Precio (€)', 'room_type': 'Tipo de Habitación'}
        )

        fig_3 = px.scatter(
            self.listings, 
            x='distance_to_gran_via', 
            y='price', 
            color='room_type', 
            title='Relación entre Precio y Distancia a Gran Vía',
            labels={'distance_to_gran_via': 'Distancia a Gran Vía (km)', 'price': 'Precio (€)', 'room_type': 'Tipo de Habitación'}
        )

        return fig_1, fig_2, fig_3

    def get_corr_matrix(self):
        corr = self.listings[['price', 'm2', 'log_price', 'review_scores_rating', 'distance_to_sol', 'distance_to_retiro', 'distance_to_gran_via']].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.index,
            y=corr.columns,
            colorscale='Viridis',
            zmin=-1,
            zmax=1
        ))

        fig.update_layout(
            title='Matriz de Correlación',
            xaxis_title='Variables',
            yaxis_title='Variables',
            width=800,
            height=800
        )

        return fig
    
    def get_madrid_cloropleth(self):
        avg_price_by_district = self.listings.groupby('neighbourhood_group')['price'].mean().reset_index()
        avg_price_by_district.rename(columns={'price': 'avg_price'}, inplace=True)

        gdf_with_prices = self.gdf.merge(avg_price_by_district, left_on='neighbourhood_group', right_on='neighbourhood_group')

        m = folium.Map(location=[40.416775, -3.703790], zoom_start=12, tiles="CartoDB positron")

        folium.Choropleth(
            geo_data=gdf_with_prices,
            data=gdf_with_prices,
            columns=['neighbourhood_group', 'avg_price'],
            key_on='feature.properties.neighbourhood_group',
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Precio promedio (€)'
        ).add_to(m)

        folium.GeoJson(
            gdf_with_prices,
            style_function=lambda x: {'fillColor': 'transparent', 'color': 'blue', 'weight': 0.5},
            tooltip=folium.GeoJsonTooltip(
                fields=['neighbourhood_group', 'avg_price'],
                aliases=['Distrito:', 'Precio promedio (€):'],
                localize=True
            )
        ).add_to(m)

        add_tourist_spots(m)

        return m

    def get_madrid_heatmap(self):
        heat_data = self.listings[['latitude', 'longitude', 'price']].dropna()

        m = folium.Map(location=[40.416775, -3.703790], zoom_start=12, tiles="CartoDB positron")

        HeatMap(
            data=heat_data[['latitude', 'longitude', 'price']].values,
            radius=10,
            blur=15,
            max_zoom=1,
            min_opacity=0.5
        ).add_to(m)

        avg_price_by_neighbourhood = self.listings.groupby('neighbourhood')['price'].mean().reset_index()
        gdf_filtered = self.gdf.merge(avg_price_by_neighbourhood, on='neighbourhood')
        gdf_filtered['price'] = gdf_filtered['price'].round(2)

        folium.GeoJson(
            gdf_filtered,
            name='Distritos',
            style_function=lambda feature: {
                'fillOpacity': 0,
                'color': 'black', 
                'weight': 1
            },
            tooltip=folium.features.GeoJsonTooltip(
                fields=['neighbourhood_group', 'neighbourhood', 'price'],
                aliases=['Distrito:', 'Barrio', 'Precio promedio (€/noche):'],
                localize=True,
                sticky=True 
            )
        ).add_to(m)

        return m

