from pyclustering.cluster import cluster_visualizer
from pyclustering.cluster.xmeans import xmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.utils import read_sample
from pyclustering.samples.definitions import SIMPLE_SAMPLES

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
        normalized_x.append((data_x[i]-xmin)/(xmax-xmin))
        normalized_y.append((data_y[i]-ymin)/(ymax-ymin))

    normalized = []

    for i in range(len(normalized_x)):
        normalized.append([normalized_x[i],normalized_y[i]])
    return normalized

def xmeans_clustering(data, max_count):

    data = normalize(data)
    amount_initial_centers = 5

    initial_centers = kmeans_plusplus_initializer(data, amount_initial_centers).initialize()

    xmeans_instance = xmeans(data, initial_centers, tolerance=0.025, kmax=50, ccore=False)

    xmeans_instance.process()


    clusters = xmeans_instance.get_clusters()
    centers = xmeans_instance.get_centers()

    print(f"number of clusters: {len(clusters)}")
    clusters_count = len(clusters)

    return clusters, clusters_count
