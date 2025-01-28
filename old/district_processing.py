from dash import html, dcc
import numpy as np
import plotly.express as px
import folium
from general_purpose import add_tourist_spots, add_borders
from folium.plugins import HeatMap

def update_stats_graph(gdf, distrito, listings):
	df_filtered = listings[listings['neighbourhood_group'] == distrito]
	avg_price = df_filtered['price'].mean()
	avg_min_nights = df_filtered['minimum_nights'].mean()
	avg_n_listings = df_filtered.shape[0]

	data = html.Div([
		html.H4(f'Estadísticas para el distrito {distrito}', style={'color': 'white'}),
		html.P(f'Precio promedio: {avg_price:.2f}€', style={'color': 'white'}),
		html.P(f'Número promedio de noches mínimas: {avg_min_nights:.2f}', style={'color': 'white'}),
		html.P(f'Número de listados: {avg_n_listings}', style={'color': 'white'})
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
	return html.Div([
		data,
		dcc.Graph(figure=fig_violin),
		dcc.Graph(figure=fig_bar),
		dcc.Graph(figure=fig_hist)
	])

def update_heatmap_graph(gdf, distrito, listings):
	df_filtered = listings[listings['neighbourhood_group'] == distrito]
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
		radius=8,
		max_zoom=13
	).add_to(m)


	add_borders(gdf, m)
	add_tourist_spots(m)

	map_html = m._repr_html_()

	return html.Iframe(
		srcDoc=map_html,
		style={
			"width": "100%",
			"height": "600px",
			"border": "none"
		}
	)
	
