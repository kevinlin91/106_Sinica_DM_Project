import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import processing_utils as pu
import user_preprocessing as pp

from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

from handle_sqlite import sqlite_data_handler

class clustering(object):
    def __init__(self, data):
        # TODO: Clusterin can't handle categorical data yet
        self.data = data.select_dtypes(include=[np.number])

    def fit_kmeans(self, n_clusters=3, random_state=None):
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
        kmeans.fit(self.data)
        self.labels = kmeans.labels_
        self.data['cluster'] = self.labels
        return self.labels

    def fit_hierarchical(self, n_clusters=2, affinity='euclidean', linkage='ward'):
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters, affinity=affinity, linkage=linkage)
        hierarchical.fit(self.data)
        return hierarchical.labels_

    def visualize(self):
        data = self.data
        model = TSNE(n_components=2)
        coordinates = model.fit_transform(data)
        data['x'] = coordinates[:,0]
        data['y'] = coordinates[:,1]
        for k in np.unique(self.labels):
            points = data[(data['cluster'] == k)]
            plt.scatter(points['x'], points['y'], linewidths=0.5, s=10)
        plt.show()

    def describe(self):
        for k in np.unique(self.labels):
            cluster = self.data[(self.data['cluster'] == k)]
            print("Cluster: ", k)
            print("Median:")
            print(cluster.median())
            print("Mean:")
            print(cluster.mean())
            print("\n")

if __name__ == '__main__':
    data = sqlite_data_handler("./data")
    processor = pp.preProcessor(data)
    users = processor.get_users()

    # Select users and features to cluster upon
    users = users.loc[(users['HighestRanking'] < 200) & (users['NumSubmissions'] > 1), ['NumSubmissions', 'NumPosts', 'DaysTillActivity', 'HighestRanking']]

    # Select columns to apply log to
    users = pu.log_data(users, ['NumSubmissions', 'NumPosts'])
    print(users.describe())
    users = pu.normalize_data(users)

    # Select User features
    users = users.sample(frac=0.1)
    cluster = clustering(users)
    cluster.fit_kmeans(2)
    cluster.describe()
    cluster.visualize()
