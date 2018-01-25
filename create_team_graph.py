import os
import pandas as pd
import itertools
import networkx as nx
from nxpd import draw
import matplotlib.pyplot as plt
import numpy as np

def create_graph(team_pickle_path, teammembership_pickle_path):
    try:
        teammemberships = pd.read_pickle(teammembership_pickle_path)
    except:
        print ('TeamMemberships.pickle path is wrong')
    try:
        team = pd.read_pickle(team_pickle_path)
    except:
        print ('Teams.pickle path is wrong')
        
    join_data = pd.merge(teammemberships, team, how='outer', left_on='TeamId', right_on='Id')[ ['TeamId', 'UserId', 'CompetitionId'] ]

    if not os.path.isdir('./data/graph'):
        os.mkdir('./data/graph')
    
    graph_data = list()
    for Id in join_data['CompetitionId'].unique():
        data = join_data.loc[ join_data[ 'CompetitionId' ] == Id]
        graph_data.append(data)

    for graph in graph_data:
        edge_list = list()
        node_list = list()
        for teamid in graph['TeamId'].unique():
            edges = graph.loc[ graph['TeamId'] == teamid]
            users = edges['UserId'].tolist()
            if len(users)>1:
                edge_list += list(itertools.combinations(users,2))
            else:
                node_list += users
        team_graph = nx.Graph()
        team_graph.add_nodes_from(node_list)
        team_graph.add_edges_from(edge_list)
        
        path = './data/graph/competition_%d.gpickle' % graph['CompetitionId'].tolist()[0]
        nx.write_gpickle(team_graph, path)

        
def create_accumulate_graph(competition_pickle_path):
    try:
        competitions = pd.read_pickle(competition_pickle_path)
    except:
        print ('Competitions.pickle path is wrong')
    if not os.path.isdir('./data/graph'):
        print ('Please run create_graph() first')
    if not os.path.isdir('./data/accumulate_graph'):
        os.mkdir('./data/accumulate_graph')
    
    competitions_order = competitions[ ['Id', 'Deadline'] ].set_index('Id')
    competitions_order = competitions_order.apply(pd.to_datetime)
    competitions_order.sort_values(by='Deadline',inplace=True)
    orders = competitions_order.index.tolist()
    G = nx.Graph()
    for order in orders:
        path = './data/graph/competition_%d.gpickle'%order
        if os.path.exists(path):
            tmp_G = nx.read_gpickle(path)
            G.add_nodes_from(tmp_G.nodes)
            G.add_edges_from(tmp_G.edges)
            output_path = './data/accumulate_graph/competition_accumulate_%d.gpickle'%order
            nx.write_gpickle(G,output_path)
            

    
if __name__ == '__main__':
    #create_graph('../Teams.pickle', '../TeamMemberships.pickle')
    create_accumulate_graph('../Competitions.pickle')
