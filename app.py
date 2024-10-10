import dash
from dash import dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load Data
employee_data = pd.read_csv("data/employee.csv").drop_duplicates().reset_index(drop=True)
employee_data['Start_Date'] = pd.to_datetime(employee_data['Start_Date'])
employee_data['End_Date'] = pd.to_datetime(employee_data['End_Date'])

# Set "Still Employed" for current employees
employee_data['Reason_for_Leaving'] = employee_data.apply(
    lambda row: "Still Employed" if pd.isnull(row['End_Date']) else row['Reason_for_Leaving'],
    axis=1
)

# Define colors for consistency
color_map = {
    'Male': 'lightblue',
    'Female': 'lightpink',
    'Non-binary': 'yellow',
    'IT': 'skyblue',
    'HR': 'orange',
    'Sales': 'green',
    'Finance': 'purple',
    'Marketing': 'pink',
    'Low': 'red',
    'Medium': 'orange',
    'High': 'yellowgreen',
}

# Initialize Dash app with Bootstrap CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.JOURNAL])

# Layout of the dashboard
app.layout = dbc.Container([
    html.H1("Employee Retention Dashboard", className="text-center"),
    html.P("Simulated data to explore employee turnover and satisfaction metrics.", className="mb-1 text-center"),

    # Filters
    dbc.Row([
        dbc.Col([
            html.Label("Filter by Department:"),
            dcc.Dropdown(
                id='department-filter',
                options=[{'label': dept, 'value': dept} for dept in employee_data['Department'].unique()],
                value=employee_data['Department'].unique().tolist(),  # Default to all departments
                multi=True
            )
        ], width=6),
        dbc.Col([
            html.Label("Filter by Reason for Leaving:"),
            dcc.Dropdown(
                id='reason-filter',
                options=[{'label': reason, 'value': reason} for reason in employee_data['Reason_for_Leaving'].fillna("Not Indicated").unique()],
                value=employee_data['Reason_for_Leaving'].fillna("Not Indicated").unique().tolist(),  # Default to all reasons
                multi=True
            )
        ], width=6),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            html.Label("Filter by Gender:"),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': gender, 'value': gender} for gender in employee_data['Gender'].unique()],
                value=employee_data['Gender'].unique().tolist(),  # Default to all genders
                multi=True
            )
        ], width=6),
        dbc.Col([
            html.Label("Filter by Age Group:"),
            dcc.Dropdown(
                id='age-group-filter',
                options=[{'label': age, 'value': age} for age in employee_data['Age_Group'].unique()],
                value=employee_data['Age_Group'].unique().tolist(),  # Default to all age groups
                multi=True
            )
        ], width=6),
    ], className="mb-3"),

    # Filter by Exit Year
    dbc.Row([
        dbc.Col([
            html.Label("Filter by Exit Year:"),
            dcc.Dropdown(
                id='exit-year-filter',
                options=[{'label': str(year), 'value': year} for year in employee_data['End_Date'].dt.year.unique() if pd.notnull(year)],
                value=[],  # Default to no exit year
                multi=True
            )
        ], width=6),
    ], className="mb-3"),

    # Cards for Statistics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Total Employees"),
                    html.Div(id='total-employees', className='stat-box'),
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Satisfaction Score"),
                    html.Div(id='avg-satisfaction', className='stat-box'),
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Average Work Hours"),
                    html.Div(id='avg-work-hours', className='stat-box'),
                ])
            ])
        ], width=4),
    ], className="mb-4"),

    # Visualization Section
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='turnover-reasons'),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='satisfaction-scores'),
        ], width=6),
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='average-work-hours'),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='age-group-distribution'),
        ], width=6),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='gender-distribution'),
        ], width=12),
    ]),

    # Footer
    html.Footer("Developed by HanChen Wang, October 2024", style={'textAlign': 'center', 'padding': '10px'})
], fluid=True)

# Callbacks for statistics and visualizations
@app.callback(
    [
        Output('total-employees', 'children'),
        Output('avg-satisfaction', 'children'),
        Output('avg-work-hours', 'children'),
        Output('turnover-reasons', 'figure'),
        Output('satisfaction-scores', 'figure'),
        Output('average-work-hours', 'figure'),
        Output('age-group-distribution', 'figure'),
        Output('gender-distribution', 'figure'),
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

    # Statistics
    total_employees = f"Total Employees: {filtered_data['Employee_ID'].nunique()}"
    avg_satisfaction = f"Average Satisfaction Score: {filtered_data['Satisfaction_Score'].mean():.2f}"
    avg_work_hours = f"Average Work Hours: {filtered_data['Work_Hours'].mean():.2f} hours"

    # Turnover Reasons by Department
    turnover_reasons = filtered_data[filtered_data['Reason_for_Leaving'].notna()]
    turnover_fig = px.pie(turnover_reasons, 
                           names='Reason_for_Leaving', 
                           title='Turnover Reasons by Department',
                           hole=0.3,
                           color_discrete_sequence=['#4CAF50', '#2196F3', '#FFC107', '#FF5722', '#9C27B0'])
    turnover_fig.update_traces(textinfo='percent+label')

    # Satisfaction Scores by Job Level
    satisfaction_fig = px.box(filtered_data, 
                               x='Job_Level', 
                               y='Satisfaction_Score', 
                               title='Satisfaction Scores by Job Level',
                               labels={'Job_Level': 'Job Level', 'Satisfaction_Score': 'Satisfaction Score'},
                               color_discrete_sequence=['#2196F3'])
    satisfaction_fig.update_layout(boxmode='overlay', showlegend=False)

    # Average Work Hours by Department
    avg_work_hours_df = filtered_data.groupby('Department')['Work_Hours'].mean().reset_index()
    avg_work_hours_fig = px.box(avg_work_hours_df, 
                                 x='Department', 
                                 y='Work_Hours',
                                 title='Average Work Hours by Department',
                                 labels={'Work_Hours': 'Average Work Hours'},
                                 color_discrete_sequence=['#FFC107'])
    avg_work_hours_fig.update_layout(boxmode='overlay', showlegend=False)

    # Age Group Distribution
    age_group_fig = px.histogram(filtered_data, 
                                  x='Age_Group', 
                                  color='Gender',
                                  title='Age Group Distribution',
                                  labels={'Age_Group': 'Age Group'},
                                  color_discrete_map=color_map)
    age_group_fig.update_layout(barmode='group')

    # Gender Distribution
    gender_fig = px.histogram(filtered_data, 
                               x='Gender', 
                               color='Department', 
                               title='Gender Distribution by Department',
                               labels={'Gender': 'Gender'},
                               color_discrete_map=color_map)
    gender_fig.update_layout(barmode='group')

    return total_employees, avg_satisfaction, avg_work_hours, turnover_fig, satisfaction_fig, avg_work_hours_fig, age_group_fig, gender_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
