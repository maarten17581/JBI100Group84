from dash_extensions.enrich import DashProxy, MultiplexerTransform


app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()])
app.title = "JBI100 CreditVis"
