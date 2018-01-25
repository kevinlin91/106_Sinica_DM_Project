#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from sklearn import preprocessing
from handle_sqlite import sqlite_data_handler
from user_feature_engineering import featureExtractor

class preProcessor(object):
    def __init__(self, data):
        self.data = data
        self.users = data.table_Users

    def get_users(self):
        self.users = self.users[['Id', 'Ranking', 'HighestRanking', 'Tier', 'RegisterDate']].set_index('Id')

        # Add extracted features from other tables
        engineered_features = featureExtractor(self.data).user_features()
        self.users = pd.merge(self.users, engineered_features, how='outer', left_index=True, right_index=True)

        self.handle_missing_user_data()
        self.transform_user_data()
        return self.users

    def transform_user_data(self):
        # Fix Wrong Tier Assignment
        self.users.loc[self.users.Tier == 0, 'Tier'] = 1
        # Make Tier evenly distributed
        self.users['Tier'] = self.users['Tier'].replace(10, 5) # Categorical data

    def handle_missing_user_data(self):
        self.users['Tier'].fillna(1, inplace=True)
        self.users['NumPosts'].fillna(0, inplace=True)
        self.users['PostsPerWeek'].fillna(0, inplace=True)

if __name__ == "__main__":
    data = sqlite_data_handler("./data")
    pp = preProcessor(data)
    users = pp.get_users()

    #Select which users to include: Active Users which have days so we can handle timely features
    users = users[(users['NumCompetitions'] > 0) & (users['DaysOnKaggle'] > 7)]
    print(users.describe())

    #Asthetics
    params = {'axes.titlesize':'24', 'axes.labelsize':'20', 'xtick.labelsize':'16', 'ytick.labelsize':'16'}
    matplotlib.rcParams.update(params)

    users[['PostsPerWeek', 'SubmissionsPerCompetition', 'PointsPerWeek', 'CompetitionsPerWeek']].hist(bins = 100, log=False, layout=(2, 2))
    #users.plot.scatter(y='NumSubmissions', x='DaysOnKaggle')
    #users.plot.scatter(x='NumSubmissions', y='PointsPerWeek')
    #users.plot.scatter(x='DaysOnKaggle', y='NumPosts')
    #users.plot.scatter(x='TotalCompetitions', y='UserPointsMultiplier')

    plt.show()

