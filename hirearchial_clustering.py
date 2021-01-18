import matplotlib.pyplot as plt
import numpy
import scipy.cluster.hierarchy as hcluster
import time

def hierarichial_cluster(data):
    thresh = 1.5
    t0 = time.time()
    clusters = hcluster.fclusterdata(data, thresh, criterion="distance")
    print(f"Hirearchial time: {time.time()-t0}")
    print(clusters)
    print(len(clusters))
    return clusters

# hierarichial_cluster(data)
