from competition_preprocessing import compPreProcessor

import pandas as pd
import os
import networkx as nx
import pickle
import matplotlib.pyplot as plt
import numpy as np


def power_user_id(teammembership_pickle_path, team_pickle_path, competition_pickle_path, user_pickle_path):

    teammemberships = pd.read_pickle(teammembership_pickle_path)
    team = pd.read_pickle(team_pickle_path)
    competitions = pd.read_pickle(competition_pickle_path)
    users = pd.read_pickle(user_pickle_path)

    team_competitions = pd.DataFrame(team)[['Id','CompetitionId']]
    team_competitions.columns = ['TeamId', 'CompetitionId']
    team_members = pd.DataFrame(teammemberships)[['TeamId','UserId']]    
    user_id = pd.merge(team_competitions, team_members, left_on='TeamId', right_on='TeamId')
    
    highest_rank = pd.DataFrame(users)[['Id','HighestRanking']]
    user_rank_competition = pd.merge(user_id, highest_rank, left_on='UserId', right_on='Id')
    
    competition_unique = user_rank_competition['CompetitionId'].unique()

    if not os.path.isdir('./data/power_userid'):
        os.mkdir('./data/power_userid')
    for competition in competition_unique:
        unique_user = user_rank_competition[ user_rank_competition['CompetitionId']==competition]
        unique_user = unique_user[ ['UserId', 'HighestRanking'] ]
        path = ('./data/power_userid/%d.csv')%competition
        unique_user.to_csv(path, index=False)


def get_user(competition_id):
    path = './data/power_userid/%d.csv' % competition_id
    user = pd.read_csv(path)
    return user
    

def topk_user_id(user, k):
    topk = user[ user['HighestRanking']<k ]['UserId'].sort_values().tolist()
    return topk

def get_competition_sortby_deadline(competition_pickle_path):
    competitions = pd.read_pickle(competition_pickle_path)
    competitions_order = competitions[ ['Id', 'Deadline'] ].set_index('Id')
    competitions_order = competitions_order.apply(pd.to_datetime)
    competitions_order.sort_values(by='Deadline',inplace=True)
    orders = competitions_order.index.tolist()

    return orders

def get_competition_withUSD(competition_pickle_path):
    competition = compPreProcessor().get_competitions()
    USD_id = list(competition.loc[competition.USD == 1].index)    
    competitions = pd.read_pickle(competition_pickle_path)
    competitions_order = competitions[ ['Id', 'Deadline'] ].set_index('Id')
    competitions_order = competitions_order.apply(pd.to_datetime)
    competitions_order.sort_values(by='Deadline',inplace=True)
    orders = competitions_order.index.tolist()
    new_orders = [ a for a in orders if a in USD_id]
    
    return new_orders


def draw(comps, user, feature,degree):
    length = np.arange(len(comps))
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0], fig_size[1] = 16.0, 12.0
    plt.rcParams["figure.figsize"] = fig_size
    plt.figure(1)
    plt.title(user)
    plt.subplot(211)
    plt.plot(length, feature)
    plt.xticks(length, comps, rotation=70)
    plt.yticks(np.arange(0,1.1,0.1))
    plt.title('Local clustering coefficient')
    plt.subplot(212)
    plt.plot(length, degree, color='r')
    plt.xticks(length, comps, rotation=70)
    #plt.yticks(np.arange(0,1.1,0.1))
    plt.title('Degree')
    plt.suptitle(user)
    plt.savefig('./image/%d.png'%user)
    #plt.show()
    plt.clf()


def networks():
    competition_path = './data/power_userid/'
    competition_id = [int(_id.split('.')[0]) for _id in os.listdir(competition_path)]
    u2c = dict()
    sort_competition_id = get_competition_sortby_deadline('../Competitions.pickle')
    try:
        u2c = pickle.load(open('u2c.pickle','rb'))
    except:
        k = 10
        for _id in competition_id:
            user_ids = topk_user_id( get_user(_id), k)
            for user_id in user_ids:
                if not user_id in u2c:
                    u2c[user_id] = [_id]
                else:
                    u2c[user_id].append(_id)
        for comp_list in u2c:
            original = u2c[comp_list]
            new = sorted(original, key=lambda x: sort_competition_id.index(x))
            u2c[comp_list] = new
        pickle.dump(u2c, open('u2c.pickle','wb'))
    user_list = list(u2c.keys())
    for user in user_list:
        comps = u2c[user]
        degree = list()
        local_clustering = list()
        for comp in u2c[user]:
            path = './data/accumulate_graph/competition_accumulate_%d.gpickle'%comp
            G = nx.read_gpickle(path)
            #degree.append(nx.degree_centrality(G)[user])
            degree.append(G.degree(user))
            local_clustering.append(nx.clustering(G,user))
        #print (degree)
        draw(comps,user,local_clustering,degree)

def draw_global(competition_id, top_gcc, nontop_gcc):
    length = np.arange(len(competition_id))
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0], fig_size[1] = 100.0, 20.0
    plt.rcParams["figure.figsize"] = fig_size
    plt.figure(1)
    plt.plot(length, top_gcc, color='b', label='top')
    plt.plot(length, nontop_gcc, color='r', label='nontop')
    plt.xticks(length, competition_id, rotation=90)
    plt.yticks(np.arange(0,0.4,0.1))
    ax = plt.gca()
    ax.tick_params(axis = 'y', which = 'major', labelsize = 24)
    ax.tick_params(axis = 'x', which = 'major', labelsize = 10, width=2)
    plt.legend()
    plt.show()
    #plt.savefig('./image/top_vs_nontop.png')


def nx2gexf(G, top_users, nontop_users,index):
    for user in top_users:
        G.node[user]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
    for user in nontop_users:
        G.node[user]['viz'] = {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}}
    nx.write_gexf(G, "%d.gexf" % index, version="1.2draft")
    

def network_global():
    competition_path = './data/power_userid/'
    competition_id = get_competition_withUSD('../Competitions.pickle')
    k = 100
    top_gcc = list()
    nontop_gcc = list()
    competition = list()
    top_users = list()
    non_top_users = list()
    for index, _id in enumerate(competition_id):
    #for _id in competition_id[:1]:
        graph_path = './data/accumulate_graph/competition_accumulate_%d.gpickle'%_id
        G = nx.read_gpickle(graph_path)
        all_users = G.nodes()
        tmp_top_users = topk_user_id( get_user(_id), k)
        top_users = list(set().union(top_users,tmp_top_users))
        nontop_users = list(set().union(non_top_users,list(set(all_users) - set(tmp_top_users))))
        if (len(top_users)!=0):
            top_gcc.append(nx.average_clustering(G,top_users))
            nontop_gcc.append(nx.average_clustering(G,nontop_users))
            competition.append(_id)
        if index==int(len(competition_id)/4) or index == int(len(competition_id)/2) or index == len(competition_id)-1:
            nx2gexf(G, top_users, nontop_users, _id)
        
        
            
    draw_global(competition, top_gcc, nontop_gcc)
        
        
    
    

        
        
if __name__ == '__main__':
    if not os.path.isdir('./data/power_userid'):
        power_user_id('../TeamMemberships.pickle', '../Teams.pickle', '../Competitions.pickle', '../Users.pickle')
    #user = get_user(2435)
    #topk = topk_user_id(user,10)
    #print (topk)
    #c = get_competition_sortby_deadline('../Competitions.pickle')
    #networks()
    network_global()
    
