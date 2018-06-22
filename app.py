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

df = dp.save_load_transform(access_token, group_id)
final_df = pd.concat([df,pd.read_csv('src', sep='\t', encoding='utf-8')], ignore_index=True)
final_df = final_df.loc[(final_df.real_names!='GroupMe') & (final_df.real_names!='GroupMe Calendar') & (final_df.real_names!='Paul Joon Kim'), :]

proportions = dp.get_proportions(final_df)

pvt =  final_df.pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
pvt1 = final_df[(final_df['favorited_count']>0) | (final_df['real_names']=='Paul Joon Kim')].pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
pvt['difference'] = pvt.loc[:,('count','favorited_count')] - pvt1.loc[:,('sum','favorited_count')]
pvt.sort_values(by = ('count', 'favorited_count'),ascending=True,inplace=True)

count_pvt = pvt.loc[:,('count', 'favorited_count')].sort_values(ascending=True)
sum_pvt = pvt1.loc[:,('count', 'favorited_count')].sort_values(ascending=True)


total_msg = len(final_df)
total_mem = len(sum_pvt)



server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

app.layout = html.Div(children = [
    html.H1(children = 'GroupMe Analytics'),

    html.Div(children =
             '%d Members | %d Messages | Analytics generated as of %s' %(total_mem, total_msg, gen_date)),

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

                    barmode= 'stack',

                    margin={
                    'l': 110,  # left margin, in px
                    'r': 15,  # right margin, in px
                    't': 40,  # top margin, in px
                    'b': 40  # bottom margin, in px
                    },

                    yaxis={'ticklen': 8, 'tickcolor': '#FFF'}
                )



        }
    ),
    html.Div([

        dcc.Dropdown(
            id='opt-dropdown',
            options=[{'label': key, 'value': key} for key, i in proportions.items()],
            value='Andrew Wardlaw'
        ),

        dcc.Graph(
            id='donut-chart',
            figure={
                "data": [
                    {
                      "values": proportions['Andrew Wardlaw']*100,
                      "labels": proportions['Andrew Wardlaw'].index,
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
                            "text": "<b>Andrew<\b>",
                            "x": 0.21,
                            "y": 0.5
                        }
                    ]
                }
            }
        ),


    ],style={'width': '49%', 'display': 'inline-block', 'float': 'middle','margin-top': '10'}
    )
])
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
                            "text": '<b>'+name.split(' ')[0]+'<\b>',
                            "x": 0.21,
                            "y": 0.5
                        }
                    ]
                }
            }




if __name__ == '__main__':
    #app.run_server(debug=True, port=8000, host='0.0.0.0')
    app.run_server(debug=True, threaded=True)