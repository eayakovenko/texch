import sklearn
import numpy as np

from collections import defaultdict

from texch.clustering.base import BaseClusterer
from texch.exceptions import NotCorrectEstimatorException
from texch.utils import not_proxied


class SklearnClusterer(BaseClusterer):
    def __init__(self, cluster_class, *args, **kwargs):
        if not issubclass(cluster_class, sklearn.base.ClusterMixin):
            raise NotCorrectEstimatorException(
                'A subclass of sklearn.base.ClusterMixin is expected as cluster_class'
            )
        super(SklearnClusterer, self).__init__(cluster_class, *args, **kwargs)

    def fit(self, data, *fit_args, **fit_kwargs):
        not_proxied(self)
        # skrearn clustering algorithms do not expect fit args and kwargs
        if self.clusterer is None:
            self.clusterer = self.cluster_class(*self.args, **self.kwargs)
        self.clusterer.fit(data)
        if hasattr(self.clusterer, 'labels_'):
            self.labels = self.clusterer.labels_.astype(np.int)
        else:
            self.labels = self.clusterer.predict(data)
        clusters = defaultdict(list)
        for ind, cluster in enumerate(self.labels):
            clusters[cluster].append(ind)
        self.clusters = clusters
