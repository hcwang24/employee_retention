import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Load Data
employee_data = pd.read_csv("data/employee.csv").drop_duplicates().reset_index(drop=True)
employee_data['Start_Date'] = pd.to_datetime(employee_data['Start_Date'])
employee_data['End_Date'] = pd.to_datetime(employee_data['End_Date'])

# Set "Still Employed" for current employees
employee_data['Reason_for_Leaving'] = employee_data.apply(
    lambda row: "Still Employed" if pd.isnull(row['End_Date']) else row['Reason_for_Leaving'],
    axis=1
)
employee_data['Reason_for_Leaving'] = employee_data['Reason_for_Leaving'].fillna("Not Indicated")

# Define colors for consistency
gender_color_map = {
    'Male': 'Skyblue',
    'Female': 'orangered',
    'Non-binary': 'yellow',
}

job_level_color_map = {
    "L1": "Red",
    "L2": "Orange",
    "L3": "Yellow",
    "L4": "Green",
    "L5": "Blue",
}

reason_color_map = {
    'Work-Life Balance': 'Orange',
    'Compensation': '#3498DB',
    'Career Growth': '#FFC300',
    'Personal Reasons': '#E74C3C',
    'Retirement': '#8E44AD',
    'Still Employed': '#2ECC71',
}

# Initialize Dash app with Bootstrap CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

server = app.server

# Layout of the dashboard
app.layout = dbc.Container([
    html.H1("Employee Retention Dashboard", className="text-center"),
    html.P("Simulated data to explore employee turnover and satisfaction metrics.", className="mb-1 text-center"),

# Statistics Bar
    
    dbc.Row([
        # Left Column Wrapped in Card with Minimal Padding
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.Label("Filter by Department:"),
                    dcc.Dropdown(
                        id='department-filter',
                        options=[{'label': dept, 'value': dept} for dept in employee_data['Department'].unique()],
                        value=sorted(employee_data['Department'].unique().tolist()),  # Default to all departments
                        multi=True
                    ),
                    html.Label("Filter by Reason for Leaving:"),
                    dcc.Dropdown(
                        id='reason-filter',
                        options=[{'label': reason, 'value': reason} for reason in employee_data['Reason_for_Leaving'].dropna().unique()],
                        value=employee_data['Reason_for_Leaving'].dropna().unique().tolist(),  # Default to all reasons
                        multi=True
                    ),
                    html.Label("Filter by Gender:"),
                    dcc.Dropdown(
                        id='gender-filter',
                        options=[{'label': gender, 'value': gender} for gender in employee_data['Gender'].unique()],
                        value=sorted(employee_data['Gender'].unique().tolist()),  # Default to all genders
                        multi=True
                    ),
                    html.Label("Filter by Age Group:"),
                    dcc.Dropdown(
                        id='age-group-filter',
                        options=[{'label': age, 'value': age} for age in employee_data['Age_Group'].unique()],
                        value=sorted(employee_data['Age_Group'].unique().tolist()),  # Default to all age groups
                        multi=True
                    ),
                    html.Label("Filter by Exit Year:"),
                    dcc.Dropdown(
                        id='exit-year-filter',
                        options=[{'label': year, 'value': year} for year in sorted(employee_data['End_Date'].dt.year.unique()) if pd.notnull(year)],
                        value=[],  # Default to no exit year
                        multi=True
                    ),
                ], style={'padding': '0'}),
            ], style={'backgroundColor': 'rgba(173, 216, 230, 0.5)', 'padding': '0px'})  # Light Blue with 50% opacity and minimal padding
        , width=2),  # Left Column for Filters

        # Right Column Wrapped in Card with Minimal Padding
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody(html.H4(id='total-employees', className='card-title'), style={'backgroundColor': 'rgba(255, 255, 255, 0.5)', 'padding': '0px'})), width=4),
                        dbc.Col(dbc.Card(dbc.CardBody(html.H4(id='avg-satisfaction', className='card-title'), style={'backgroundColor': 'rgba(255, 255, 255, 0.5)', 'padding': '0px'})), width=4),
                        dbc.Col(dbc.Card(dbc.CardBody(html.H4(id='total-turnover', className='card-title'), style={'backgroundColor': 'rgba(255, 255, 255, 0.5)', 'padding': '0px'})), width=4),
                    ], className="mb-1 text-center"),
                    
                    # Visualization Section
                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='turnover-reasons', style={'padding': '0px', 'height': '100%'}),
                        ], width=4),
                        dbc.Col([
                            dcc.Graph(id='satisfaction-scores', style={'padding': '0px', 'height': '100%'}),
                        ], width=4),
                        dbc.Col([
                            dcc.Graph(id='average-work-hours', style={'padding': '0px', 'height': '100%'}),
                        ], width=4),
                    ], style={'height': '40vh'}),  # First Row of Graphs

                    dbc.Row([
                        dbc.Col([
                            dcc.Graph(id='age-group-distribution', style={'padding': '0px', 'height': '100%'}),
                        ], width=4),
                        dbc.Col([
                            dcc.Graph(id='gender-distribution', style={'padding': '0px', 'height': '100%'}),
                        ], width=4),
                        dbc.Col([
                            dash_table.DataTable(
                                id='data-preview',
                                columns=[{"name": i, "id": i} for i in employee_data.columns],
                                data=[],
                                page_size=8,
                                style_table={'overflowX': 'auto'},
                            ),
                            html.Button("Export CSV", id="export-button", n_clicks=0),
                            dcc.Download(id="download-dataframe-csv"),
                        ], width=4),
                    ], style={'height': '40vh'}),  # Second Row of Graphs
                ], style={'padding': '0'}),
            ], style={'backgroundColor': 'rgba(255, 255, 255, 0.5)', 'padding': '0px'})  # White with 50% opacity and minimal padding
        , width=10)  # Right Column for Visualizations and Preview
    ], className="mb-1"),

    # Footer
    html.Footer("Developed by HanChen Wang, October 2024", style={'textAlign': 'center', 'padding': '10px'})
], fluid=True, style={
    'background-image': 'url("/assets/work.jpg")',  # Adjusted to reference assets folder
    'background-size': 'cover',
    'background-repeat': 'no-repeat',
    'background-attachment': 'fixed',
    'background-position': 'center',
    'min-height': '100vh',
})

