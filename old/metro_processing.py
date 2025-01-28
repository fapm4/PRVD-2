import geopandas as gpd
import pandas as pd
import os
from general_purpose import add_tourist_spots
import folium

def ordenar_lineas(linea):
	return int(linea.replace('Linea ', ''))


class MetroProcessing:
    def __init__(self, listings, gdf):
        self.gdf = gdf
        self.listings = listings

        data_path = os.path.join(os.getcwd(), 'data')
        self.metro_data = pd.read_csv(os.path.join(data_path, "metro.csv"), sep=",")
        self.metro_data['Longitude'] = self.metro_data['Longitude'].str.replace(',', '.').astype(float)
        self.metro_data['Latitude'] = self.metro_data['Latitude'].str.replace(',', '.').astype(float)
        self.metro_data['Traffic'] = self.metro_data['Traffic'].str.replace('.', '').astype(int)

    def add_borders(self, m):
        folium.GeoJson(
            self.gdf, 
            name="Distritos de Madrid",
            style_function=lambda feature: {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.1,
            },
            
            tooltip=folium.GeoJsonTooltip(
                fields=['neighbourhood_group'],
                aliases=['Distrito:'],
                localize=True
            )
        
        ).add_to(m)

    def add_cloropleths_barrio(self, m):
        avg_price_per_neighbourhood = self.listings.groupby('neighbourhood')['price'].mean().reset_index()
        avg_price_per_neighbourhood = avg_price_per_neighbourhood.merge(self.gdf, left_on='neighbourhood', right_on='neighbourhood')

        folium.Choropleth(
            geo_data=self.gdf,
            name='choropleth',
            data=avg_price_per_neighbourhood,
            columns=['neighbourhood', 'price'],
            key_on='feature.properties.neighbourhood',
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Precio Promedio (€/noche)',
            highlight=True
        ).add_to(m)

        gdf_with_prices = self.gdf.merge(avg_price_per_neighbourhood, on="neighbourhood")
        gdf_with_prices["price"] = gdf_with_prices["price"].astype(str).str.replace(',', '.').astype(float)
        gdf_with_prices["price"] = gdf_with_prices["price"].apply(lambda x: f"{x:.2f}")


        gdf_with_prices = gdf_with_prices.rename(columns={'geometry_x': 'geometry'}).set_geometry('geometry')
        if 'geometry_y' in gdf_with_prices.columns:
            gdf_with_prices = gdf_with_prices.drop(columns=['geometry_y'])

        folium.GeoJson(
            data=gdf_with_prices,
            style_function=lambda feature: {
                'fillColor': 'transparent',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.0,
            },
            popup=folium.GeoJsonPopup(
                fields=['neighbourhood', 'price'],
                aliases=['Barrio:', 'Precio Promedio (€):'],
                localize=True
            )
        ).add_to(m)

    def add_cloropleths_distrito(self, m):
        avg_price_per_neighbourhood = self.listings.groupby('neighbourhood_group')['price'].mean().reset_index()
        avg_price_per_neighbourhood = avg_price_per_neighbourhood.merge(self.gdf, left_on='neighbourhood_group', right_on='neighbourhood_group')

        folium.Choropleth(
            geo_data=self.gdf,
            name='choropleth',
            data=avg_price_per_neighbourhood,
            columns=['neighbourhood_group', 'price'],
            key_on='feature.properties.neighbourhood_group',
            fill_color='YlGnBu',
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name='Precio Promedio (€/noche)',
            highlight=True
        ).add_to(m)

        gdf_with_prices = self.gdf.merge(avg_price_per_neighbourhood, on="neighbourhood_group")
        gdf_with_prices["price"] = gdf_with_prices["price"].astype(str).str.replace(',', '.').astype(float)
        gdf_with_prices["price"] = gdf_with_prices["price"].apply(lambda x: f"{x:.2f}")


        gdf_with_prices = gdf_with_prices.rename(columns={'geometry_x': 'geometry'}).set_geometry('geometry')
        if 'geometry_y' in gdf_with_prices.columns:
            gdf_with_prices = gdf_with_prices.drop(columns=['geometry_y'])

        folium.GeoJson(
            data=gdf_with_prices,
            style_function=lambda feature: {
                'fillColor': 'transparent',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.0,
            },
            popup=folium.GeoJsonPopup(
                fields=['neighbourhood_group', 'price'],
                aliases=['Distrito:', 'Precio Promedio (€):'],
                localize=True
            )
        ).add_to(m)

    def get_madrid_metro_map(self, barrio):

        mapa_metro = folium.Map(
            location=[40.4168, -3.7038],
            zoom_start=12
        )

        if barrio:
            self.add_cloropleths_barrio(mapa_metro)
        else:
            self.add_cloropleths_distrito(mapa_metro)

        # Colores oficiales del Metro de Madrid
        colores_linea = {
            'Linea 1': '#2B7CE9',    # Azul claro
            'Linea 2': '#E6343C',    # Rojo
            'Linea 3': '#FFD700',    # Amarillo
            'Linea 4': '#8B4513',    # Marrón
            'Linea 5': '#4CAF50',    # Verde
            'Linea 6': '#808080',    # Gris
            'Linea 7': '#FF8C00',    # Naranja
            'Linea 8': '#FFC0CB',    # Rosa
            'Linea 9': '#800080',    # Morado
            'Linea 10': '#000080',   # Azul oscuro
            'Linea 11': '#90EE90',   # Verde claro
            'Linea 12': '#DAA520'    # Dorado más oscuro (GoldenRod)
        }

        # Creamos las capas para cada línea
        for linea in sorted(self.metro_data['Line'].unique(), key=ordenar_lineas):  # Ordenamos usando la función auxiliar
            
            # Creamos un grupo para esta línea
            line_group = folium.FeatureGroup(name=f'{linea}')
            
            # Filtramos y ordenamos las estaciones de esta línea
            df_linea = self.metro_data[self.metro_data['Line'] == linea].sort_values('Order of Points')
            
            # Primero dibujamos las conexiones entre estaciones
            coordinates = df_linea[['Latitude', 'Longitude']].values.tolist()
            if len(coordinates) > 1:
                folium.PolyLine(
                    locations=coordinates,
                    color=colores_linea[linea],
                    weight=3,
                    opacity=0.8
                ).add_to(line_group)
            
            # Calculamos el rango de tráfico para esta línea
            min_traffic = df_linea['Traffic'].min()
            max_traffic = df_linea['Traffic'].max()
            min_radius = 5
            max_radius = 30
            
            for _, row in df_linea.iterrows():
                radius = min_radius + (row['Traffic'] - min_traffic) * (max_radius - min_radius) / (max_traffic - min_traffic)
                
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=radius,
                    popup=f"Estación: {row['Station']}<br>Línea: {row['Line']}<br>Tráfico: {row['Traffic']:,} pasajeros",
                    color=colores_linea[linea],
                    fill=True,
                    fill_color=colores_linea[linea],
                    fill_opacity=0.2,
                    weight=3,
                    tooltip=f"{row['Station']}: {row['Traffic']:,} pasajeros"
                ).add_to(line_group)
            
            line_group.add_to(mapa_metro)

    
        html_title = f"""
        <h3 style="text-align:center">Mapa de cloropletas junto con metro por {"barrios" if barrio else "distritos"}</h3>"""
        mapa_metro.get_root().html.add_child(folium.Element(html_title))

        folium.LayerControl(collapsed=False).add_to(mapa_metro)
        add_tourist_spots(mapa_metro)

        return mapa_metro           
