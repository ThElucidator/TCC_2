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

    # Method to execute an insert query
    def insert(self, tabela, campos, values):
        query = f"INSERT INTO {tabela} ({campos}) VALUES ({values})"
        self.sql.execute(query)
        self.cnx.commit()


# Creating a Dash app
app = dash.Dash("TCC_2")

# Defining the layout of the app
app.layout = html.Div(
    [  
        html.Div(
            [   
                html.Div(
                    [
                        html.H3("Situação de Bolsa"),
                        dcc.Checklist(
                            id="bolsa-filter",
                            options=[
                                {"label": "Sim", "value": "sim"},
                                {"label": "Não", "value": "nao"},
                            ],
                            value=["sim", "nao"],
                            style={"display": "inline-block", "width": "200px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.H3("Aproveitamento do Aluno"),
                        dcc.RangeSlider(0, 100, 20, value=[0, 100], id="nota-filter"),
                    ],
                    style={
                        "display": "inline-block",
                        "width": "250px",
                        "margin-right": "20px",
                    },
                ),
                html.Div(
                    [
                        html.H3("Situação de Trabalho"),
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
                    ]
                ),
                html.Div(
                    [
                        html.H3("Situação Civil"),
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
                    style={"display": "inline-block", "width": "200px"},
                ),
            ],
            style={"display": "flex"},
        ),
        html.Div([dcc.Graph(id="scatter-map")]),
    ]
)


# Defining a callback function for updating the scatter plot
@app.callback(
    Output("scatter-map", "figure"),
    [
        Input("bolsa-filter", "value"),
        Input("nota-filter", "value"),
        Input("trab-filter", "value"),
        Input("civ-filter", "value"),
    ],
)
def plot(bolsa_filter, nota_filter, trab_filter, civ_filter):
    # Creating an instance of the DB class
    db = DB()
    # Querying the database and filling in missing values with 'N/A'
    alunos_linhas = db.select("*", "alunos").fillna("N/A")

    alunos_linhas = alunos_linhas.query(f"bolsa in {bolsa_filter}")
    alunos_linhas = alunos_linhas.query(
        f"aproveitamento >= {nota_filter[0]} & aproveitamento <= {nota_filter[1]}"
    )
    alunos_linhas = alunos_linhas.query(f"situacaotrab in {trab_filter}")
    alunos_linhas = alunos_linhas.query(f"situacaocivil in {civ_filter}")

    # Creating the scatter plot
    fig = px.scatter_mapbox(
        alunos_linhas,
        hover_name="nome",
        hover_data=[
            "situacao",
            "bolsa",
            "aproveitamento",
            "situacaotrab",
            "situacaocivil",
            "descricao",
        ],
        lat="lat",
        lon="lon",
        color="situacao",
        zoom=9,
        width=900,
        height=600,
        title="Mapa da evasão de alunos",
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


