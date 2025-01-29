import folium
from dash import html
import pandas as pd

class MetroMap:
    def __init__(self, base_path):
        self.base_path = base_path
        self.df = self._load_data()
        self.colors = self._setup_colors()

    def _load_data(self):
        # Cargar datos del metro
        df = pd.read_csv(self.base_path)  # Ajusta la ruta según tu estructura

        df['Longitude'] = df['Longitude'].str.replace(',', '.').astype(float)
        df['Latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
        # La columna de tráfico tiene puntos que separan miles
        df['Traffic'] = df['Traffic'].str.replace('.', '').astype(int)
        return df
    
    # Función auxiliar para ordenar las líneas correctamente
    def ordenar_lineas(self, linea):
        return int(linea.replace('Linea ', ''))
    
    def _setup_colors(self):
        # Definir colores para las líneas
        return {
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

    def create_map(self):
        # Creamos el mapa con las conexiones
        mapa_metro = folium.Map(
            location=[40.4168, -3.7038],
            zoom_start=12
        )

        # Creamos las capas para cada línea
        for linea in sorted(self.df['Line'].unique(), key=self.ordenar_lineas):  # Ordenamos usando la función auxiliar
            
            # Creamos un grupo para esta línea
            line_group = folium.FeatureGroup(name=f'{linea}')
            
            # Filtramos y ordenamos las estaciones de esta línea
            df_linea = self.df[self.df['Line'] == linea].sort_values('Order of Points')
            
            # Primero dibujamos las conexiones entre estaciones
            coordinates = df_linea[['Latitude', 'Longitude']].values.tolist()
            if len(coordinates) > 1:
                folium.PolyLine(
                    locations=coordinates,
                    color=self.colors[linea],
                    weight=3,
                    opacity=0.8
                ).add_to(line_group)
            
            # Calculamos el rango de tráfico para esta línea
            min_traffic = df_linea['Traffic'].min()
            max_traffic = df_linea['Traffic'].max()
            min_radius = 5
            max_radius = 30
            
            # Luego añadimos las estaciones
            for _, row in df_linea.iterrows():
                # Calculamos el radio proporcional al tráfico
                radius = min_radius + (row['Traffic'] - min_traffic) * (max_radius - min_radius) / (max_traffic - min_traffic)
                
                # Añadimos el marcador de la estación
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=radius,
                    popup=f"Estación: {row['Station']}<br>Línea: {row['Line']}<br>Tráfico: {row['Traffic']:,} pasajeros",
                    color=self.colors[linea],
                    fill=True,
                    fill_color=self.colors[linea],
                    fill_opacity=0.2,
                    weight=3,
                    tooltip=f"{row['Station']}: {row['Traffic']:,} pasajeros"
                ).add_to(line_group)
            
            line_group.add_to(mapa_metro)

        # Añadimos el control de capas
        folium.LayerControl(collapsed=False).add_to(mapa_metro)

        # Mostramos el mapa
        return mapa_metro