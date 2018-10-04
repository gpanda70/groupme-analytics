import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import flask
import os
from random import randint

from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd
from datetime import datetime


from message import Message
import transform

access_token = 'WgdkiHLjL5Qe0AgGUhqAnXExQuPQIdvah67xTDQr'
group_id = '13388728'

sched = BlockingScheduler()

# Loading in the message and updating it
file_path = os.path.join(os.path.dirname(__file__),'src')
msg = Message(access_token, group_id,file_path)

#

final_df = msg.load()

#Data for the first donut chart
liked_you_prob = transform.TransformSolver(transform.LikedYouProb())
liked_you_prob = liked_you_prob.transform(final_df)

#Data for the second donut chart
you_liked_prob = transform.TransformSolver(transform.YouLikedProb())
you_liked_prob = you_liked_prob.transform(final_df)

#Data for the bar charts
total_message = transform.TransformSolver(transform.TotalMessages())
all_like, diff, one_like = total_message.transform(final_df)

all_like = all_like.sort_values('a')
diff = diff.reindex(all_like.index)
one_like = one_like.reindex(all_like.index)

total_msg = len(final_df)
total_mem = len(diff)
gen_date = str(datetime.now())


server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)
#app = dash.Dash()

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
                        x=diff['a'],
                        y=diff.index,
                        orientation='h',
                        name='No Likes'
                    ),

                    go.Bar(
                        x=one_like['a'],
                        y=one_like.index,
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
            options=[{'label': key, 'value': key} for key, i in liked_you_prob.items()],
            value='Andrew Wardlaw'
            ),
        ], className = 'six columns'),

        html.Div([
            dcc.Dropdown(
            id='opt-dropdown2',
            options=[{'label': key, 'value': key} for key, i in you_liked_prob.items()],
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
                          "values": liked_you_prob['Andrew Wardlaw'],
                          "labels": liked_you_prob['Andrew Wardlaw'].index,
                          "name": "This is the # of likes this person gave you out of your Total likes received",
                          "hoverinfo":"label+value+percent+name",
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
                          "values": you_liked_prob['Andrew Wardlaw'],
                          "labels": you_liked_prob['Andrew Wardlaw'].index,
                          "name": "This is the # of likes you gave this person out of your Total Likes Gave",
                          "hoverinfo":"label+value+percent+name",
                          "hole": .4,
                          "type": "pie"
                        }
                    ],
                    "layout": {
                        "title": "Who do you Like?",
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
def update_pie1_probablity(name):
    return {
                "data": [
                    {
                      "values": liked_you_prob[name],
                      "labels": liked_you_prob[name].index,
                      "domain": {"x": [0, .48]},
                      "name": "This is the # of likes this person gave you out of your Total likes received",
                      "hoverinfo":"label+value+percent+name",
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
                            "text": '<b>'+name.split(' ')[0]+'</b>',
                            "x": 0.20,
                            "y": 0.5
                        }
                    ]
                }
            }

@app.callback(
    dash.dependencies.Output('donut-chart2', 'figure'),
    [dash.dependencies.Input('opt-dropdown2', 'value')]
)
def update_pie2_probablity(name):
    return {
                "data": [
                    {
                      "values": you_liked_prob[name],
                      "labels": you_liked_prob[name].index,
                      "domain": {"x": [0, .48]},
                      "name": "This is the # of likes you gave this person out of your Total Likes Gave",
                      "hoverinfo":"label+value+percent+name",
                      "hole": .4,
                      "type": "pie"
                    }
                ],
                "layout": {
                    "title": "Who do you like?",
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
    #app.run_server(debug=True, port=8000, host='0.0.0.0')
    app.run_server(debug=True, threaded=True)
    #app.run_server(debug=True, port=8000, host='0.0.0.0')
    #app.run_server(debug=True, threaded=True)
