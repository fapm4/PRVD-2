from dash import html, dcc

class Layout:
    def create_layout(self):
        return html.Div([
            html.H1("Visualización de Transporte de Madrid"),
            
            dcc.Tabs(id='tab-selector', value='metro', children=[
                dcc.Tab(label='Metro', value='metro'),
                dcc.Tab(label='Bus', value='bus'),
            ]),
            
            html.Div(id='content-container')
        ])