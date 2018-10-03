import requests
import json
from ast import literal_eval

import pandas as pd
import numpy as np


class Message:
    """Class that represents a groupme message
    """
    def __init__(self, access_token, group_id, file_name):
        self.user = []
        self.created_at = []
        self.text = []
        self.sender_id = []
        self.user_id = []
        self.favorited_by = []
        self.message_id = []
        self.is_current = False

        self.access_token = access_token
        self.group_id = group_id
        self.file_name = file_name

    def load(self):
        """Loads in csv file that contains all groupme messages"""
        self.df = pd.read_csv(self.file_name, sep='\t', encoding='utf-8')

        #Reads in the string as a list and ignores null values in the favorited_by column
        self.df.loc[:, 'favorited_by'] = self.df.loc[:, 'favorited_by'].apply(lambda x: x if pd.isnull(x) else literal_eval(x))
        return self.df

    def update(self):
        """Updates the messages in the csv file from the last message that was retrieved"""

        last_msg_id = self.df['message_id'].iat[0]
        payload = {'after_id': last_msg_id}
        response = requests.get('https://api.groupme.com/v3/groups/' + self.group_id + '/messages?token=' + self.access_token,
                                params=payload)
        data = response.json()
        history = True

        while history:
            try:

                for i in range(0,20):
                    self.user.append(data['response']['messages'][i]['name'])
                    self.created_at.append(data['response']['messages'][i]['created_at'])
                    self.text.append(data['response']['messages'][i]['text'])
                    self.sender_id.append(data['response']['messages'][i]['sender_id'])
                    self.user_id.append(data['response']['messages'][i]['user_id'])
                    self.favorited_by.append(data['response']['messages'][i]['favorited_by'])
                    self.message_id.append(data['response']['messages'][i]['id'])


                payload = {'after_id': self.message_id[-1]}
                response = requests.get('https://api.groupme.com/v3/groups/' + self.group_id + '/messages?token=' + self.access_token,
                                        params=payload)
                data = response.json()

            except IndexError:
                history = False
                self.is_current = False
            except KeyError:
                history = False
                self.is_current = True


    def save(self):
        if not self.is_current:
            user_map = {'10509565': 'Paul Joon Kim', '10956238': 'Cody Walls', '12719684': 'Christian Cremo',
                        '13130965': 'Stephen Osborn', '16923137': 'Scott Tippins', '303329': 'Jenkins',
                        '21051438': 'Andrew Wardlaw', '22705519': 'James Im', '22705520': 'Steven Hancock',
                        '24129141': 'Friedrich Neat', '6667755': 'Jack Harris', 'calendar': 'GroupMe Calendar',
                        'system': 'GroupMe', 10509565: 'Paul Joon Kim', 10956238: 'Cody Walls', 12719684: 'Christian Cremo',
                        13130965: 'Stephen Osborn', 16923137: 'Scott Tippins', 303329: 'Jenkins',
                        21051438: 'Andrew Wardlaw', 22705519: 'James Im', 22705520: 'Steven Hancock',
                        24129141: 'Friedrich Neat', 6667755: 'Jack Harris'}

            updated_df = pd.DataFrame({'user': self.user,
                               'create_date': self.created_at,
                               'text': self.text,
                               'sender_id': self.sender_id,
                               'user_id': self.user_id,
                               'favorited_by': self.favorited_by,
                               'message_id': self.message_id})

            #transforms empty list in favorited by to null value
            updated_df['favorited_by'] = updated_df['favorited_by'].apply(lambda x: np.nan if not x else x)
            #Finds the count of favorited messages and updates the favorited_count column
            updated_df['favorited_count'] = updated_df['favorited_by'].apply(lambda x: len(x) if isinstance(x,list) \
                                    else 0)
            #maps names to real names based on user id.
            updated_df['real_names'] = updated_df['user_id'].map(user_map)
            #reverses direction so it will fit with new data
            updated_df = updated_df[::-1]

            final_df = pd.concat([updated_df, self.df], ignore_index=True)
            #ignores the people below
            final_df = final_df.loc[(final_df.real_names != 'GroupMe') & (final_df.real_names != 'GroupMe Calendar') & (final_df.real_names != 'Paul Joon Kim'), :]
            #converts favorited count to float so you can perform divisions
            final_df['favorited_count'] = final_df['favorited_count'].astype(np.float64)
            final_df.to_csv(self.file_name, sep='\t', encoding='utf-8', index=False)
