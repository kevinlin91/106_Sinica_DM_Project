# -*- coding: utf-8 -*-

import pandas as pd

from datetime import datetime
from handle_sqlite import sqlite_data_handler

class featureExtractor(object):
    def __init__(self, data):
        self.user = data.table_Users
        self.forummessage = data.table_ForumMessages
        self.teammembership = data.table_TeamMemberships
        self.submission = data.table_Submissions
        self.competitions = data.table_Teams

    def numPosts(self):
        user_posts = pd.DataFrame(self.forummessage['AuthorUserId'].value_counts())
        user_posts.columns = ['NumPosts']
        return user_posts

    def numCompetitions(self):
        # Teams are unique for competitions
        user_competitions = pd.DataFrame(self.teammembership['UserId'].value_counts())
        user_competitions.columns = ['NumCompetitions']
        return user_competitions

    def numSubmissions(self):
        submissions = pd.DataFrame(self.submission['TeamId'].value_counts())
        submissions.columns = ['count']
        teams = pd.DataFrame(self.teammembership)[['TeamId', 'UserId']]
        user_submissions = pd.merge(submissions, teams, left_index=True, right_on='TeamId')
        user_submissions['NumSubmissions'] = user_submissions.groupby(['UserId'])['count'].transform('sum')
        user_submissions = user_submissions[['UserId', 'NumSubmissions']].drop_duplicates('UserId', keep='first').set_index('UserId')
        return user_submissions

    def durationTillActivity(self):
        # Get first team submission
        submission_dates = self.submission[['TeamId', 'DateSubmitted']]
        submission_dates = submission_dates.sort_values(by='DateSubmitted')
        submission_dates = submission_dates.drop_duplicates('TeamId', keep='first').set_index('TeamId')

        # Assign first team submission to user
        teams = pd.DataFrame(self.teammembership)[['TeamId', 'UserId']]
        user_submission_dates = pd.merge(teams, submission_dates, how='outer', right_index=True, left_on='TeamId')
        # Drop submissions that can not be assigned to a user. (More submissions than teams)
        user_submission_dates = user_submission_dates[user_submission_dates['UserId'].notnull()]
        user_submission_dates = user_submission_dates[['UserId', 'DateSubmitted']].set_index('UserId')
        user_submission_dates.columns = ['FirstSubmission']

        # Calculate Duration between user register date and first submission
        users = self.user[['Id', 'RegisterDate']]
        user_dates = pd.merge(user_submission_dates, users, left_index=True, right_on='Id')
        user_dates = user_dates.sort_values(by='FirstSubmission').drop_duplicates('Id', keep='first')
        user_dates['DaysTillActivity'] = user_dates.apply(lambda row: calcDuration(row['RegisterDate'], row['FirstSubmission']), axis=1)

        # Time On Kaggle
        dbDate = '2016-04-21 00:00:00'
        user_dates['DaysOnKaggle'] = user_dates.apply(lambda row: calcDuration(row['RegisterDate'], dbDate), axis=1)
        user_duration = user_dates[['Id', 'DaysTillActivity', 'DaysOnKaggle']].set_index('Id')

        # Drop neg. duration, when submission date is earlier then registration date
        user_duration.loc[(user_duration.DaysTillActivity < 1), 'DaysTillActivity'] = 0
        # Less then one day is 0
        user_duration.loc[(user_duration.DaysOnKaggle < 1), 'DaysOnKaggle'] = 1
        return user_duration

    def user_scores(self):
        user_scores = pd.read_csv("data/UserScores.csv")
        user_scores = user_scores[['UserId', 'UserPoints', 'UserPointsMultiplier']].set_index('UserId')
        user_scores.columns = ['Points', 'PointsM']
        return user_scores

    def calc_timely_features(self, users):
        users.loc[(users.PointsM.notna() & (users.DaysOnKaggle != 0)), 'PointsPerWeek'] = (users.PointsM/users.DaysOnKaggle)*7
        users.loc[((users.NumCompetitions != 0) & (users.DaysOnKaggle != 0)), 'CompetitionsPerWeek'] = (users.NumCompetitions/users.DaysOnKaggle)*7
        users.loc[((users.NumPosts != 0) & (users.DaysOnKaggle != 0)), 'PostsPerWeek'] = (users.NumPosts/users.DaysOnKaggle)*7
        users.loc[(users.NumCompetitions.notna() & users.NumSubmissions.notna()), 'SubmissionsPerCompetition'] = (users.NumSubmissions/users.NumCompetitions)
        return users

    def user_features(self):
        users = self.user[['Id', 'DisplayName']].set_index('Id')
        users = pd.merge(users, self.numPosts(), how='outer', right_index = True, left_index = True)
        users = pd.merge(users, self.numCompetitions(), how='outer', right_index = True, left_index = True)
        users = pd.merge(users, self.numSubmissions(), how='outer', right_index = True, left_index = True)
        users = pd.merge(users, self.durationTillActivity(), how='outer', right_index = True, left_index = True)
        users = pd.merge(users, self.user_scores(), how='outer', right_index = True, left_index = True)
        users = self.calc_timely_features(users)
        return users

def calcDuration(a, b):
    _format = '%Y-%m-%d %H:%M:%S'
    a = datetime.strptime(a, _format)
    b = datetime.strptime(b, _format)
    duration = round(((b - a).total_seconds()/(86400)),2)
    return(duration)

if __name__ == '__main__':
    data = sqlite_data_handler("./data")
    extractor = featureExtractor(data)
    users = extractor.user_features()
    #print(users.head(5))
    print(users.describe())
    #print(users.loc[users.SubmissionsPerCompetition > 50,])

