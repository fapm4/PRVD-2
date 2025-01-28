import folium
from folium import plugins
from dash import html
import pandas as pd
import os

class BusMap:
    def __init__(self):
        self.data = self._load_data()
        self.colors = self._setup_colors()
        
    def _load_data(self):
        """Cargar todos los archivos GTFS necesarios"""
        base_path = 'data/bus_interurbano'
        
        # Inicializar DataFrames vacíos
        all_stops = pd.DataFrame()
        all_routes = pd.DataFrame()
        all_trips = pd.DataFrame()
        all_stop_times = pd.DataFrame()
        
        # Buscar todas las subcarpetas
        subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        
        # Leer archivos de cada subcarpeta
        for subdir in subdirs:
            subdir_path = os.path.join(base_path, subdir)
            
            # Leer stops.txt si existe
            stops_path = os.path.join(subdir_path, 'stops.txt')
            if os.path.exists(stops_path):
                stops_df = pd.read_csv(stops_path)
                all_stops = pd.concat([all_stops, stops_df], ignore_index=True)
            
            # Leer routes.txt si existe
            routes_path = os.path.join(subdir_path, 'routes.txt')
            if os.path.exists(routes_path):
                routes_df = pd.read_csv(routes_path)
                all_routes = pd.concat([all_routes, routes_df], ignore_index=True)
            
            # Leer trips.txt si existe
            trips_path = os.path.join(subdir_path, 'trips.txt')
            if os.path.exists(trips_path):
                trips_df = pd.read_csv(trips_path)
                all_trips = pd.concat([all_trips, trips_df], ignore_index=True)
            
            # Leer stop_times.txt si existe
            stop_times_path = os.path.join(subdir_path, 'stop_times.txt')
            if os.path.exists(stop_times_path):
                stop_times_df = pd.read_csv(stop_times_path)
                all_stop_times = pd.concat([all_stop_times, stop_times_df], ignore_index=True)
        
        # Eliminar duplicados
        all_stops = all_stops.drop_duplicates()
        all_routes = all_routes.drop_duplicates()
        all_trips = all_trips.drop_duplicates()
        all_stop_times = all_stop_times.drop_duplicates()
        
        return {
            'stops': all_stops,
            'routes': all_routes,
            'trips': all_trips,
            'stop_times': all_stop_times
        }
    
    def _setup_colors(self):
        """Configurar colores para las rutas"""
        colores_diurnos = [
            '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF',
            '#00FFFF', '#FF8000', '#80FF00', '#00FF80', '#0080FF',
            '#8000FF', '#FF0080', '#FF4040', '#40FF40', '#4040FF'
        ]
        
        colores_nocturnos = [
            '#800000', '#008000', '#000080', '#808000', '#800080',
            '#008080', '#804000', '#408000', '#008040', '#004080',
            '#400080', '#800040', '#662222', '#226622', '#222266'
        ]
        
        route_colors = {}
        diurnas_index = 0
        nocturnas_index = 0
        
        # Obtener nombres únicos de ruta
        unique_route_names = self.data['routes']['route_short_name'].unique()
        
        # Asignar colores a cada ruta
        for route_name in unique_route_names:
            if str(route_name).startswith('N'):
                color = colores_nocturnos[nocturnas_index % len(colores_nocturnos)]
                nocturnas_index += 1
            else:
                color = colores_diurnos[diurnas_index % len(colores_diurnos)]
                diurnas_index += 1
            
            # Asignar el mismo color a todas las rutas con el mismo nombre
            route_ids = self.data['routes'][self.data['routes']['route_short_name'] == route_name]['route_id']
            for route_id in route_ids:
                route_colors[route_id] = color
        
        return route_colors
    
    def create_map(self):
        """Crear el mapa con todas las rutas y paradas"""
        # Crear el mapa base
        mapa_buses = folium.Map(
            location=[40.4168, -3.7038],
            zoom_start=11
        )
        
        # Diccionarios para almacenar las capas
        overlays = {
            "Líneas Diurnas": {},
            "Líneas Nocturnas": {}
        }
        
        # Agrupar los viajes por ruta
        grouped_trips = self.data['trips'].groupby('route_id')
        
        # Para cada ruta
        for route_id, trips in grouped_trips:
            color = self.colors.get(route_id, '#FF0000')
            route_name = self.data['routes'][self.data['routes']['route_id'] == route_id]['route_short_name'].iloc[0]
            
            # Crear una capa para esta línea
            feature_group = folium.FeatureGroup(name=f"Línea {route_name}")
            
            # Obtener un viaje representativo
            sample_trip = trips.iloc[0]
            
            # Obtener todas las paradas de este viaje en orden
            trip_stops = self.data['stop_times'][
                self.data['stop_times']['trip_id'] == sample_trip['trip_id']
            ].sort_values('stop_sequence')
            
            coordinates = []
            
            for _, stop_time in trip_stops.iterrows():
                stop = self.data['stops'][self.data['stops']['stop_id'] == stop_time['stop_id']].iloc[0]
                coordinates.append([stop['stop_lat'], stop['stop_lon']])
                
                # Crear contenido HTML para el popup
                popup_content = f"""
                <div style="width: 200px">
                    <h4 style="color:{color}">Línea {route_name}</h4>
                    <b>Parada:</b> {stop['stop_name']}<br>
                    <b>Hora:</b> {stop_time['arrival_time']}<br>
                    <b>Zona:</b> {stop.get('zone_id', 'N/A')}<br>
                    <b>Dirección:</b> {stop.get('stop_desc', 'N/A')}<br>
                </div>
                """
                
                # Agregar marcador para la parada
                folium.CircleMarker(
                    location=[stop['stop_lat'], stop['stop_lon']],
                    radius=5,
                    color=color,
                    fill=True,
                    fillOpacity=0.7,
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=stop['stop_name']
                ).add_to(feature_group)
            
            # Agregar la línea que conecta las paradas
            folium.PolyLine(
                coordinates,
                weight=2,
                color=color,
                opacity=0.8
            ).add_to(feature_group)
            
            # Añadir al diccionario correspondiente
            if str(route_name).startswith('N'):
                overlays["Líneas Nocturnas"][f"Línea {route_name}"] = feature_group
            else:
                overlays["Líneas Diurnas"][f"Línea {route_name}"] = feature_group
            
            # Añadir al mapa
            feature_group.add_to(mapa_buses)
        
        # Añadir el botón de selección
        select_button_html = """
        <div id='select-button' style='position: fixed; top: 10px; right: 50px; z-index: 999; background: white; padding: 10px; border-radius: 4px; box-shadow: 0 1px 5px rgba(0,0,0,0.4); margin-right: 320px;'>
            <button id='toggleButton' onclick='toggleAll()' style='padding: 5px 10px;'>Seleccionar todas</button>
        </div>

        <script>
        var allSelected = true;

        function toggleAll() {
            const checkboxes = document.querySelectorAll('.leaflet-control-layers-overlays input[type="checkbox"]');
            const button = document.getElementById('toggleButton');
            
            checkboxes.forEach(checkbox => {
                if (checkbox.checked !== !allSelected) {
                    checkbox.click();
                }
            });
            
            allSelected = !allSelected;
            button.textContent = allSelected ? 'Seleccionar todas' : 'Deseleccionar todas';
        }
        </script>
        """
        
        # Añadir el botón de selección al mapa
        mapa_buses.get_root().html.add_child(folium.Element(select_button_html))
        
        # Agregar el control de capas agrupadas
        plugins.GroupedLayerControl(
            groups={
                "Líneas Diurnas": overlays["Líneas Diurnas"],
                "Líneas Nocturnas": overlays["Líneas Nocturnas"]
            },
            exclusive_groups=False,
            collapsed=False
        ).add_to(mapa_buses)
        
        # Convertir a HTML para Dash
        return html.Iframe(
            srcDoc=mapa_buses._repr_html_(),
            style={'width': '100%', 'height': '800px', 'border': 'none'}
        )