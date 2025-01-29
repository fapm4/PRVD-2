import folium
from folium.plugins import MarkerCluster
from folium import Popup, GeoJson, GeoJsonTooltip, GeoJsonPopup, FeatureGroup, CircleMarker, PolyLine, LayerControl, Icon
import pandas as pd
import json
import random
from pyproj import Proj, Transformer


class MadridMap:
    def __init__(self, airbnb_path, noise_path, metro_path, geojson_path):
        self.airbnb_data = pd.read_csv(airbnb_path)
        self.noise_data = pd.read_csv(noise_path, delimiter=';')
        self.metro_data = pd.read_csv(metro_path, quotechar='"')
        self.geojson_path = geojson_path
        self.map = folium.Map(location=[40.4168, -3.7038], zoom_start=12)
        self._convert_noise_coordinates()
        self._process_metro_data()
        self.line_colors = self._setup_metro_colors()

    def _convert_noise_coordinates(self):
        """Convertir coordenadas de ruido de ETRS89 a lat/lon"""
        proj_etrs89 = Proj(proj='utm', zone=30, ellps='WGS84')
        proj_latlon = Proj(proj='latlong', datum='WGS84')
        transformer = Transformer.from_proj(proj_etrs89, proj_latlon)

        def convert(x, y):
            lon, lat = transformer.transform(x, y)
            return lat, lon

        self.noise_data['Latitude'], self.noise_data['Longitude'] = zip(
            *self.noise_data.apply(lambda row: convert(row['X (ETRS89)'], row['Y (ETRS89)']), axis=1))

    def _process_metro_data(self):
        """Обработка координат метро"""
        self.metro_data['Longitude'] = self.metro_data['Longitude'].str.replace(',', '.').astype(float)
        self.metro_data['Latitude'] = self.metro_data['Latitude'].str.replace(',', '.').astype(float)

    def _setup_metro_colors(self):
        """Назначить цвета линиям метро"""
        return {
            'Linea 1': '#2B7CE9',
            'Linea 2': '#E6343C',
            'Linea 3': '#FFD700',
            'Linea 4': '#8B4513',
            'Linea 5': '#4CAF50',
            'Linea 6': '#808080',
            'Linea 7': '#FF8C00',
            'Linea 8': '#FFC0CB',
            'Linea 9': '#800080',
            'Linea 10': '#000080',
            'Linea 11': '#90EE90',
            'Linea 12': '#DAA520'
        }

    def _classify_noise(self, laeq):
        """Классифицировать уровень шума"""
        if laeq < 60:
            return 'bajo', 'green'
        elif 60 <= laeq < 70:
            return 'medio', 'orange'
        else:
            return 'alto', 'red'

    def add_airbnb_markers(self, selected_amenities):
        """Добавить маркеры Airbnb"""
        feature_group = FeatureGroup(name="Selected Amenities").add_to(self.map)
        marker_cluster = MarkerCluster().add_to(feature_group)

        def get_marker_color(price):
            if price < 100:
                return "green"
            elif price < 300:
                return "orange"
            else:
                return "red"

        for _, item in self.airbnb_data.iterrows():
            amenities = item["Amenities"]
            price = item["Price"]
            property_type = item["Property Type"]

            if isinstance(amenities, str):
                amenities = amenities.split(',')
            else:
                continue

            if all(amenity in amenities for amenity in selected_amenities):
                popup_content = f"""
                    <b>{item['Name']}</b><br>
                    <b>Price:</b> €{price}<br>
                    <b>Property Type:</b> {property_type}<br>
                    <b>Amenities:</b> {', '.join(amenities)}
                """
                folium.Marker(
                    location=[item["Latitude"], item["Longitude"]],
                    popup=Popup(popup_content),
                    icon=Icon(color=get_marker_color(price), icon="info-sign")
                ).add_to(marker_cluster)

    def add_noise_markers(self):
        """Добавить маркеры уровня шума"""
        self.noise_data['nivel'], self.noise_data['color'] = zip(*self.noise_data['LAEQ'].apply(self._classify_noise))

        for _, row in self.noise_data.iterrows():
            if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
                CircleMarker(
                    location=(row['Latitude'], row['Longitude']),
                    radius=20,
                    color=row['color'],
                    fill=True,
                    fill_color=row['color'],
                    fill_opacity=0.3,
                    popup=f"Nivel de ruido: {row['nivel']} ({row['LAEQ']} dB) en {row['tipo']}"
                ).add_to(self.map)

    def add_metro_lines(self):
        """Добавить линии метро"""
        feature_groups_metro = {line: FeatureGroup(name=line) for line in self.metro_data['Line'].unique()}

        for _, row in self.metro_data.iterrows():
            CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=5,
                color=self.line_colors.get(row['Line'], 'gray'),
                weight=2,
                opacity=1,
                fill=True,
                fill_color=self.line_colors.get(row['Line'], 'gray'),
                fill_opacity=0.4,
                popup=f"{row['Station']} ({row['Line']})"
            ).add_to(feature_groups_metro[row['Line']])

        for i in range(len(self.metro_data) - 1):
            start_station = self.metro_data.iloc[i]
            end_station = self.metro_data.iloc[i + 1]

            if start_station['Line'] == end_station['Line']:
                PolyLine(
                    locations=[[start_station['Latitude'], start_station['Longitude']],
                               [end_station['Latitude'], end_station['Longitude']]],
                    color=self.line_colors.get(start_station['Line'], 'gray'),
                    weight=4,
                    opacity=0.6
                ).add_to(feature_groups_metro[start_station['Line']])

        for group in feature_groups_metro.values():
            group.add_to(self.map)

    def add_neighbourhoods(self):
        """Добавить районы из GeoJSON"""
        with open(self.geojson_path, encoding="utf8") as f:
            geojson_data = json.load(f)

        def random_color():
            return f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.5)"

        GeoJson(
            geojson_data,
            style_function=lambda feature: {
                'fillColor': random_color(),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5
            },
            tooltip=GeoJsonTooltip(fields=['neighbourhood', 'neighbourhood_group']),
            popup=GeoJsonPopup(fields=['neighbourhood', 'neighbourhood_group'])
        ).add_to(self.map)

    def create_map(self, selected_amenities):
        """Создать карту с метками"""
        self.add_airbnb_markers(selected_amenities)
        self.add_noise_markers()
        self.add_metro_lines()
        self.add_neighbourhoods()
        LayerControl().add_to(self.map)
        return self.map


# Использование класса
selected_amenities = ["TV", "Wireless Internet"]

madrid_map = MadridMap(
    airbnb_path="filtered_airbnb_listings.csv",
    noise_path="ruido.csv",
    metro_path="metro.csv",
    geojson_path="neighbourhoods.geojson"
).create_map(selected_amenities)