# Callbacks for statistics and visualizations
@app.callback(
    [
        Output('turnover-reasons', 'figure'),
        Output('satisfaction-scores', 'figure'),
        Output('average-work-hours', 'figure'),
        Output('age-group-distribution', 'figure'),
        Output('gender-distribution', 'figure'),
        Output('data-preview', 'data'),
        Output('total-employees', 'children'),
        Output('avg-satisfaction', 'children'),
        Output('total-turnover', 'children'),
    ],
    [
        Input('department-filter', 'value'),
        Input('reason-filter', 'value'),
        Input('gender-filter', 'value'),
        Input('age-group-filter', 'value'),
        Input('exit-year-filter', 'value'),
    ]
)
def update_dashboard(department_filter, reason_filter, gender_filter, age_group_filter, exit_year_filter):
    # Filter data based on selections
    filtered_data = employee_data[
        (employee_data['Department'].isin(department_filter)) &
        (employee_data['Reason_for_Leaving'].isin(reason_filter)) &
        (employee_data['Gender'].isin(gender_filter)) &
        (employee_data['Age_Group'].isin(age_group_filter))
    ]

    # Filter by exit year if selected
    if exit_year_filter:
        filtered_data = filtered_data[filtered_data['End_Date'].dt.year.isin(exit_year_filter)]
    
    # Calculate statistics
    total_employees = f"Total Employees: {len(filtered_data)}"
    avg_satisfaction = f"Average Satisfaction Score: {filtered_data['Satisfaction_Score'].mean().round(2) if len(filtered_data) > 0 else 0}"
    total_turnover = f"Total Turnover: {len(filtered_data[filtered_data['Reason_for_Leaving'] != 'Still Employed'])}"

    # Turnover Reasons by Department
    turnover_reasons = filtered_data[filtered_data['Reason_for_Leaving'].notna()]
    turnover_fig = px.pie(turnover_reasons, 
                           names='Reason_for_Leaving', 
                           color='Reason_for_Leaving',
                           title='Turnover Reasons',
                           hole=0.3,
                           color_discrete_map=reason_color_map)
    turnover_fig.update_traces(textinfo='percent+label')
    turnover_fig.update_layout(title_font_size=18, showlegend=False, margin=dict(l=10, r=10, b=10))

    # Satisfaction Scores by Job Level
    satisfaction_fig = px.box(filtered_data.sort_values("Job_Level"), 
                               x='Job_Level', 
                               y='Satisfaction_Score', 
                               color='Job_Level', 
                               title='Satisfaction Scores by Job Level',
                               labels={'Job_Level': 'Job Level', 'Satisfaction_Score': 'Satisfaction Score'},
                               color_discrete_map=job_level_color_map)
    satisfaction_fig.update_layout(title_font_size=18, boxmode='overlay', showlegend=False, margin=dict(l=10, r=10, b=10))

    # Average Work Hours by Department
    avg_work_hours_fig = px.box(filtered_data.sort_values("Department"), 
                                 x='Department', 
                                 y='Work_Hours',
                                 title='Weekly Work Hours by Department',
                                 labels={'Work_Hours': 'Weekly Work Hours'},
                                 color_discrete_sequence=['black'])
    avg_work_hours_fig.update_layout(title_font_size=18, boxmode='overlay', showlegend=False, margin=dict(l=10, r=10, b=10))

    # Age Group Distribution
    age_group_fig = px.histogram(filtered_data.sort_values("Age_Group"), 
                                  x='Age_Group', 
                                  color='Gender',
                                  title='Age Group and Gender Distribution',
                                  labels={'Age_Group': 'Age Group'},
                                  color_discrete_map=gender_color_map)
    age_group_fig.update_layout(title_font_size=18, barmode='group', showlegend=False, margin=dict(l=10, r=10, b=10))

    # Gender Distribution
    gender_fig = px.histogram(filtered_data.sort_values("Department"), 
                               x='Department', 
                               color='Gender',
                               title='Gender Distribution',
                               labels={'Department': 'Department'},
                               color_discrete_map=gender_color_map)
    gender_fig.update_layout(title_font_size=18, barmode='group', showlegend=False, margin=dict(l=10, r=10, b=10))

    # Return filtered data for the table
    data_preview = filtered_data.to_dict('records')

    return turnover_fig, satisfaction_fig, avg_work_hours_fig, age_group_fig, gender_fig, data_preview, total_employees, avg_satisfaction, total_turnover

# Export button callback
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-button", "n_clicks"),
    State('department-filter', 'value'),
    State('reason-filter', 'value'),
    State('gender-filter', 'value'),
    State('age-group-filter', 'value'),
    State('exit-year-filter', 'value'),
)
def export_data(n_clicks, department_filter, reason_filter, gender_filter, age_group_filter, exit_year_filter):
    if n_clicks > 0:
        # Filter data based on selections
        filtered_data = employee_data[
            (employee_data['Department'].isin(department_filter)) &
            (employee_data['Reason_for_Leaving'].isin(reason_filter)) &
            (employee_data['Gender'].isin(gender_filter)) &
            (employee_data['Age_Group'].isin(age_group_filter))
        ]

        # Filter by exit year if selected
        if exit_year_filter:
            filtered_data = filtered_data[filtered_data['End_Date'].dt.year.isin(exit_year_filter)]

        return dcc.send_data_frame(filtered_data.to_csv, "filtered_employee_data.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
