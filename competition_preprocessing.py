#!/usr/bin/env python

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

import processing_utils
from competition_feature_engineering import competitions_feature as cf

class compPreProcessor(object):
    def __init__(self):
        self.competitions = pd.read_csv('./data/competitions.csv').set_index('CompetitionId')

    def get_competitions(self):
        self.handle_missing_data()
        self.transform_data()
        self.competitions = processing_utils.log_data(self.competitions, ['DataSizeBytes', 'RewardQuantity'])
        return self.competitions

    def handle_missing_data(self):
        # Knowledge Or Swag competitions, which do not have a quantity --> Set 0
        self.competitions.RewardQuantity.fillna(0, inplace=True)

        # Manually research missing Data Size
        self.competitions.loc[2442, 'DataSizeBytes'] = 0 # External Sources
        self.competitions.loc[4453, 'DataSizeBytes'] = 5.218e8
        # Can't find out datasize --> drop
        self.competitions.drop([2496, 2518, 2752, 2984, 3108, 3211, 3493, 4031], inplace=True)

    def transform_data(self):
        # Take care of outliers i.e. 100000
        self.competitions.loc[self.competitions.MaxDailySubmissions > 10, 'MaxDailySubmissions'] = 10

        # TODO: Standardize Submissions/Teams by duration?
        # TODO: Normalize some Features to 0 to 1? Makes no sense with log

if __name__ == "__main__":
    pp = compPreProcessor()
    competitions = pp.get_competitions()

    # Plot some graphs
    competitions = competitions.loc[competitions.USD == 1, ] # $$$ competitions
    
    params = {'axes.titlesize':'24', 'axes.labelsize':'20', 'xtick.labelsize':'16', 'ytick.labelsize':'16'}
    matplotlib.rcParams.update(params)
    #competitions.plot.scatter(y='Top10')
    plt.plot(competitions.DataSizeBytes, competitions.Top100, "o")

    plt.show()
