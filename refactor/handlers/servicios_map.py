import folium
from folium.plugins import MarkerCluster
import pandas as pd
import os

class ServiciosMap:
    def __init__(self, base_path):
        self.base_path = base_path

        # Cargar los dataframes
        self.dataframes = {
            "Restaurantes": pd.read_csv(os.path.join(base_path,  'restaurantes.csv'), sep=';'),
            "Centros de Salud": pd.read_csv(os.path.join(base_path,  'salud.csv'), sep=';'),
            "Parques": pd.read_csv(os.path.join(base_path,  'jardines.csv'), sep=';'),
            "Fuentes": pd.read_csv(os.path.join(base_path,  'fuentes_potables.csv'), sep=';'),
            "Fuentes mascotas": pd.read_csv(os.path.join(base_path,  'fuentes_mascotas.csv'), sep=';')
        }

        # Diccionario de iconos según el tipo
        self.iconos = {
            "Restaurantes": "cutlery",
            "Parques": "tree",
            "Fuentes": "tint",
            "Fuentes mascotas": "dog",
            "Centros de Salud": "medkit"
        }

        
    @staticmethod
    def generar_mapa_tipo(mapa, data, tipo, icono):
    
        cluster = MarkerCluster(name=tipo).add_to(mapa)  # Añadimos una capa para cada tipo

        # Recorremos el dataframe para añadir marcadores personalizados
        for _, row in data.iterrows():

            texto_popup = ""

            if tipo == "Restaurantes":
                texto_popup = f"<b>{row['nombre']}</b><br>Cocina: {row['categorias']}<br>Horario: {row['horario']}<br>Teléfono: {row['telefono']}"
            elif tipo == "Parques":
                texto_popup = f"<b>{row['nombre']}</b><br>Equipamiento: {row['equipamiento']}<br>Horario: {row['horario']}"
            elif tipo == "Fuentes":
                texto_popup = f"<b>{row['codigo']}</b><br>Fuente potable disponible."
            elif tipo == "Fuentes mascotas":
                texto_popup = f"<b>{row['codigo']}</b><br>Fuente para mascotas."
            elif tipo == "Centros de Salud":
                texto_popup = f"<b>{row['nombre']}</b><br>Descripción: {row['descripcion']}<br>Horario: {row['horario']}<br>Teléfono: {row['telefono']}"
            else:
                texto_popup = "Información no disponible."

            # Añadir el marcador al mapa
            folium.Marker(
                location=[row["latitud"], row["longitud"]],
                popup=folium.Popup(texto_popup, max_width=300),
                icon=folium.Icon(icon=icono, prefix="fa", color="blue")
            ).add_to(cluster)


    def generar_mapa(self):
        # Generamos el mapa de madrid
        mapa = folium.Map([40.428, -3.76], zoom_start=12)

        # Iterar sobre los datasets y generar capas en el mapa
        for tipo, df in self.dataframes.items():
            self.generar_mapa_tipo(mapa, df, tipo, self.iconos.get(tipo, "info-sign"))

        # Añadir control de capas para alternar entre ellas
        folium.LayerControl().add_to(mapa)

        return mapa