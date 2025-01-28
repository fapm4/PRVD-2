import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from dash import html, dcc

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