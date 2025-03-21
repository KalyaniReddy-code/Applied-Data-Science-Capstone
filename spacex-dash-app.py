# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Generate dropdown options (Adding 'All Sites' as default)
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown for Launch Site Selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Default selection (All Sites)
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie Chart to show the total successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    # TASK 3: Payload Slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},  # Marks every 2500kg
        value=[min_payload, max_payload]  # Default to full range
    ),

    html.Br(),

    # TASK 4: Scatter Chart for Payload vs. Launch Success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: Callback to update the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Aggregate data for all sites
        fig = px.pie(
            spacex_df, 
            values='class',  
            names='Launch Site',  
            title='Total Successful Launches by Site'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count success and failure occurrences
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        
        # Create pie chart for selected site
        fig = px.pie(
            site_counts, 
            values='count',  
            names='class',  
            title=f'Success vs. Failure for {entered_site}',
            color_discrete_map={1: 'green', 0: 'red'}  # Green for success, red for failure
        )
    
    return fig


# TASK 4: Callback to update the scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter data based on payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    
    # If a specific site is selected, filter by site
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',  # Different boosters will have different colors
        title=f'Payload vs. Launch Outcome for {selected_site if selected_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
        
    )
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port = 8060)