import pandas as pd
import plotly.express as px

class MadridPollutionMap:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = self.load_data()
        self.columns_to_plot = ['PM10', 'NO_2', 'O_3', 'PM25', 'NOx']
        self.df_aggregated = self.aggregate_data()

    def load_data(self):
        return pd.read_csv(self.file_path)
    
    def aggregate_data(self):
        df_filtered = self.df[['station', 'lat', 'lon'] + self.columns_to_plot]
        return df_filtered.groupby(['station', 'lat', 'lon'])[self.columns_to_plot].mean().reset_index()
    
    def create_map(self):
        fig = px.density_mapbox(
            self.df_aggregated,
            lat='lat',
            lon='lon',
            z='PM10',  
            color_continuous_scale='Viridis',
            mapbox_style="carto-positron",
            title="Contaminación por contornos en el mapa"
        )
        
        dropdown_buttons = [
            dict(
                label=col,
                method='update',
                args=[
                    {'z': [self.df_aggregated[col]]},
                    {'coloraxis': {'colorbar': {'title': col}}}
                ]
            ) for col in self.columns_to_plot
        ]
        
        fig.update_layout(
            updatemenus=[dict(
                type='dropdown',
                direction='down',  
                x=1.00,  
                y=1.05, 
                xanchor='left',
                yanchor='top',
                showactive=True,
                buttons=dropdown_buttons
            )],
            title={
                'text': "Contaminación por contornos en el mapa",
                'x': 0.0, 
                'xanchor': 'left',
                'y': 0.95,  
                'yanchor': 'top'
            },
            mapbox_center_lat=40.4168, 
            mapbox_center_lon=-3.7038,
            mapbox_zoom=10,
            width=1000,
            height=800,
            coloraxis_colorbar={'title': 'PM10'}  
        )
        pollution_map = MadridPollutionMap('madrid_nuevo.csv')
        return fig
    
    def show_map(self):
        fig = self.create_map()
        fig.show()