import folium

def add_tourist_spots(m):
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

	for spot in tourist_spots:
		folium.Marker(
			location=[spot["lat"], spot["lon"]],
			popup=folium.Popup(f"<b>{spot['name']}</b>", max_width=300),
			icon=folium.Icon(color='green', icon='info-sign')
		).add_to(m)

	folium.LayerControl().add_to(m)
	
def add_borders(gdf, map_obj):
	for _, row in gdf.iterrows():
		folium.GeoJson(
			row['geometry'],
			style_function=lambda x: {
				'fillColor': 'transparent',
				'color': 'black',
				'weight': 1,
				'fillOpacity': 0.0
			},
			popup=folium.Popup(
				f"<b>Barrio</b>: {row['neighbourhood']}",
				max_width=300
			)
		).add_to(map_obj)