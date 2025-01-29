import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from dash import html, dcc
import folium
from folium.plugins import MarkerCluster

class CrimeVisualization:
    def __init__(self, crime_data, gdf):
        self.crimes_data = crime_data
        self.gdf = gdf

    def get_all_graphs(self):
        numeric_columns = self.crimes_data.select_dtypes(include=['int64', 'float64'])

        correlation_matrix = numeric_columns.corr()
        fig_corr = px.imshow(correlation_matrix, text_auto=True, title="Matriz de Correlación entre Tipos de Incidentes")
        fig_corr.show()

        fig1 = px.bar(
            self.crimes_data,
            x="DISTRITOS",
            y=["RELACIONADAS CON LAS PERSONAS", "RELACIONADAS CON EL PATRIMONIO",
            "POR TENENCIA DE ARMAS", "POR TENENCIA DE DROGAS", "POR CONSUMO DE DROGAS"],
            title="Distribución de incidentes por distrito",
            labels={"value": "Número de incidentes", "variable": "Tipo de incidente"},
            barmode="group"
        )

        incident_totals = self.crimes_data[
            ["RELACIONADAS CON LAS PERSONAS", "RELACIONADAS CON EL PATRIMONIO",
            "POR TENENCIA DE ARMAS", "POR TENENCIA DE DROGAS", "POR CONSUMO DE DROGAS"]
        ].sum().reset_index()
        incident_totals.columns = ["Tipo de incidente", "Total"]

        fig2 = px.pie(
            incident_totals,
            names="Tipo de incidente",
            values="Total",
            title="Proporción de incidentes por tipo"
        )

        self.crimes_data["TOTAL INCIDENTES"] = self.crimes_data[
            ["RELACIONADAS CON LAS PERSONAS", "RELACIONADAS CON EL PATRIMONIO",
            "POR TENENCIA DE ARMAS", "POR TENENCIA DE DROGAS", "POR CONSUMO DE DROGAS"]
        ].sum(axis=1)
        top_districts = self.crimes_data.nlargest(3, "TOTAL INCIDENTES")

        fig3 = px.bar(
            top_districts,
            x="DISTRITOS",
            y=["RELACIONADAS CON LAS PERSONAS", "RELACIONADAS CON EL PATRIMONIO",
            "POR TENENCIA DE ARMAS", "POR TENENCIA DE DROGAS", "POR CONSUMO DE DROGAS"],
            title="Distribución de incidentes en los 3 distritos con más incidentes",
            labels={"value": "Número de incidentes", "variable": "Tipo de incidente"},
            barmode="stack"
        )

        return html.Div([
            dcc.Graph(figure=fig_corr),
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2),
            dcc.Graph(figure=fig3)
        ])
    
    def get_map(self, crimen):
        if self.gdf.crs is None or self.gdf.crs.to_string() != "EPSG:4326":
            self.gdf = self.gdf.to_crs(epsg=4326)

        self.gdf["TOTAL INCIDENTES FILTRADOS"] = self.crimes_data[crimen]

        self.gdf["centroid"] = self.gdf.geometry.centroid
        self.gdf["latitude"] = self.gdf["centroid"].y
        self.gdf["longitude"] = self.gdf["centroid"].x

        map_center = [
            self.gdf["latitude"].mean(),
            self.gdf["longitude"].mean()
        ]

        folium_map = folium.Map(location=map_center, zoom_start=12)

        for _, row in self.gdf.iterrows():
            if not (row["latitude"] and row["longitude"]) or row["TOTAL INCIDENTES FILTRADOS"] <= 0:
                continue
            
            scaled_radius = max(row["TOTAL INCIDENTES FILTRADOS"], 1) * 10

            folium.Circle(
                location=[row["latitude"], row["longitude"]],
                radius=scaled_radius,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=0.5,
                popup=(
                    f"<b>Distrito:</b> {row.get('neighbourhood_group', 'Desconocido')}<br>"
                    f"<b>Total {crimen}:</b> {row['TOTAL INCIDENTES FILTRADOS']}"
                )
            ).add_to(folium_map)

        return folium_map