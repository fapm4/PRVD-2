from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import pandas as pd

from components.metro_map import MetroMap
from components.bus_map import BusMap
from components.layout import Layout

class TransportApp:
    def __init__(self):
        self.app = Dash(__name__)
        
        # Inicializar componentes
        self.metro_map = MetroMap()
        self.bus_map = BusMap()
        self.layout = Layout()
        
        # Configurar layout principal
        self.app.layout = self.layout.create_layout()
        
        # Configurar callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        @self.app.callback(
            Output('content-container', 'children'),
            Input('tab-selector', 'value')
        )
        def update_content(selected_tab):
            if selected_tab == 'metro':
                return self.metro_map.create_map()
            elif selected_tab == 'bus':
                return self.bus_map.create_map()
            return html.Div("Selecciona una visualización")
    
    def run(self):
        self.app.run_server(debug=True)

if __name__ == '__main__':
    app = TransportApp()
    app.run()