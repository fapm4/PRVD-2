import folium
from .general_use import add_tourist_spots
import pandas as pd
import folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors  # Para convertir colores RGBA a hexadecimal
from matplotlib.colors import LinearSegmentedColormap
from IPython.display import display, HTML
from folium.plugins import Search

class BiciMAD:
    def __init__(self,data):
        self.dfbike=data
    

    def obtener_color(self,valor, min_valor, max_valor):
        # Normalizar valor entre 0 y 1
        rango_normalizado = (valor - min_valor) / (max_valor - min_valor) if max_valor > min_valor else 0
        # Crear un mapa de colores personalizado (de verde a rojo)
        cmap = LinearSegmentedColormap.from_list("verde_rojo", ["green", "yellow", "red"])
        # Obtener el color correspondiente (en formato RGBA y convertir a hexadecimal)
        color = cmap(rango_normalizado)
        return mcolors.rgb2hex(color[:3])
    
    def extraer_coordenadas(self,geolocation):
        
        
        if pd.isnull(geolocation):
            return None, None
        try:
            # Extraer la parte de las coordenadas
            start = geolocation.find('[') + 1
            end = geolocation.find(']')
            coords = geolocation[start:end].split(',')
            # Convertir las coordenadas a float
            lon = float(coords[0].strip())
            lat = float(coords[1].strip())
            return lat, lon
        except (ValueError, IndexError):
            # Si ocurre algún error, devolver None
            return None, None
    
    def Create_Map(self):
        # Filtrar address y station
        dfbike_filtered = self.dfbike[ 
            self.dfbike['station_unlock'].notnull() & (self.dfbike['station_unlock'] != "") &
            self.dfbike['station_lock'].notnull() & (self.dfbike['station_lock'] != "") &
            self.dfbike['address_unlock'].notnull() & (self.dfbike['address_unlock'] != "") &
            self.dfbike['address_lock'].notnull() & (self.dfbike['address_lock'] != "")
        ]

        # Seleccionar 1000 registros del dataset filtrado
        dfbike_sample = dfbike_filtered.sample(n=20000, random_state=42)


        dfbike_sample[['lat_unlock', 'lon_unlock']] = dfbike_sample['geolocation_unlock'].apply(
            lambda x: pd.Series(self.extraer_coordenadas(x))
        )
        dfbike_sample[['lat_lock', 'lon_lock']] = dfbike_sample['geolocation_lock'].apply(
            lambda x: pd.Series(self.extraer_coordenadas(x))
        )

        # Coordenadas únicas para estaciones
        estaciones_unlock = dfbike_sample[['station_unlock', 'unlock_station_name', 'lat_unlock', 'lon_unlock']].rename(
            columns={'station_unlock': 'station_id', 'unlock_station_name': 'station_name', 'lat_unlock': 'lat', 'lon_unlock': 'lon'}
        )
        estaciones_lock = dfbike_sample[['station_lock', 'lock_station_name', 'lat_lock', 'lon_lock']].rename(
            columns={'station_lock': 'station_id', 'lock_station_name': 'station_name', 'lat_lock': 'lat', 'lon_lock': 'lon'}
        )

        # Convertir stations a int
        dfbike_sample['station_lock'] = dfbike_sample['station_lock'].astype(float).astype(int)
        dfbike_sample['station_unlock'] = dfbike_sample['station_unlock'].astype(float).astype(int)


        # Combinar y eliminar duplicados
        estaciones = pd.concat([estaciones_unlock, estaciones_lock]).drop_duplicates(subset=['station_id']).dropna()

        # Calcular conteos
        conteo_desbloqueos = dfbike_sample.groupby('station_unlock').size().rename("desbloqueos")
        conteo_bloqueos = dfbike_sample.groupby('station_lock').size().rename("bloqueos")

        # Unir conteos
        estaciones = estaciones.set_index('station_id')
        estaciones = estaciones.join(conteo_desbloqueos).join(conteo_bloqueos).fillna(0).reset_index()

        # Calcular la actividad total por estación
        estaciones['total_actividad'] = estaciones['desbloqueos'] + estaciones['bloqueos']

        # Calcular los valores mínimo y máximo de actividad total
        min_total_actividad = estaciones['total_actividad'].min()
        max_total_actividad = estaciones['total_actividad'].max()

        # Función para normalizar valores y asignar un color

        # Madrid map
        mapa = folium.Map(location=[40.4168, -3.7038], zoom_start=12)

        # Añadir marcadores con colores basados en actividad total
        for _, row in estaciones.iterrows():
            # Determinar color según el total de actividad
            color = self.obtener_color(row['total_actividad'], min_total_actividad, max_total_actividad)
            
            # Contenido del popup con bloqueos y desbloqueos separados
            popup_text = f"""
            <b>Estación:</b> {row['station_name']}<br>
            <b>Desbloqueos:</b> {int(row['desbloqueos'])}<br>
            <b>Bloqueos:</b> {int(row['bloqueos'])}<br>
            <b>Total Actividad:</b> {int(row['total_actividad'])}
            """
            # Agregar marcador 
            folium.Marker(
                location=[row['lat'], row['lon']],
                icon=folium.Icon(icon="bicycle", prefix="fa", color="black", icon_color=color),  # Icono de bicicleta
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(mapa)

        return mapa