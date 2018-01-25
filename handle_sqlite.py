# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import pickle
import os

class sqlite_data_handler(object):
    def __init__(self, path_root=''):
        self.path_root = path_root
        self.filename = 'database.sqlite'
        self.data_file_path = os.path.join(path_root,self.filename)
        self.conn = sqlite3.connect(self.data_file_path)
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()
        self.tablenames = [ x[0] for x in tables]
        self.data_table_path = [ os.path.join(path_root,tablename+'.pickle') for tablename in self.tablenames ]
        
        try:
            self.table_CompetitionHostSegments = pd.read_pickle(self.data_table_path[0])
            self.table_Competitions = pd.read_pickle(self.data_table_path[1])
            self.table_Datasets = pd.read_pickle(self.data_table_path[2])
            self.table_DatasetVersions = pd.read_pickle(self.data_table_path[3])
            self.table_EvaluationAlgorithms = pd.read_pickle(self.data_table_path[4])
            self.table_Forums = pd.read_pickle(self.data_table_path[5])
            self.table_ForumMessages = pd.read_pickle(self.data_table_path[6])
            self.table_ForumTopics = pd.read_pickle(self.data_table_path[7])
            self.table_RewardTypes = pd.read_pickle(self.data_table_path[8])
            self.table_Scripts = pd.read_pickle(self.data_table_path[9])
            self.table_ScriptLanguages = pd.read_pickle(self.data_table_path[10])
            self.table_ScriptProjects = pd.read_pickle(self.data_table_path[11])
            self.table_ScriptRuns = pd.read_pickle(self.data_table_path[12])
            self.table_ScriptRunOutputFiles = pd.read_pickle(self.data_table_path[13])
            self.table_ScriptRunOutputFileExtensions = pd.read_pickle(self.data_table_path[14])
            self.table_ScriptRunOutputFileGroups = pd.read_pickle(self.data_table_path[15])
            self.table_ScriptVersions = pd.read_pickle(self.data_table_path[16])
            self.table_ScriptVotes = pd.read_pickle(self.data_table_path[17])
            self.table_Sites = pd.read_pickle(self.data_table_path[18])
            self.table_Users = pd.read_pickle(self.data_table_path[19])
            self.table_Submissions = pd.read_pickle(self.data_table_path[20])
            self.table_TeamMemberships = pd.read_pickle(self.data_table_path[21])
            self.table_Teams = pd.read_pickle(self.data_table_path[22])
            self.table_ValidationSets = pd.read_pickle(self.data_table_path[23])
        except:
            self.convert()
            pass

    def get_header(self, table_data):
        return list(table_data.columns.values)
        
    def query(self, q):
        c = self.conn.cursor()
        try:
            c.execute(q)
            return c.fetchall()
        except sqlite3.Error as e:
            print(e)

    def convert(self):
        print ("no pickle file, start to load database")
        
        self.table_CompetitionHostSegments = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[0], self.conn)
        self.table_CompetitionHostSegments.to_pickle(self.data_table_path[0])
            
        self.table_Competitions = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[1], self.conn)
        self.table_Competitions.to_pickle(self.data_table_path[1])
            
        self.table_Datasets = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[2], self.conn)
        self.table_Datasets.to_pickle(self.data_table_path[2])
            
        self.table_DatasetVersions = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[3], self.conn)
        self.table_DatasetVersions.to_pickle(self.data_table_path[3])
          
        self.table_EvaluationAlgorithms = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[4], self.conn)
        self.table_EvaluationAlgorithms.to_pickle(self.data_table_path[4])
            
        self.table_Forums = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[5], self.conn)
        self.table_Forums.to_pickle(self.data_table_path[5])
                        
        self.table_ForumMessages = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[6], self.conn)
        self.table_ForumMessages.to_pickle(self.data_table_path[6])
            
        self.table_ForumTopics = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[7], self.conn)
        self.table_ForumTopics.to_pickle(self.data_table_path[7])
            
        self.table_RewardTypes = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[8], self.conn)
        self.table_RewardTypes.to_pickle(self.data_table_path[8])
            
        self.table_Scripts = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[9], self.conn)
        self.table_Scripts.to_pickle(self.data_table_path[9])
            
        self.table_ScriptLanguages = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[10], self.conn)
        self.table_ScriptLanguages.to_pickle(self.data_table_path[10])
            
        self.table_ScriptProjects = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[11], self.conn)
        self.table_ScriptProjects.to_pickle(self.data_table_path[11])
            
        self.table_ScriptRuns = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[12], self.conn)
        self.table_ScriptRuns.to_pickle(self.data_table_path[12])
            
        self.table_ScriptRunOutputFiles = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[13], self.conn)
        self.table_ScriptRunOutputFiles.to_pickle(self.data_table_path[13])

        self.table_ScriptRunOutputFileExtensions = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[14], self.conn)
        self.table_ScriptRunOutputFileExtensions.to_pickle(self.data_table_path[14])
            
        self.table_ScriptRunOutputFileGroups = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[15], self.conn)
        self.table_ScriptRunOutputFileGroups.to_pickle(self.data_table_path[15])

        self.table_ScriptVersions = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[16], self.conn)
        self.table_ScriptVersions.to_pickle(self.data_table_path[16])
            
        self.table_ScriptVotes = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[17], self.conn)
        self.table_ScriptVotes.to_pickle(self.data_table_path[17])
            
        self.table_Sites = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[18], self.conn)
        self.table_Sites.to_pickle(self.data_table_path[18])
            
        self.table_Users = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[19], self.conn)
        self.table_Users.to_pickle(self.data_table_path[19])
            
        self.table_Submissions = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[20], self.conn)
        self.table_Submissions.to_pickle(self.data_table_path[20])
            
        self.table_TeamMemberships = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[21], self.conn)
        self.table_TeamMemberships.to_pickle(self.data_table_path[21])
            
        self.table_Teams = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[22], self.conn)
        self.table_Teams.to_pickle(self.data_table_path[22])
            
        self.table_ValidationSets = pd.read_sql_query("SELECT * FROM %s" % self.tablenames[23], self.conn)
        self.table_ValidationSets.to_pickle(self.data_table_path[23])
    
if __name__ == '__main__':
    sqlite_data = sqlite_data_handler('I:\kaggle_meta')
    print (sqlite_data.data_file_path)
    print (sqlite_data.data_table_path[0])
    print (sqlite_data.get_header(sqlite_data.table_Users))
    print (sqlite_data.query("select count(*) from Users"))
