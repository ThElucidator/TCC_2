# Importing the necessary modules
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from mysql import connector

# Defining a database class
class DB:
    # Initializing the class with a database connection and a cursor
    def __init__(self):
        self.cnx = connector.connect(user="root", database="tcc")
        self.sql = self.cnx.cursor()

    # Closing the connection when exiting the class
    def __exit__(self):
        self.sql.close()
        self.cnx.close()

    # Method to execute a select query, returning the result as a pandas DataFrame
    def select(self, campos, tabela, where=None):
        query = f"SELECT {campos} FROM {tabela}"

        if where:
            query += f" WHERE {where}"

        self.sql.execute(query)
        columns = self.sql.column_names
        rows = self.sql.fetchall()

        return pd.DataFrame(rows, columns=columns)

    # Method to rename columns in a table
    def rename(self, dataframe, mapping):
        renamed_df = dataframe.rename(columns=mapping)

        return renamed_df

# Creating a Dash app
app = dash.Dash("TCC_2")

# Defining the layout of the app
app.layout = html.Div(
    [
        html.H1("Mapa da Evasão de Alunos - IFNMG-TO", style={"display": "flex", "justify-content": "center", "align-items": "top", "height": "5vh"}),
        html.Div(
            [
                html.Div(
                    [
                        html.Button(
                            "Filtrar por Situação de Bolsa",
                            id="toggle-bolsa-filter",
                            n_clicks=0,
                            style={"margin-bottom": "25px"},
                        ),
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="bolsa-filter",
                                    options=[
                                        {"label": "Sim", "value": "sim"},
                                        {"label": "Não", "value": "nao"},
                                    ],
                                    value=["sim", "nao"],
                                    style={"display": "inline-block", "width": "200px"},
                                ),
                            ],
                            id="bolsa-filter-container",
                        ),
                    ]
                , style={"margin-right": "20px", "width": "15vw"}),
                html.Div(
                    [
                        html.Button(
                            "Filtrar por Aproveitamento do Aluno",
                            id="toggle-aproveitamento-filter",
                            n_clicks=0,
                            style={"margin-bottom": "50px"},
                        ),
                        html.Div(
                            [
                                dcc.RangeSlider(
                                    0, 100, 20, value=[0, 100], id="nota-filter"
                                ),
                            ],
                            id="aproveitamento-filter-container",
                        ),
                    ]
                , style={"margin-right": "100px", "width": "15vw"}),
                html.Div(
                    [
                        html.Button(
                            "Filtrar por Turma",
                            id="toggle-turma-filter",
                            n_clicks=0,
                            style={"margin-bottom": "20px"},
                        ),
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="turma-filter",
                                    options=[
                                        {"label": "2018", "value": 2018},
                                        {"label": "2019", "value": 2019},
                                        {"label": "2020", "value": 2020},
                                        {"label": "2021", "value": 2021},
                                    ],
                                    value=[2018, 2019, 2020, 2021],
                                    style={"display": "inline-block", "width": "200px", "margin-right": "20px"},
                                ),
                            ],
                            id="turma-filter-container",
                        ),
                    ]
                , style={"margin-right": "60px", "width": "15vw"}),
                html.Div(
                    [
                        html.Button(
                            "Filtrar por Situação de Trabalho",
                            id="toggle-trab-filter",
                            n_clicks=0,
                            style={"margin-bottom": "25px"},
                        ),
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="trab-filter",
                                    options=[
                                        {"label": "Trabalha", "value": "trabalha"},
                                        {"label": "Desempregado(a)", "value": "desempregado"},
                                        {"label": "Não Trabalha", "value": "nao trabalha"},
                                    ],
                                    value=["trabalha", "desempregado", "nao trabalha"],
                                    style={"display": "inline-block", "width": "200px", "margin-right": "20px"},
                                ),
                            ],
                            id="trab-filter-container",
                        ),
                    ]
                , style={"margin-right": "60px", "width": "15vw"}),
                html.Div(
                    [
                        html.Button(
                            "Filtrar por Situação Civil",
                            id="toggle-civ-filter",
                            n_clicks=0,
                            style={"margin-bottom": "20px"},
                        ),
                        html.Div(
                            [
                                dcc.Checklist(
                                    id="civ-filter",
                                    options=[
                                        {"label": "Separado(a)", "value": "separado(a)"},
                                        {"label": "Divorciado(a)", "value": "divorciado(a)"},
                                        {"label": "Casado(a)", "value": "casado(a)"},
                                        {"label": "Solteiro(a)", "value": "solteiro(a)"},
                                    ],
                                    value=[
                                        "separado(a)",
                                        "divorciado(a)",
                                        "casado(a)",
                                        "solteiro(a)",
                                    ],
                                ),
                            ],
                            id="civ-filter-container",
                        ),
                    ]
                , style={"width": "15vw"}),
            ],
            style={
                "display": "flex",
                "justify-content": "center",
                "align-items": "top",
                "height": "15vh",
            },
        ),
        html.Div(
            [dcc.Graph(id="scatter-map")],
            style={
                "display": "flex",
                "justify-content": "center",
                "align-items": "top",
                "height": "70vh",
                "border": "2px solid black",
                "border-radius": "10px",
            },
        ),
    ]
)


