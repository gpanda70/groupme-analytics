import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import flask
import os
from random import randint

import pandas as pd
from datetime import datetime
import dataprep as dp


access_token = 'WgdkiHLjL5Qe0AgGUhqAnXExQuPQIdvah67xTDQr'
group_id = '13388728'
gen_date = str(datetime.now())

final_df = dp.save_load_transform(access_token, group_id)
print(final_df.head())

proportions = dp.get_proportions(final_df)

pvt =  final_df.pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
pvt1 = final_df[(final_df['favorited_count']>0) | (final_df['real_names']=='Paul Joon Kim')].pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
pvt['difference'] = pvt.loc[:,('count','favorited_count')] - pvt1.loc[:,('sum','favorited_count')]
pvt.sort_values(by = ('count', 'favorited_count'),ascending=True,inplace=True)

count_pvt = pvt.loc[:,('count', 'favorited_count')].sort_values(ascending=True)
sum_pvt = pvt1.loc[:,('count', 'favorited_count')].sort_values(ascending=True)


total_msg = len(final_df)
total_mem = len(sum_pvt)


#server = flask.Flask(__name__)
#server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
#app = dash.Dash(__name__, server=server)
app = dash.Dash()

#app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
app.css.append_css({'external_url': ['https://cdn.rawgit.com/xhlulu/0acba79000a3fd1e6f552ed82edb8a64/raw/dash_template.css',
                                     'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
                                     'https://cdn.rawgit.com/TahiriNadia/styles/b1026938/custum-styles_phyloapp.css',
                                     'https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i',
                                     'https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i']})

app.layout = html.Div(children = [
    html.Div([
        html.H2('GroupMe Analytics')
    ], className='banner'),


    html.Div(children =
             '%d Members | %d Messages | Analytics generated as of %s' %(total_mem, total_msg, gen_date)),

    html.Div([
        dcc.Graph(
            id='bar-graph',
            figure={
                'data': [
                    go.Bar(
                        x=pvt['difference'],
                        y=pvt.index,
                        orientation='h',
                        name='No Likes'
                    ),

                    go.Bar(
                        x=sum_pvt,
                        y=sum_pvt.index,
                        orientation='h',
                        name='At least 1 Like'
                    )
                ],
                'layout':
                    go.Layout(
                        title='Messages Posted',

                        barmode='stack',

                        margin={
                        'l': 110,  # left margin, in px
                        'r': 15,  # right margin, in px
                        't': 40,  # top margin, in px
                        'b': 40  # bottom margin, in px
                        },

                        yaxis={'ticklen': 8, 'tickcolor': '#FFF'}
                    )
            }
        )
    ], className= '12 columns'),
    html.Div([
        html.Div([
            dcc.Dropdown(
            id='opt-dropdown',
            options=[{'label': key, 'value': key} for key, i in proportions.items()],
            value='Andrew Wardlaw'
            ),
        ], className = 'six columns'),

        html.Div([
            dcc.Dropdown(
            id='opt-dropdown2',
            options=[{'label': key, 'value': key} for key, i in proportions.items()],
            value='Andrew Wardlaw'
            ),
        ], className = 'six columns'),
    ], className='row', style={'margin-top': '300'}),

    html.Div([
        html.Div([
            dcc.Graph(
                id='donut-chart',
                figure={
                    "data": [
                        {
                          "values": proportions['Andrew Wardlaw']*100,
                          "labels": proportions['Andrew Wardlaw'].index,
                          "name": "This is the % of Likes attributed to this person",
                          "hoverinfo":"label+percent+name",
                          "hole": .4,
                          "type": "pie"
                        }
                    ],
                    "layout": {
                        "title": "Who Likes You?",
                        "annotations": [
                            {
                                "font": {
                                    "size": 10
                                },
                                "showarrow": False,
                                "text": "<b>Andrew</b>",
                                "x": 0.20,
                                "y": 0.5
                            }
                        ]

                    }
                }
            ),
        ], className = 'six columns'),
        html.Div([
            dcc.Graph(
                id='donut-chart2',
                figure={
                    "data": [
                        {
                          "values": proportions['Andrew Wardlaw']*100,
                          "labels": proportions['Andrew Wardlaw'].index,
                          "name": "This is the % of Likes attributed to this person",
                          "hoverinfo":"label+percent+name",
                          "hole": .4,
                          "type": "pie"
                        }
                    ],
                    "layout": {
                        "title": "Who Likes You?",
                        "annotations": [
                            {
                                "font": {
                                    "size": 10
                                },
                                "showarrow": False,
                                "text": "<b>Andrew</b>",
                                "x": 0.51,
                                "y": 0.5
                            }
                        ]

                    }
                }
            ),
        ], className = 'six columns')
    ], className = 'row')
], className= 'ten columns offset-by-one')



@app.callback(
    dash.dependencies.Output('donut-chart', 'figure'),
    [dash.dependencies.Input('opt-dropdown', 'value')]
)
def update_pie_probablity(name):
    return {
                "data": [
                    {
                      "values": proportions[name]*100,
                      "labels": proportions[name].index,
                      "domain": {"x": [0, .48]},
                      "name": "This is the % of Likes attributed to this person",
                      "hoverinfo":"label+percent+name",
                      "hole": .4,
                      "type": "pie"
                    }
                ],
                "layout": {
                    "title": "Who Likes You",
                    "annotations": [
                        {
                            "font": {
                                "size": 10
                            },
                            "showarrow": False,
                            "text": '<b>'+name.split(' ')[0]+'</b>',
                            "x": 0.20,
                            "y": 0.5
                        }
                    ]
                }
            }




if __name__ == '__main__':
    app.run_server(debug=True, port=8000, host='0.0.0.0')
    #app.run_server(debug=True, threaded=True)
