# Import required libraries
import os
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
# https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_3/lab_theia_plotly_dash.md.html

path = os.path.dirname(os.path.realpath(__file__))

# Read the data into pandas dataframe
spacex_df = pd.read_csv(path+"/spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

by_launch_df = spacex_df[['Launch Site', 'class']]
by_launch_df = pd.concat(
    [by_launch_df, pd.get_dummies(by_launch_df['class'])], axis=1)
by_launch_df.rename(columns={0: 'failed', 1: 'succeeded'}, inplace=True)
by_launch_df.drop(['class'], axis=1, inplace=True)
summary_df = by_launch_df.groupby(['Launch Site']).sum()
summary_df['overall_success_pct'] = summary_df['succeeded'].values / \
    (summary_df['succeeded'].sum())
summary_df.reset_index(inplace=True)


def get_selected_df(entered_site):
    global spacex_df
    selected = spacex_df[spacex_df['Launch Site'] == entered_site]
    selected_df = selected[['Launch Site', 'class']]
    selected_df = selected_df.groupby(['class']).count()
    selected_df.reset_index(inplace=True)
    return selected_df


#fig_pie = None
#fig_scatter = None
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites',
                      'value': 'ALL'},
                     {'label': 'CCAFS LC-40',
                      'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40',
                      'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A',
                      'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}],
                 value='ALL',
                 placeholder='Select a Launch Site here',
                 searchable=True
                 ),

    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(
        # dcc.Graph(id='success-pie-chart', figure=fig_pie)),
        # dcc.Graph(id='success-pie-chart')), #dcc.Graph is not working at all
        html.Div([], id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                    marks={0: '0', 100: '100'},
                    value=[min_payload, max_payload]),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(
        # dcc.Graph(id='success-payload-scatter-chart', figure=fig_scatter))
        # dcc.Graph(id='success-payload-scatter-chart'))
        # dcc.Graph(id='success-payload-scatter-chart'))  #dcc.Graph is not working at all
        html.Div([], id='success-payload-scatter-chart'))
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output


@ app.callback([Output(component_id='success-pie-chart', component_property='children'),
                # Output(component_id='success-pie-chart', component_property='figure'),
                # Output(component_id='success-payload-scatter-chart', component_property='figure')],
                Output(component_id='success-payload-scatter-chart', component_property='children')],
               [Input(component_id='site-dropdown', component_property='value'),
                Input(component_id='payload-slider', component_property='value')])
def get_charts(entered_site, payload_slider):
    spacex_df_sub = spacex_df[spacex_df['Payload Mass (kg)'].between(
        payload_slider[0], payload_slider[1])]
    if entered_site == 'ALL':
        fig_pie = px.pie(summary_df, values='overall_success_pct',
                         names='Launch Site',
                         title='Total Success Launches By Site')
        fig_scatter = px.scatter(spacex_df_sub, x='Payload Mass (kg)', y='class',
                                 color='Booster Version Category',
                                 title='Correlation between Payload and Success for all Sites')
    else:
        selected = get_selected_df(entered_site)
        fig_pie = px.pie(selected, values='Launch Site',
                         names='class',
                         title='Total Success Launches for site '+entered_site)

        fig_scatter = px.scatter(spacex_df_sub[spacex_df_sub['Launch Site'] == entered_site],
                                 x='Payload Mass (kg)', y='class',
                                 color='Booster Version Category',
                                 title='Correlation between Payload and Success for site '+entered_site)

    return [dcc.Graph(figure=fig_pie),
            dcc.Graph(figure=fig_scatter)]


# Run the app
if __name__ == '__main__':
    app.run_server()
    # app.run_server(debug=True)