# Callbacks to toggle the visibility of each filter
@app.callback(
    Output("bolsa-filter-container", "style"),
    [Input("toggle-bolsa-filter", "n_clicks")],
)
def toggle_bolsa_filter(n_clicks):
    if n_clicks % 2 == 0:
        return {"display": "none"}
    else:
        return {"display": "block"}

@app.callback(
    Output("aproveitamento-filter-container", "style"),
    [Input("toggle-aproveitamento-filter", "n_clicks")],
)
def toggle_aproveitamento_filter(n_clicks):
    if n_clicks % 2 == 0:
        return {"display": "none"}
    else:
        return {"display": "block", "margin-left": "-50px"}

@app.callback(
    Output("turma-filter-container", "style"),
    [Input("toggle-turma-filter", "n_clicks")],
)
def toggle_turma_filter(n_clicks):
    if n_clicks % 2 == 0:
        return {"display": "none"}
    else:
        return {"display": "block"}

@app.callback(
    Output("trab-filter-container", "style"),
    [Input("toggle-trab-filter", "n_clicks")],
)
def toggle_trab_filter(n_clicks):
    if n_clicks % 2 == 0:
        return {"display": "none"}
    else:
        return {"display": "block"}


@app.callback(
    Output("civ-filter-container", "style"),
    [Input("toggle-civ-filter", "n_clicks")],
)
def toggle_civ_filter(n_clicks):
    if n_clicks % 2 == 0:
        return {"display": "none"}
    else:
        return {"display": "block"}


# Defining a callback function for updating the scatter plot
@app.callback(
    Output("scatter-map", "figure"),
    [
        Input("bolsa-filter", "value"),
        Input("nota-filter", "value"),
        Input("turma-filter", "value"),
        Input("trab-filter", "value"),
        Input("civ-filter", "value"),
    ],
)
def plot(bolsa_filter, nota_filter,turma_filter, trab_filter, civ_filter):
    # Creating an instance of the DB class
    db = DB()
    # Querying the database and filling in missing values with 'N/A'
    alunos_linhas = db.select("*", "alunos").fillna("N/A")

    if len(bolsa_filter) > 0:
        alunos_linhas = alunos_linhas.query(f"bolsa in {bolsa_filter}")
    else:
        alunos_linhas = alunos_linhas.sample(0)

    if len(nota_filter) > 0:
        alunos_linhas = alunos_linhas.query(
            f"aproveitamento >= {nota_filter[0]} & aproveitamento <= {nota_filter[1]}"
        )
    else:
        alunos_linhas = alunos_linhas.sample(0)

    if len(turma_filter) > 0:
        alunos_linhas = alunos_linhas.query(f"turma in {turma_filter}")
    else:
        alunos_linhas = alunos_linhas.sample(0)

    if len(trab_filter) > 0:
        alunos_linhas = alunos_linhas.query(f"situacaotrab in {trab_filter}")
    else:
        alunos_linhas = alunos_linhas.sample(0)

    if len(civ_filter) > 0:
        alunos_linhas = alunos_linhas.query(f"situacaocivil in {civ_filter}")
    else:
        alunos_linhas = alunos_linhas.sample(0)

    # renaming columns to visualization
    alunos_linhas = db.rename(
        alunos_linhas,
        {
            "nome": "Nome",
            "situacao": "Situação",
            "bolsa": "Bolsa",
            "aproveitamento": "Aproveitamento",
            "turma": "Turma",
            "situacaotrab": "Situação de Trabalho",
            "situacaocivil": "Situação Civil",
            "descricao": "Descrição",
            "lat": "Latitude",
            "lon": "Longitude",
        },
    )

    # Creating the scatter plot
    if alunos_linhas.empty:
        fig = px.scatter_mapbox(
            alunos_linhas,
            lat=[],
            lon=[],
            zoom=9.6,
            width=1800,
            height=620,
        )
    else:
        fig = px.scatter_mapbox(
            alunos_linhas,
            hover_name="Nome",
            hover_data=[
                "Situação",
                "Bolsa",
                "Aproveitamento",
                "Turma",
                "Situação de Trabalho",
                "Situação Civil",
                "Descrição",
            ],
            lat="Latitude",
            lon="Longitude",
            color="Situação",
            zoom=9.6,
            width=1800,
            height=620,
        )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center_lat=-17.85,
        mapbox_center_lon=-41.50,
        margin={"r": 0, "t": 50, "l": 0, "b": 10},
    )

    return fig


# Running the app
if __name__ == "__main__":
    app.run_server(debug=True)
