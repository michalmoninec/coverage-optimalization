from pyclustering.cluster import cluster_visualizer
from pyclustering.cluster.xmeans import xmeans, splitting_type
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.utils import read_sample
from pyclustering.samples.definitions import SIMPLE_SAMPLES

import numpy as np


def normalize(data):
    data_x = []
    data_y = []

    for i in range(len(data)):
        data_x.append(data[i][0])
        data_y.append(data[i][1])

    xmax = max(data_x)
    xmin = min(data_x)

    ymax = max(data_y)
    ymin = min(data_y)

    normalized_x = []
    normalized_y = []

    for i in range(len(data_x)):
        # normalized_x.append((data_x[i]-xmin)/(xmax-xmin))
        # normalized_y.append((data_y[i]-ymin)/(ymax-ymin))

        normalized_x.append(data_x[i] - xmin)
        normalized_y.append(data_y[i] - ymin)

    normalized = []

    for i in range(len(normalized_x)):
        normalized.append([normalized_x[i], normalized_y[i]])
    return normalized


def xmeans_clustering(data):
    # def xmeans_clustering(data,init_count, max_count, crit_type, core_acc):

    amount_initial_centers = 2
    print(f"data for xmenas: {data}")
    initial_centers = kmeans_plusplus_initializer(
        data, amount_initial_centers
    ).initialize()

    # MINIMUM_NOISELESS_DESCRIPTION_LENGTH
    # BAYESIAN_INFORMATION_CRITERION

    xmeans_instance = xmeans(
        data,
        initial_centers,
        tolerance=0.1,
        kmax=3,
        criterion=splitting_type.BAYESIAN_INFORMATION_CRITERION,
        ccore=False,
    )

    xmeans_instance.process()

    clusters = xmeans_instance.get_clusters()
    centers = xmeans_instance.get_centers()

    print(f"Number of cluster after clustering: {len(clusters)}")
    clusters_count = len(clusters)

    return clusters, clusters_count, centers
