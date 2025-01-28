import folium
from folium import plugins
import pandas as pd
from scipy.spatial.distance import cdist
import numpy as np

class CercaniasMap:
    def __init__(self):
        self.data = self._load_data()
        self.stations_by_line = self._setup_stations()
        self.colors = self._setup_colors()
        
    def _load_data(self):
        """Cargar datos de Cercanías"""
        df_stops = pd.read_csv("data/cercanias/stops.txt")
        df_routes = pd.read_csv("data/cercanias/routes.txt")
        return {'stops': df_stops, 'routes': df_routes}
    
    def _setup_stations(self):
        """Configurar estaciones por línea"""
        return {
            'C1': [
                'PRÍNCIPE PÍO', 'PIRÁMIDES', 'DELICIAS', 'MÉNDEZ ÁLVARO', 'ATOCHA', 
                'RECOLETOS', 'NUEVOS MINISTERIOS', 'CHAMARTÍN', 'FUENTE DE LA MORA',
                'VALDEBEBAS', 'AEROPUERTO T4'
            ],
            'C2': [
                'GUADALAJARA', 'AZUQUECA', 'MECO', 'ALCALÁ DE HENARES UNIVERSIDAD',
                'ALCALÁ DE HENARES', 'LA GARENA', 'SOTO DEL HENARES', 'TORREJÓN DE ARDOZ',
                'SAN FERNANDO', 'COSLADA', 'VICÁLVARO', 'SANTA EUGENIA', 'VALLECAS',
                'ATOCHA', 'RECOLETOS', 'NUEVOS MINISTERIOS', 'CHAMARTÍN'
            ],
            'C3': [
                'ARANJUEZ', 'CIEMPOZUELOS', 'VALDEMORO', 'PINTO', 'GETAFE INDUSTRIAL',
                'VILLAVERDE BAJO', 'ATOCHA', 'SOL', 'NUEVOS MINISTERIOS', 'CHAMARTÍN'
            ],
            'C4A': [
                'PARLA', 'GETAFE CENTRO', 'VILLAVERDE ALTO', 'ATOCHA', 'SOL', 
                'NUEVOS MINISTERIOS', 'CHAMARTÍN', 'CANTOBLANCO UNIVERSIDAD', 
                'UNIVERSIDAD P. COMILLAS', 'VALDELASFUENTES', 'ALCOBENDAS-S.S. DE LOS REYES'
            ],
            'C4B': [
                'PARLA', 'GETAFE CENTRO', 'VILLAVERDE ALTO', 'ATOCHA', 'SOL',
                'NUEVOS MINISTERIOS', 'CHAMARTÍN', 'CANTOBLANCO UNIVERSIDAD',
                'EL GOLOSO', 'TRES CANTOS', 'COLMENAR VIEJO'
            ],
            'C5': [
                'MÓSTOLES EL SOTO', 'MÓSTOLES', 'LAS RETAMAS', 'ALCORCÓN',
                'SAN JOSÉ DE VALDERAS', 'CUATRO VIENTOS', 'LAGUNA', 'EMBAJADORES',
                'ATOCHA', 'VILLAVERDE ALTO', 'ZARZAQUEMADA', 'LEGANÉS', 'FUENLABRADA',
                'LA SERNA', 'HUMANES'
            ],
            'C7': [
                'ALCALÁ DE HENARES', 'TORREJÓN DE ARDOZ', 'SAN FERNANDO', 'COSLADA',
                'VICÁLVARO', 'SANTA EUGENIA', 'VALLECAS', 'ATOCHA', 'NUEVOS MINISTERIOS',
                'CHAMARTÍN', 'PRÍNCIPE PÍO'
            ],
            'C8': [
                'GUADALAJARA', 'ALCALÁ DE HENARES', 'TORREJÓN DE ARDOZ', 'ATOCHA',
                'CHAMARTÍN', 'PITIS', 'LAS ROZAS', 'TORRELODONES', 'GALAPAGAR-LA NAVATA',
                'VILLALBA', 'CERCEDILLA'
            ],
            'C9': [
                'CERCEDILLA', 'PUERTO NAVACERRADA', 'COTOS'
            ],
            'C10': [
                'VILLALBA', 'TORRELODONES', 'LAS ROZAS', 'PITIS', 'PRÍNCIPE PÍO',
                'ATOCHA', 'RECOLETOS', 'NUEVOS MINISTERIOS', 'CHAMARTÍN', 'FUENTE DE LA MORA',
                'VALDEBEBAS', 'AEROPUERTO T4'
            ]
        }
    
    def _setup_colors(self):
        """Configurar colores de las líneas"""
        colores_linea = {}
        for _, route in self.data['routes'].iterrows():
            if pd.notna(route['route_color']):
                colores_linea[route['route_short_name']] = f"#{route['route_color']}"
            else:
                # Para C4A y C4B usamos colores específicos
                if route['route_short_name'] == 'C4A':
                    colores_linea[route['route_short_name']] = '#996633'  # Marrón claro
                elif route['route_short_name'] == 'C4B':
                    colores_linea[route['route_short_name']] = '#664422'  # Marrón oscuro
        return colores_linea
    
    def _order_coordinates(self, coordinates):
        """Ordenar coordenadas para conectar estaciones cercanas"""
        if len(coordinates) <= 2:
            return coordinates
        
        ordered = [coordinates[0]]
        remaining = coordinates[1:]
        
        while remaining:
            last_point = np.array([ordered[-1]])
            remaining_points = np.array(remaining)
            distances = cdist(last_point, remaining_points).flatten()
            nearest_idx = np.argmin(distances)
            ordered.append(remaining[nearest_idx])
            remaining.pop(nearest_idx)
        
        return ordered
    
    def create_map(self):
        """Crear el mapa de Cercanías"""
        # Crear el mapa base
        mapa_cercanias = folium.Map(
            location=[40.4168, -3.7038],
            zoom_start=11
        )
        
        # Procesar cada línea
        for route_name, stations in self.stations_by_line.items():
            line_group = folium.FeatureGroup(name=f'Línea {route_name}')
            color = self.colors[route_name]
            
            # Lista para almacenar las coordenadas de las estaciones de esta línea
            line_coordinates = []
            
            # Filtramos las estaciones que pertenecen a esta línea
            for _, stop in self.data['stops'].iterrows():
                if stop['location_type'] == 0:  # Solo paradas, no estaciones padre
                    if any(station in stop['stop_name'].upper() for station in stations):
                        # Añadimos las coordenadas para la línea
                        line_coordinates.append([stop['stop_lat'], stop['stop_lon']])
                        
                        # Creamos el marcador para la estación
                        folium.CircleMarker(
                            location=[stop['stop_lat'], stop['stop_lon']],
                            radius=8,
                            popup=f"""
                                <b>{stop['stop_name']}</b><br>
                                {stop['stop_desc']}<br>
                                Zona: {stop['zone_id']}
                            """,
                            color=color,
                            fill=True,
                            fill_color=color,
                            fill_opacity=0.2,
                            weight=2,
                            tooltip=stop['stop_name']
                        ).add_to(line_group)
            
            # Ordenamos las coordenadas y dibujamos las líneas
            if len(line_coordinates) > 1:
                ordered_coordinates = self._order_coordinates(line_coordinates)
                folium.PolyLine(
                    locations=ordered_coordinates,
                    weight=3,
                    color=color,
                    opacity=0.8
                ).add_to(line_group)
            
            line_group.add_to(mapa_cercanias)
        
        # Añadir control de capas
        folium.LayerControl(collapsed=False).add_to(mapa_cercanias)
        
        # Añadir leyenda
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; 
                    left: 50px; 
                    width: 150px;
                    height: auto;
                    z-index: 1000;
                    background-color: white;
                    padding: 10px;
                    border-radius: 5px;
                    border: 2px solid grey;
                    font-size: 14px;">
            <p style="margin-bottom: 10px;"><strong>Líneas Cercanías</strong></p>
        '''
        
        for route_name, color in self.colors.items():
            legend_html += f'''
            <div style="margin-bottom: 5px;">
                <span style="color: {color}">●</span> {route_name}
            </div>
            '''
        
        legend_html += '</div>'
        mapa_cercanias.get_root().html.add_child(folium.Element(legend_html))
        
        return mapa_cercanias