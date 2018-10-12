import pandas as pd


class Transform:
    """The transformation strategy interface"""
    def __init__(self):
        self.user_map = {'10509565': 'Paul Joon Kim', '10956238': 'Cody Walls', '12719684': 'Christian Cremo',
                    '13130965': 'Stephen Osborn', '16923137': 'Scott Tippins', '303329': 'Jenkins',
                    '21051438': 'Andrew Wardlaw', '22705519': 'James Im', '22705520': 'Steven Hancock',
                    '24129141': 'Friedrich Neat', '6667755': 'Jack Harris', 'calendar': 'GroupMe Calendar',
                    'system': 'GroupMe', 10509565: 'Paul Joon Kim', 10956238: 'Cody Walls', 12719684: 'Christian Cremo',
                    13130965: 'Stephen Osborn', 16923137: 'Scott Tippins', 303329: 'Jenkins',
                    21051438: 'Andrew Wardlaw', 22705519: 'James Im', 22705520: 'Steven Hancock',
                    24129141: 'Friedrich Neat', 6667755: 'Jack Harris'}
    def transform(self, final_df):
        pass


class LikedYouProb(Transform):
    """
    Represents the transformation for the breakdown of total likes each GroupMe
    member received.
    """
    def __init__(self):
        super(LikedYouProb, self).__init__()
        self.user_map

    def run(self, final_df):
        proportions = {}
        counts = {}
        #The count is the number of messages. The sum is number of likes the person received
        pvt = final_df.pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
        for person in pvt.index:
            p = final_df.loc[(final_df.real_names == person) & (final_df.favorited_by.isnull() == False), :].favorited_by
            p = p.apply(pd.Series).stack().reset_index(drop=True)  # This should flatten your Series List
            p = p.map(self.user_map)  # This converts user id to real_names
            proportions[person] = (p.value_counts()) # Normalize should turn the numbers to percentages

        return proportions


class YouLikedProb(Transform):
    """
    Represents the transformation for the breakdown of total likes each GroupMe
    member gave to one another.
    """
    def __init__(self):
        super(YouLikedProb, self).__init__()
        self.user_map

    def run(self, final_df):
        proportions = {}
        pvt = final_df.pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
        likes_given = final_df.loc[(final_df.favorited_by.isnull() == False), :].favorited_by
        likes_given = likes_given.apply(pd.Series).stack().reset_index(drop=True)
        likes_given = likes_given.map(self.user_map)
        likes_given_total = likes_given.value_counts().sort_index()
        likes_given_total = (dict(likes_given_total))
        likes_given = proportions.fromkeys(likes_given.value_counts().sort_index().index)

        x = final_df.loc[final_df.favorited_by.isnull() == False , ['favorited_by', 'real_names']].stack().apply(pd.Series).stack()
        #print(x.reset_index())
        mask = (x.index.get_level_values(1)=='favorited_by')
        x[mask] = x[mask].map(self.user_map)
        #print(x.unstack(level=1))
        b = x.unstack(level=1)
        b = b.sort_index(level=[0,1], ascending=False)
        b.loc[:,'real_names']= b.loc[:,'real_names'].fillna(method='bfill')

        for person in likes_given:
            c = b.loc[b.favorited_by==person, 'real_names']
            proportions[person] = c.value_counts()

        return proportions


class TotalLikesGiven(Transform):
    """
    The transfomation for returning a DataFrame that has the count of member's
    total likes given.
    """

    def __init__(self):
        super(TotalLikesGiven, self).__init__()
        self.user_map

    def run(self, final_df):
        pvt = final_df.pivot_table(values = 'favorited_count', index='real_names',aggfunc=['sum', 'count', 'mean'])
        likes_given = final_df.loc[(final_df.favorited_by.isnull() == False), :].favorited_by
        likes_given = likes_given.apply(pd.Series).stack().reset_index(drop=True)
        likes_given = likes_given.map(self.user_map)
        likes_given = likes_given.value_counts()
        return(likes_given)


class TotalLikesReceived(Transform):
    """
    The transfomation for returning a DataFrame that has the count of member's
    total likes received.
    """
    def __init__(self):
        super(TotalLikesReceived, self).__init__()
        self.user_map

    def run(self, final_df):
        pvt = final_df.groupby('real_names')['favorited_count'].sum()
        return(pvt)


class TotalMessages(Transform):
    """Returns transformation for Total Messages sent on the groupme"""

    def __init__(self):
        super(TotalMessages, self).__init__()
        self.user_map

    def run(self, final_df):
        like_one = final_df.pivot_table(values = 'favorited_by', index='real_names',aggfunc='count')  # at least 1 like
        like_all = final_df.pivot_table(values = 'favorited_count', index='real_names', aggfunc='count')  # total likes
        like_one.rename(columns={like_one.columns[0]: 'a'}, inplace=True)
        like_all.rename(columns={like_all.columns[0]: 'a'}, inplace=True)

        return([like_all, like_all.sub(like_one), like_one])


class TransformSolver:
    """The Context Manager"""
    def __init__(self, strategy):
        self.strategy = strategy

    def transform(self, final_df):
        return self.strategy.run(final_df)

    def changeTransformation(self, newTransform):
        self.strategy = newTransform
