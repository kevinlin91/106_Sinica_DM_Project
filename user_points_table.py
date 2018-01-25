#!/usr/bin/env python

# A program to compute points earned by users in competitions
# Information is stored in the database in table UserPoints
# Columns are UserId (INTEGER), CompetitionId (INTEGER), Points (REAL)
# Points is the number of points earned by UserId in competition CompetitionId
#
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import sys

from handle_sqlite import sqlite_data_handler

def computePoints(db):
    user_points = pd.read_sql_query("""SELECT TeamMemberships.UserId, TeamMemberships.TeamId,
                             Competitions.Id as CompetitionId, Competitions.UserRankMultiplier, COUNT(Distinct(Submissions.Id)) as NSubs, Teams.Ranking
                             FROM Teams JOIN TeamMemberships ON Teams.Id = TeamMemberships.TeamId
                             JOIN Competitions ON Competitions.Id = Teams.CompetitionId
                             JOIN Submissions ON Submissions.TeamId = Teams.Id
                             GROUP By TeamMemberships.TeamId, TeamMemberships.UserId ORDER BY TeamMemberships.UserId """, db.conn)

    # teamSizes[teamId] holds the number of members in team teamId
    teamSizes = user_points.groupby(['TeamId']).agg({'UserId': 'nunique'}).to_dict()["UserId"]
    # competingTeams[competitionId] holds the number of teams competing in competition competitionId
    competingTeams = user_points.groupby(['CompetitionId']).agg({'TeamId': 'nunique'}).to_dict()["TeamId"]

    # The Kaggle formula, but WITHOUT decay
    def kagglePoints(teamSize, rank, nTeams, multiplier):
        return 100000.0/math.sqrt(teamSize) * math.pow(rank, -0.75) * math.log10(1 + math.log10(nTeams)) * multiplier

    user_points['Points'] = user_points.apply(lambda row: kagglePoints(teamSizes[row['TeamId']], row['Ranking'],
                                                                competingTeams[row['CompetitionId']], row['UserRankMultiplier']), axis=1)

    # Only interest in users/competitions where points have been made
    user_points = user_points.loc[user_points.Points > 0,]
    return user_points

def writeToDB(db, user_points):
    print("Writing to Database...")
    user_points[['UserId', 'CompetitionId', 'Points']].to_sql('UserPoints', db.conn, if_exists='replace')
    db.conn.commit()
    print("Wrote on Database: ")
    print(pd.read_sql_query("select * from UserPoints;", db.conn).head(4))

def user_comp_matrix(points):
    users = points.UserId.unique()
    comps = points.CompetitionId.sort_values().unique()
    m = pd.DataFrame(np.zeros((len(users), len(comps))))
    m.columns = comps
    m.index = users

    def to_matrix(row):
        m.loc[row.UserId, row.CompetitionId] = row.Points + sum(m.loc[row.UserId,])

    points = points.sort_values(['CompetitionId', 'UserId'])
    points.apply(to_matrix, axis=1)
    return m

if __name__ == '__main__':
    db = sqlite_data_handler('data')
    print("Computing Points...")
    points = computePoints(db)
    comps = points.groupby(['CompetitionId']).agg({'Points': 'sum', 'UserId': 'nunique', 'UserRankMultiplier': 'median'})

    # TODO: User Comp matrix with aggregated User Counts
    # TODO: 2. aggregated user counts have to be normalized? Mean better?
    m = user_comp_matrix(points)
    print(m)
    
    # comps['UserScores'] = m.sum()
    # print(m.sum())
    
    # plt.plot(comps.UserScores, 'ro')
    # plt.show()

    #writeToDB(db, user_points)
    db.conn.close()
