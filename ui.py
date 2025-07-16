import requests

from utils import mathjax_utils as mu
from utils.logger_config import setup_logger

import dash 
from dash import html, dcc, Dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc 
from dash import dash_table
from dash import callback_context
from flask import Flask

import time

import pandas as pd

import os  
import base64

# Endpoints of FAST API
UPLOAD_ENDPOINT = "http://127.0.0.1:8000/upload-pdf/"
EXTRACTION_ENDPOINT = "http://127.0.0.1:8000/extract-data/"
RAG_ENDPOINT = "http://127.0.0.1:8000/query-document/"
DELETE_ENDPOINT = "http://127.0.0.1:8000/delete-file/"

logger = setup_logger(name="frontend", log_file="logs/ui.log")
logger.info("Starting main application")

# dash_app = dash.Dash(__name__, 
#                      requests_pathname_prefix="/app/",
#                      routes_pathname_prefix="/app/",
#                      external_stylesheets=[dbc.themes.CYBORG])
# mu.inject_mathjax_index(dash_app)
# dash_app.title = "EOI/RFP Assistant"


# Check and create a pdf upload directory
UPLOAD_DIRECTORY = "./uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


# Creaate a layout of Dash app.
def create_dash_app():
    dash_app = Dash(
        __name__, 
        # routes_pathname_prefix="/rag/",
        requests_pathname_prefix="/rag/",
        # assets_url_path="/rag/assets",
        external_stylesheets=[dbc.themes.CYBORG]
    )
    mu.inject_mathjax_index(dash_app)
    dash_app.title = "EOI/RFP Assistant"

    dash_app.layout = dbc.Container(
        fluid=True,
        style={
            "height" : "100%",
            "width" : "100%",
            "padding" : "20px",
            "backgroundColor" : "#041720",
        },

        children=[
            # Blank Row 
            dbc.Row(style={"height": "100px"}),

            # Content Row
            dbc.Row(
                # Divide this row into two columns
                children=[
                    # Column 1: left Column 
                    dbc.Col(
                        # Divide this column into two rows 
                        children=[
                            # row 1 for the upload and display document
                            dbc.Row(
                                # Divide this row into the Two columns
                                children = [
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    dcc.Upload(
                                                        id="upload_eoi",
                                                        children=html.Div(
                                                            [
                                                                html.H5(
                                                                    "Upload EOI/RFP", 
                                                                    style=
                                                                    {
                                                                        "color": "#909097",
                                                                        "fontFamily": "Roboto, sans-serif",
                                                                        "textAlign": "center",
                                                                        # "marginBottom": "5px"
                                                                    }
                                                                ),
                                                                html.Img(
                                                                    src="/rag/assets/pdf_upload.jpg",
                                                                    style=
                                                                    {
                                                                        "height": "70px",
                                                                        "width": "80px",
                                                                        "cursor": "pointer",
                                                                        "marginBottom": "10px",
                                                                        "borderRadius": "4px",
                                                                    }
                                                                ),
                                                                html.Div(
                                                                    [
                                                                        "Drag and Drop or ",
                                                                        html.A(
                                                                            "Select file", 
                                                                            style=
                                                                            {
                                                                            'color': "#6FA1FF",
                                                                            "textDecoration": "underline"
                                                                            }
                                                                            )
                                                                    ], style=
                                                                        {
                                                                            "fontSize": "12px",
                                                                            "textAlign": "center"
                                                                        }
                                                                ),        
                                                                html.Div(
                                                                    [
                                                                        html.Div(id="upload_status", 
                                                                            style=
                                                                            {
                                                                                "textAlign": "left", 
                                                                                "fontFamily": "Roboto, sans-serif", 
                                                                                "fontSize": "9px", "margin": "10px"
                                                                            }
                                                                        ),
                                                                        dcc.Interval(
                                                                            id="message_timer", 
                                                                            interval=10 * 1000,
                                                                            n_intervals=0, 
                                                                            disabled=True
                                                                        )
                                                                    ],

                                                                )
                                                            ], 
                                                            style=
                                                            {
                                                                "display": "flex",
                                                                "flexDirection": "column",
                                                                "alignItems": "center",
                                                                "justifyContent": "center",
                                                                "height": "100%",
                                                                "width": "100%"
                                                            }
                                                        ), 
                                                    ),        
                                                ],
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "100%",
                                                "backgroundColor": "#203567",
                                                "border": "1px solid #404040",
                                                "padding": "20px",
                                                "margin": "20px",
                                                "marginBottom": "15px"
                                            }
                                        ), className="card-stack-gap", # See styles.css for formatting
                                        xs=12, sm=12, md=7, lg=7, xl=7
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    dcc.Interval(
                                                        id="interval-check-files",
                                                        interval=3000,
                                                        n_intervals=0
                                                    ),
                                                    html.H6(
                                                        "Select your document", 
                                                        style=
                                                        {
                                                            "color": "#909097", 
                                                            "fontFamily":"Roboto, sans-serif"
                                                        }
                                                    ),
                                                    dcc.Interval(id="initial-load-trigger", n_intervals=0, max_intervals=1),
                                                    dcc.RadioItems(
                                                        id="select_document",
                                                        options=[],
                                                        style=
                                                        {
                                                            'font-size': '10px',          
                                                            'color': 'grey',           
                                                            'padding': '5px',            
                                                            'margin': '10px 0', 
                                                            "whiteSpace": "normal",
                                                            "overflowWrap": "break-word",
                                                            "wordBreak": "break-word"           
                                                        },
                                                        labelStyle=
                                                        {
                                                            'display': 'flex', 
                                                            'marginBottom': "5px", 
                                                            'gap': '8px', 
                                                            "alignItems": 'center'},
                                                        inputStyle=
                                                        {
                                                            'margin-right': '10px', 
                                                            'transform':'scale(0.6)'
                                                        }
                                                    ), 
                                                    dbc.Button(
                                                        "x", id="delete_file", n_clicks=0,
                                                        style={"display": "none"} 
                                                    )
                                                ],
                                            ),
                                            style=
                                            {
                                                "width": "100%",
                                                "height": "100%",
                                                "backgroundColor": "#203567",
                                                "border": "1px solid #404040",
                                                "borderRadius": "4px", 
                                                "padding": "25px 0px 0px 0px",
                                                "margin": "20px 20px 0px 20px"
                                            }
                                        ),  xs=12, sm=12, md=5, lg=5, xl=5,  
                                    )
                                ]

                            ),             
                            # Row for the extract data section
                            dbc.Row(
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5(
                                                    "Extract Data", 
                                                    style=
                                                    {
                                                        "color": "#909097", 
                                                        "margin": "15px", 
                                                        "fontFamily": "Roboto, sans-serif"
                                                    }
                                                ),
                                                dcc.Dropdown(
                                                    id="dropdown", 
                                                    options=
                                                    [
                                                        {'label':'procurement', 'value': "procurement"},
                                                        {"label": 'key dates', 'value': "keydates"},
                                                        {"label": "contact", 'value': "contact"},
                                                        {"label": "submission", 'value': "submission"},
                                                        {"label": "project", 'value': "project"},
                                                    ], 
                                                    placeholder="Select a theme",
                                                    style=
                                                    {
                                                        'width': "59%",
                                                        "margin": "20px 5px",
                                                        'padding': '5px',
                                                        "color":"#222121"
                                                    },
                                                ),
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            dbc.Row(
                                                                # Put save csv iumage here
                                                                html.Div(
                                                                    html.Div(id="img-download-manager",
                                                                            children=[
                                                                                html.Img(
                                                                                    id="img-download",
                                                                                    src="/rag/assets/csv.png",
                                                                                    style=
                                                                                    {
                                                                                        "height": "30px", 
                                                                                        "width": "40px", 
                                                                                        "cursor": "pointer",
                                                                                    },
                                                                                    n_clicks=0
                                                                                ), 
                                                                                dcc.Download(id="download-dataframe-csv"),
                                                                            ], style={"textAlign": "right"},
                                                                            )         
                                                                ),
                                                                
                                                            ),
                                                            dbc.Row(
                                                                dcc.Loading(
                                                                    id="loading_table", 
                                                                    type="circle",
                                                                    children=
                                                                    [
                                                                        # Put dash table here 
                                                                        dash_table.DataTable(
                                                                            id="data_table",
                                                                            editable=True,
                                                                            style_table=
                                                                            {
                                                                                "overflowX": "auto", 
                                                                                "margin": "40px 0px 10px 10px",
                                                                                'backgroundColor': 'transparent'
                                                                            },
                                                                            style_header=
                                                                            {
                                                                                "backgroundColor": 'transparent', 
                                                                                "color": "white"
                                                                            },
                                                                            style_cell=
                                                                            {
                                                                                "backgroundColor": 'transparent', 
                                                                                "color": "#CEC3C3", 
                                                                                'border': '1px solid #404040',
                                                                                'fontFamily': "Roboto sans-serif", 
                                                                                "fontSize": "15px"
                                                                            },
                                                                            # style_data_conditional=
                                                                            # [
                                                                            #     {
                                                                            #         'if': {'state': 'active'},  # When a cell is hovered
                                                                            #         'backgroundColor': '#202020', # Change this to your preferred hover color
                                                                            #     },
                                                                            # ]
                                                                        )
                                                                    ]
                                                                ) 
                                                            )
                                                        ]
                                                    ),
                                                    style=
                                                    {
                                                        "width": "95%",
                                                        "height": "480px",
                                                        "backgroundColor": "#16283A",
                                                        "padding": "10px",
                                                        "margin": "0px 10px"
                                                    },
                                                ), 
                                            ]
                                        ), 
                                        style=
                                        {
                                            "width": "100%",
                                            "height": "89%",
                                            "backgroundColor": "#203567",
                                            "border": "1px solid #404040", 
                                            "padding": "10px",
                                            "margin": "70px 20px"
                                        }
                                    )
                                )
                            )
                        ], xs=11, sm=11, md=5, lg=5, xl=5,

                    ), 
                    # right Column 
                    dbc.Col(
                        # Create a three rows: 1. for title, 2. for chat display, 3. for input.
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Ask Questions About Your EOI or RFP", style={"color": "#977F7F", "margin": "30px"}),
                                    dbc.Card(
                                        html.Div(
                                            dcc.Loading(
                                                id="loading_rag_response",
                                                type="circle",
                                                color="#707070",
                                                children= [
                                                    html.Div(
                                                        # mu.render_text_with_mathjax(cleaned_text),
                                                        id="rag_output",
                                                        # dangerously_allow_html=True,
                                                        style={
                                                            "marginTop": "20px", 
                                                            "color": "#BFC5DD",
                                                            "fontFamily": "sans-serif",
                                                            "fontSize": "18px",
                                                            # "overflowy": "auto",
                                                            # "maxHeight": "700px"
                                                            }
                                                        )
                                                    ], 
                                                ),
                                                style={
                                                        "display": 'flex',
                                                        "justifyContent": "center",
                                                        "alignItems": "center",
                                                        "height": "100%"
                                                    },
                                            ),
                                            style={
                                                "width": "92%",
                                                # "height": "82%",
                                                "minHeight": "800px",
                                                "maxHeight": "850px",
                                                "backgroundColor": "#16283A",
                                                "padding": "10px",
                                                "margin": "20px 30px",
                                                "overflowY": "auto",
                                                "overflowX": "auto",
                                                # "maxHeight": "400px",
                                                # "maxWidth": "400px"
                                            }
                                        ),
                                    dbc.Card(
                                        dbc.CardBody(
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dcc.Input(
                                                            id="rag_query", 
                                                            placeholder="Enter you query",
                                                            type="text",
                                                            debounce=True,
                                                            
                                                            # resize = "vertical",
                                                            style={"fontFamily": "sans-serif", 
                                                                'fontSize': "18px", 
                                                                "backgroundColor": "#16283A",
                                                                "border": "1px solid lightgrey",
                                                                "borderRadius": "5px",
                                                                "overflow-y":"scroll",
                                                                "color": "#909090", 
                                                                "padding": "5px",
                                                                "width": "100%",
                                                                "maxHeight": "300px",
                                                                "minHeight": "50px",
                                                                "margin": "10px 10px 9px 0px"}
                                                            ), xs=9, sm=9, md=9, lg=10, xl=10
                                                        ),
                                                        dbc.Col(
                                                            html.Div(
                                                                html.Button("Ask", id="ask_button", n_clicks=0,
                                                                            style={"height": "45px",
                                                                                    "width": "67px",
                                                                                    # "display": "flex",
                                                                                    # "alignItems": 'right',
                                                                                    "border": "1px solid lightgrey",
                                                                                    "backgroundColor": "#d17651",
                                                                                    "borderRadius": "5px",
                                                                                    "cursor": "pointer",
                                                                                    "boxShadow": "0 2px 4px rgba (0, 0, 0, 0.2)",
                                                                                    "color": "lightblack",
                                                                                    "margin": "15px 0px 0px 0px", "fontSize": "15px"
                                                                                    }
                                                                                ),
                                                                            style={
                                                                                "display": "flex",
                                                                                "alignItems": "right",
                                                                                "justifyContent": "right",
                                                                                "height":"100%"
                                                                            }

                                                                            
                                                                            
                                                            ), 
                                                            xs=3, sm=3, md=3, lg=2, xl=2
                                                        ) 
                                                ]
                                            )        
                                        ),
                                        style={
                                            "width": "92.3%",
                                            # "minHeight": "10px",
                                            "maxHeight": "auto",
                                            "backgroundColor": "#767A83",
                                            "padding": "0px",
                                            "border": "0px solid #203567",
                                            "margin": "20px 10px 0px 30px"

                                        }
                                    )
                                ]
                            ),
                            style={"width": "97%",
                                    "height": "96%",
                                    "backgroundColor": "#203567",
                                    "border": "1px solid #404040",
                                    "padding": "10px",
                                    "margin": "20px 5px 0px 5px "}
                        )
                    
                    )


                ]
            ),
            html.Script("""
                        window.addEventListener("beforeunload", function (e) {
                        navigator.sendBeacon("/shutdown_cleanup");
                        });
                        """
            )
        ]
    )

    # Call back to upload the file
    @dash_app.callback(
        Output("upload_status", "children"),
        # Output("message_timer", "disabled"),
        Input("upload_eoi", "contents"),
        State("upload_eoi", "filename")
    )
    def upload_to_api(contents, filename):
        """
        Callback to handle file uploads via the Dash interface and delegate storage to a FastAPI backend.

        This callback is triggered when a user uploads a file using the "upload_eoi" Dash `dcc.Upload` component.
        Instead of saving the file directly within Dash, it forwards the file to a FastAPI endpoint (`UPLOAD_ENDPOINT`)
        for validation and storage.

        Key Behaviors:
        --------------
        - Decodes the uploaded file content from base64.
        - Sends the file as a multipart/form-data request to the FastAPI `/upload-pdf/` endpoint.
        - Relies on the backend to:
            - Enforce a maximum file limit (e.g., 3 files).
            - Validate file type (PDF only).
            - Prevent duplicate uploads.
        - Receives the upload result and displays a success or error message accordingly in the "upload_status" area.

        Parameters:
        -----------
        contents : str
            The base64-encoded contents of the uploaded file from the Dash `dcc.Upload` component.

        filename : str
            The original name of the uploaded file.

        Returns:
        --------
        dash.html.Div
            A styled success or error message, depending on the upload result returned by the FastAPI service.
        
        """
        
        try:
            if contents:
                # Split metadata and base64 content 
                content_type, content_string = contents.split(",")
                file_bytes = base64.b64decode(content_string)

                # Prepare the request payload
                files = {
                    "file": (filename, file_bytes, "application/pdf")
                }
            
                # Send to FastAPI 
                response = requests.post(UPLOAD_ENDPOINT, files=files)

                if response.status_code == 200:
                    message = response.json()['message']
                    logger.info(message)
                    return html.P(message, style={'color': 'green'})
                    # return html.Div(
                    #     [
                    #         html.P(message, style={'color': 'green'})
                    #     ]
                    # )
                else:
                    error_message = response.json()['detail']
                    print(f'The file cannot uploaded. {response.status_code}')
                    logger.info(error_message) 
                    return html.P(error_message, style={'color': 'red'})
                    # return html.Div(
                    #     [
                    #         html.P(error_message, style={'color': 'crimson'})
                    #     ]
                    # )
        except Exception as e:
            logger.error(f"Something went wrong: {str(e)}")
        
            
        
    # Call back to update the radio items
    @dash_app.callback(
        Output("select_document", "options"),
        [
            Input("upload_eoi", "contents"),
            Input("initial-load-trigger", "n_intervals"),
            Input("delete_file", "n_clicks"),
        ],
        [
            State("upload_eoi", "filename"),
            State("select_document", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_radio_items(upload_contents, n_intervals, delete_clicks, uploaded_filename, selected_file):
        """
        Dynamically updates the radio button options (`select_document`) when:

        - The app initially loads (via Interval trigger).
        - A new file is uploaded.
        - A file is deleted.

        Core Logic:
        -----------
        - On app load: checks for existing files in the upload directory and lists them.
        - On upload: if a valid file is uploaded, the radio list is refreshed.
        - On delete: calls the FastAPI delete endpoint, then refreshes the list.

        Parameters:
        -----------
        upload_contents : str or None
            Base64 content from the upload component, only used to detect upload trigger.
        n_intervals : int
            Interval value from `dcc.Interval` used to detect app load.
        delete_clicks : int
            Number of times the delete button was clicked.
        uploaded_filename : str or None
            The name of the uploaded file (used to validate upload).
        selected_file : str or None
            The currently selected file (used to determine which file to delete).

        Returns:
        --------
        list[dict]
            A list of radio options representing current PDF files in the upload directory.
        """

        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        # Handle file upload
        if triggered_id == "upload_eoi":
            time.sleep(1)
            if not uploaded_filename: # If user does cancels file upload
                raise dash.exceptions.PreventUpdate

        # Handle file delete
        elif triggered_id == "delete_file":
            if not selected_file: # If user does not selecs any file
                raise dash.exceptions.PreventUpdate
            try:
                delete_url = f"http://127.0.0.1:8000/delete-file/{selected_file}"
                response = requests.delete(delete_url)
                if response.status_code == 200:
                    logger.info(response.json()['file_message'])
                    logger.info(response.json()['folder_message'])
                else:
                    logger.info(response.json()['detail'])

            except Exception as e:
                logger.error("Something went srong while deleting the file")

        # Scan and return current files in upload directory
        files = [f for f in os.listdir(UPLOAD_DIRECTORY)]
        return [{"label": f[:-4], "value": f} for f in files]


    # Call back to display delete button dynamically
    @dash_app.callback(
            Output("delete_file", "style"),
            Input("select_document", "options")
    )
    def toggle_delete_visibility(options):
        """
        Show the delete button of any document is available.
        """
        if options and len(options) > 0:
            return {
                    "height": "10px",
                    "width":"20px",
                    "cursor": "pointer",
                    "position": "absolute",
                    "bottom": "15px",
                    "right": "15px",
                    "backgroundColor": "crimson",
                    "textAlign": "center",
                    "fontSize": "16px",
                    "justifyContent": "center",
                    "alignItems": "center",
                    "display": "flex"
                }
        else:
            return {"display": "none"}



    # Call back to update the dash table
    @dash_app.callback(
        Output("data_table", "data"),
        Output("data_table", "columns"),
        State("select_document", "value"),
        Input("dropdown", "value"),
        
    )
    def auto_extract(file_selected, schema_selected):
        """
        Callback to update the Dash DataTable based on the selectd document and schema.

        This function is triggered when a schema is selected from the dropdown. It uses the 
        previosly selected document (from the radio items) to extract the relevant data.
        
        Parameters:
        ----------- 
        - file_selected (str): The filename of the selected uploaded document. 
        - schema_selected (str): The selected schema or extraction theme from the dropdown.

        Returns:
        ----------
        - data (list of dict): The extracted data rows to populate the Dash DataTable
        - columns (list of dict): The column headers and formatting from the DataTable

        If either input is missing, an empty table is returned.

        """
        if file_selected and schema_selected:
            try:
                # Send GET request to FastAPI
                params = {"filepath": file_selected, "schema_name": schema_selected}
                response = requests.get(EXTRACTION_ENDPOINT, params)

                if response.status_code == 200:
                    payload = response.json()
                    logger.info(f"Succesfull extracted data of {schema_selected}. ")
                    return payload['rows'], payload['cols']
                else:
                    logger.info(f"Extraction of data related to {schema_selected} did not happened.")
                    return [], []

            except Exception as e:
                logger.error(f"Extraction API error: {str(e)}")
                return [], []
        return [], []
            


    # Callback to download the csv.
    @dash_app.callback(
            Output("download-dataframe-csv", "data"),
            Input("img-download", "n_clicks"),
            State("dropdown", "value"),
            State("data_table", "data"), 
            prevent_initial_call=True,
    )
    def download_csv(n_clicks, selected_label, table_data):
        """
        Triggers the download of the displayed Dash DataTable as a csv file.

        This callback is activated when the image (used as download button) is clicked.
        It uses the current content of the DataTable and the selected schema (from dropdown)
        to generate a downloadable CSV file. The file is named dynamically based on the selected
        dropdown value (schema value).

        Inputs:
        ----------
        - n_clicks (int): Number of times the image button has been clicked. 
        - selected_label (str) : The selected value from the dropdown, used as a part of the filename.
        - table_data (list of dicts): The data currently displayed in the Dash DataTable.
        
        Returns:
        ------
        - A Csv file download via "dcc.send_data_frame", named using the selected dropdown value.
        
        """
        df_to_download = pd.DataFrame(table_data)
        logger.info(f"dowloaded csv of data related to {selected_label}")
        return dcc.send_data_frame(df_to_download.to_csv, f"{selected_label}_table_export.csv", index=False)


    # Callback for rag
    @dash_app.callback(
        Output("rag_output", "children"),
        Input("ask_button", "n_clicks"),
        Input("rag_query", "n_submit"),
        State("rag_query", "value"),
        State("select_document", "value")
    )

    def get_rag_response(n_clicks, n_submit, user_query, file_selected):
        """
        Generates a response from RAG system based on the user input. 

        This callback is triggered either when the `Ask` button is clicked or the user press Enter
        inside the input box. It takes user's query and the selected document file, process the 
        query using a RAG pipeline, and returns a Markdown-formatted answer with LaTex math support.

        Inputs:
        --------
        - n_clicks (int): Number of times the "Ask" button is clicked.
        - n_submit (int): Number of times the Enter key is pressed in the input box.
        - user_query (str): The user's query string to send to the RAG system.
        - file_selected (str): The selected document file to use for retrieval.

        Returns:
        --------
        - dcc.Markdown: A formatted answer with simplified LaTeX math rendering if applicable.
        - str: An error message if an exception occurs or if inputs are invalid.
        """
        ctx = callback_context
        
        if not ctx.triggered:
            return "" 
        
        try:
            # Make sure the input is valid 
            if user_query and file_selected:
                print(file_selected)


                params = {"filepath": file_selected, "query": user_query}
                response = requests.get(RAG_ENDPOINT, params)
                if response.status_code == 200:
                    logger.info(f"RAG operation successfully executed")
                    payload = response.json()
                    answer = payload.get('answer', "")

                    clean_answer = mu.simplify_latex_math(answer)
                    return dcc.Markdown(clean_answer, mathjax=True)
                else:
                    logger.error("RAG operation failed")
                    return f"Error from server: {response.status_code} - {response.text}"
            else:
                return "Please enter a query and select a document."
                
        except Exception as e:
            return f"Error: {e.args}"


    # if __name__ == "__main__":
    #     app.run(debug=True, port=8040, use_reloader=False)
    return dash_app

if __name__ == "__main__":
    create_dash_app().run(debug=True, port=8040, use_reloader=False)