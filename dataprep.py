import requests
import pandas as pd
import numpy as np

user_map = {'10509565': 'Paul Joon Kim', '10956238': 'Cody Walls', '12719684': 'Christian Cremo',
            '13130965': 'Stephen Osborn', '16034819': 'George Barron', '16923137': 'Scott Tippins',
            '21051438': 'Andrew Wardlaw', '22705519': 'James Im', '22705520': 'Steven Hancock',
            '24129141': 'Friedrich Neat', '6667755': 'Jack Harris', 'calendar': 'GroupMe Calendar',
            'system': 'GroupMe', 10509565: 'Paul Joon Kim', 10956238: 'Cody Walls', 12719684: 'Christian Cremo',
            13130965: 'Stephen Osborn', 16034819: 'George Barron', 16923137: 'Scott Tippins',
            21051438: 'Andrew Wardlaw', 22705519: 'James Im', 22705520: 'Steven Hancock',
            24129141: 'Friedrich Neat', 6667755: 'Jack Harris'}

def data_pull(last_msg_id,access_token,group_id):

    user = []
    created_at = []
    text = []
    sender_id = []
    user_id = []
    favorited_by = []
    message_id = []
    Done = False

    payload = {'after_id': last_msg_id}
    response = requests.get('https://api.groupme.com/v3/groups/' + group_id + '/messages?token=' + access_token,
                            params=payload)
    data = response.json()

    while Done==False:

        try:

            for i in range(0,20):
                user.append(data['response']['messages'][i]['name'])
                created_at.append(data['response']['messages'][i]['created_at'])
                text.append(data['response']['messages'][i]['text'])
                sender_id.append(data['response']['messages'][i]['sender_id'])
                user_id.append(data['response']['messages'][i]['user_id'])
                favorited_by.append(data['response']['messages'][i]['favorited_by'])
                message_id.append(data['response']['messages'][i]['id'])


            payload = {'after_id': message_id[-1]}
            response = requests.get('https://api.groupme.com/v3/groups/' + group_id + '/messages?token=' + access_token,
                                    params=payload)
            data = response.json()

        except IndexError:
            Done = True

    df = pd.DataFrame({'user': user,
                       'create_date': created_at,
                       'text': text,
                       'sender_id': sender_id,
                       'user_id': user_id,
                       'favorited_by': favorited_by,
                       'message_id': message_id})

    return df[::-1]


def transform_data(df):

    df.to_csv('temp_file', sep='\t', encoding='utf-8', index=False)

    t_df = pd.read_csv('temp_file', sep='\t', encoding='utf-8')

    #transforms empty list to null value
    t_df['favorited_by'] = t_df['favorited_by'].apply(lambda x: np.nan if x == '[]' else x)

    #Finds the count of favorited messages
    t_df['favorited_count'] = t_df['favorited_by'].apply(lambda x: 0 if pd.isnull(x) \
                            else (len(x.split(',')) if ',' in x else 1))
    #maps names
    t_df['real_names'] = t_df['user_id'].map(user_map)


    return(t_df)


def save_load_transform(access_token,group_id):
    last_msg = pd.read_csv('src', sep='\t', encoding='utf-8')['message_id'].iat[0]
    new_df = data_pull(last_msg,access_token,group_id)
    t_df = transform_data(new_df)
    final_df = pd.concat([t_df, pd.read_csv('src', sep='\t', encoding='utf-8')], ignore_index=True)
    final_df = final_df.loc[(final_df.real_names != 'GroupMe') & (final_df.real_names != 'GroupMe Calendar') & (final_df.real_names != 'Paul Joon Kim'), :]
    final_df.to_csv('src', sep='\t', encoding='utf-8', index=False)
    final_df['favorited_count'] = final_df['favorited_count'].astype(np.float64)

    return final_df

def get_proportions(final_df):
    proportions = {}
    pvt = final_df.pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
    for person in pvt.index:
        p = final_df.loc[(final_df.real_names == person) & (final_df.favorited_by.isnull() == False), :].favorited_by.apply(
            lambda x: x.replace('[', ''))
        p = p.apply(lambda x: x.replace(']', ''))
        p = pd.DataFrame(p.str.split(', ').tolist()).stack()
        p = p.reset_index(drop=True)
        p = p.apply(lambda x: x.replace('\'', ''))
        p = p.map(user_map)
        proportions[person] = p.value_counts(normalize=True)

    return proportions
#access_token = 'WgdkiHLjL5Qe0AgGUhqAnXExQuPQIdvah67xTDQr'
#group_id = '13388728'

#ast_msg_id = pd.read_csv('src', sep='\t', encoding='utf-8')['message_id'].iat[0]

#print(data_pull(ast_msg_id, access_token, group_id))