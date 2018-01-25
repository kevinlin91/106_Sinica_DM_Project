# -*- coding: utf-8 -*-
from handle_sqlite import sqlite_data_handler
from datetime import datetime
import pandas as pd
import numpy as np

class competitions_feature(object):
    def __init__(self, path_root=''):
        self.path_root = path_root
        self.sqlite_data = sqlite_data_handler(self.path_root)
        self.competition = self.sqlite_data.table_Competitions
        self.team = self.sqlite_data.table_Teams
        self.submission = self.sqlite_data.table_Submissions
        self.competitionhostsegment = self.sqlite_data.table_CompetitionHostSegments

    def numSubmissions(self):
        team_competitions = pd.DataFrame(self.team)[['Id','CompetitionId']]
        team_competitions.columns = ['TeamId', 'CompetitionId']
        submissions = pd.DataFrame(self.submission['TeamId'].value_counts())
        submissions.columns = ['team_count']
        num_submissions = pd.merge(submissions, team_competitions, left_index=True, right_on='TeamId')
        num_submissions['num_submissions'] = num_submissions.groupby(['CompetitionId'])['team_count'].transform('sum')
        num_submissions= num_submissions[ ['CompetitionId', 'num_submissions'] ].drop_duplicates('CompetitionId').set_index('CompetitionId')
        num_submissions.index.name = 'Id'
        return num_submissions

    def numTeams(self):
        num_teams = pd.DataFrame(self.team['CompetitionId'].value_counts())
        num_teams.columns = ['num_teams']
        num_teams.index.name = 'Id'
        return num_teams

    def duration(self):
        competition_date = self.competition[ ['Id','DateEnabled', 'Deadline'] ]
        competition_date['Duration'] = competition_date.apply(lambda row:
                                                              self.calculate_duration(row['DateEnabled'], row['Deadline']),
                                                              axis=1)
        duration = competition_date[ ['Id', 'Duration'] ].set_index('Id')
        return duration

    def reward_type(self):
        reward = self.competition[['Id','RewardTypeId']]
        reward.set_index('Id',inplace=True)
        reward = pd.get_dummies(reward['RewardTypeId'])
        reward.columns = ['USD', 'Kudos', 'Jobs', 'Swag', 'Knowledge']
        return reward

    def host_segment(self):
        competition_host_segment = self.competition[['Id','CompetitionHostSegmentId']]
        competition_host_segment.set_index('Id',inplace=True)
        competition_host_segment = pd.get_dummies(competition_host_segment['CompetitionHostSegmentId'])
        competition_host_segment.columns = ['featured', 'research', 'recruitment', 'prospect', 'getting started', 'ge', 'playground']
        return competition_host_segment

    def max_daily_submissions(self):
        max_daily = self.competition[['Id','MaxDailySubmissions']]
        max_daily.set_index('Id',inplace=True)
        return max_daily

    def competing_competitions(self):
        competing_competitions = pd.read_csv("data/CompetingCompetitions.csv")
        competing_competitions = competing_competitions[['CompetitionId', 'CompetingCompetitions']]
        competing_competitions.columns = ['CompetitionId', 'ParallelCompetitions']
        competing_competitions.set_index('CompetitionId', inplace=True)
        return competing_competitions

    def top_kagglers(self):
        top_kagglers = pd.read_csv("data/PowerUsers.csv")
        top_kagglers.set_index('CompetitionId', inplace=True)
        return top_kagglers

    #combine all the features and return
    def get_features(self):
        competitions = self.competition
        competitions = competitions[['Id', 'UserRankMultiplier', 'DataSizeBytes', 'RewardQuantity']].set_index('Id')

        competitions = pd.merge(competitions, self.reward_type(), how='outer', right_index=True, left_index = True)
        competitions = pd.merge(competitions, self.duration(), how='outer', right_index=True, left_index = True)
        competitions = pd.merge(competitions, self.host_segment(), how='outer', right_index=True, left_index = True)
        competitions = pd.merge(competitions, self.max_daily_submissions(), how='outer', right_index=True, left_index = True)
        competitions = pd.merge(competitions, self.competing_competitions(), how='outer', right_index=True, left_index = True)
        
        # INNER Join, Competitions with no competitors are not of interest
        competitions = pd.merge(competitions, self.top_kagglers(), how='inner', right_index=True, left_index = True)

        return competitions

    def calculate_duration(self, register, deadline):
        _format = '%Y-%m-%d %H:%M:%S'
        timestamp = (datetime.strptime(deadline, _format) -
                     datetime.strptime(register, _format)).days
        return timestamp

    def save_to_csv(self):
        output = self.get_features()
        output.to_csv('./competition_features.csv',encoding='utf-8')

if __name__ == '__main__':
    print("Constructing Competitions Table")
    data = competitions_feature('./data')
    competitions = data.get_features()
    print(competitions.head(5))
    PATH='./data/competitions.csv'
    competitions.to_csv(PATH, index_label='CompetitionId', encoding='utf-8')
    print("Competition Table written to", PATH)

