import nltk

from collections import defaultdict

from texch.clustering.base import BaseClusterer
from texch.exceptions import NotCorrectEstimatorException
from texch.utils import not_proxied


class NLTKClusterer(BaseClusterer):
    def __init__(self, cluster_class, *args, **kwargs):
        if not issubclass(cluster_class, nltk.cluster.VectorSpaceClusterer):
            raise NotCorrectEstimatorException(
                'A subclass of nltk.cluster.VectorSpaceClusterer is expected as cluster_class'
            )
        super(NLTKClusterer, self).__init__(cluster_class, *args, **kwargs)

    def fit(self, data, *fit_args, **fit_kwargs):
        not_proxied(self)
        # skrearn clustering algorithms do not expect fit args and kwargs
        if self.clusterer is None:
            self.clusterer = self.cluster_class(*self.args, **self.kwargs)
        fit_kwargs.setdefault('assign_clusters', True)
        labels = self.clusterer.cluster(data, *fit_args, **fit_kwargs)
        if fit_kwargs.get('assign_clusters'):
            self.labels = labels
        else:
            self.labels = [self.clusterer.classify(vector) for vector in data]
        clusters = defaultdict(list)
        for ind, cluster in enumerate(self.labels):
            clusters[cluster].append(ind)
        self.clusters = clusters
