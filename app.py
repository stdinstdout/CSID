from shutil import ExecError
from dash import Input, Output, State, dcc, html, Dash
import dash_bootstrap_components as dbc

from extra_functions import parse_cols_name, parse_df_from_content
from clustering_functions import do_pipeline

app = Dash('csid-dash-app', 
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True)
app.title = 'CSID'

occ_card = [

    dbc.CardBody(
        [
            html.H5("Файл с данными", className="card-title"),
            dcc.Upload(id='occ-file-input', className='form-control',
                       children=[
                           html.Span('Выберите файл', id='occ-file-input-name')
                       ],
                       style={
                           'min-height': '38px'
                       }),
            dbc.FormText("Текст меолким шрифтом"),
        ],
    ),
    dbc.CardBody(
        [
            html.H5("Столбец с долготой - longitude", className="card-title"),
            dbc.Select(id='lon-select', placeholder="Выберите название колонки долготы"),
        ],
        className='pt-0'
    ),
    dbc.CardBody(
        [
            html.H5("Столбец с широтой - latitude", className="card-title"),
            dbc.Select(id='lat-select',placeholder="Выберите название колонки широты"),
        ],
        className='pt-0'
    ),
    dbc.CardBody(
        [
            html.H5("Название вида", className="card-title"),
            dbc.Input(id='species-name', type='text', placeholder="Введите названеи вида"),
        ],
        className='pt-0'
    ),
    dbc.CardBody(
        [
            html.H5("Расстояние до соседней точки", className="card-title"),
            dbc.Input(id='epsilon', type='number', placeholder="Введите расстояние до соседней точки"),
        ],
        className='pt-0'
    ),
]


app.layout = dbc.Container([

    html.H1('Коррекция пространственнной неравномерности данных', className='display-5 mt-5 mb-2'),

    dbc.Card(occ_card, color="primary", outline=True, className='mb-3'),

    dbc.Button("Скорректировать", id='start-btn', type='submit', className='w-100'),

    dcc.Download(id='download-result'),

    dbc.Alert([
        html.H4(className="alert-heading", id='alert-heading'),
        html.P(id='alert-body'),
    ], color="warning", duration=10000, is_open=False, id='alert', className='mt-3'),

])


# Вывод название столбцов из occ-file
@app.callback(Output('lat-select', 'options'),
              Output('lon-select', 'options'),
              Output('occ-file-input-name', 'children'),

              Input('occ-file-input', 'contents'),
              State('occ-file-input', 'filename'),
              prevent_initial_call=True)
def get_occ_file(contents, filename):
    col_names = parse_cols_name(contents, filename)
    
    return col_names, col_names, filename

# Clustering
@app.callback(Output('download-result', 'data'),

              Output('alert', 'is_open'),
              Output('alert-heading', 'children'),
              Output('alert-body', 'children'),

              Input('start-btn', 'n_clicks'),

              State('occ-file-input', 'contents'),
              State('occ-file-input', 'filename'),

              State('species-name', 'value'),
              State('epsilon', 'value'),

              State('lat-select', 'value'),
              State('lon-select', 'value'),
              prevent_initial_call = True)
def do_clustering(n_clicks, contents, filename, species_name, epsilon, lat, lon):

    try:
        df = parse_df_from_content(contents, filename)
        before_len = len(df)
    except Exception as ex:
        return None, True, 'Parse content error2', str(ex)
    try:
        df = do_pipeline(df, species_name, lon, lat, epsilon)
        after_len = len(df)
    except Exception as ex:
        return None, True, 'Custering Error', str(ex)

    try:
        return dcc.send_data_frame(df.to_csv, str(species_name)+".csv", index=False), True, 'Коррекция прошла успешно', \
        'Было ' + str(before_len) + ' точек | Стало ' + str(after_len) + ' точек.'
    except Exception as ex:
        return None, True, 'Downloading Error', str(ex)



if __name__ == "__main__":
    app.run_server(debug=True)