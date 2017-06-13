from sklearn.metrics.cluster import (
    entropy,
    homogeneity_score,
    completeness_score,
    v_measure_score,
    adjusted_rand_score,
    adjusted_mutual_info_score,
    normalized_mutual_info_score,
    mutual_info_score,
    fowlkes_mallows_score,
    calinski_harabaz_score,
    silhouette_score
)
from sklearn.metrics.classification import (
    precision_score, recall_score,
    f1_score, accuracy_score
)
from texch.utils import already_run, true_labels_set
from texch.decorators import cached_property


class ExperimentMixin(object):

    scores = ()

    def __init__(self, true_labels, verbose_name):
        self._true_labels = None
        self.verbose_name = verbose_name
        self._is_run = False
        self._result = None
        self.set_true_labels(true_labels)

    def set_true_labels(self, true_labels):
        self._true_labels = true_labels

    @property
    def true_labels(self):
        return self._true_labels

    @property
    def spent(self):
        raise NotImplementedError

    @property
    def total_spent(self):
        raise NotImplementedError

    @property
    def is_run(self):
        return self._is_run

    def run(self):
        raise NotImplementedError

    @property
    def result(self):
        already_run(self)
        return self._result

    def compute_score(self, *args, **kwargs):
        return self.result.compute_score(*args, **kwargs)

    def compute_scores(self, *args, **kwargs):
        return self.result.compute_scores(*args, **kwargs)

    def plot_scores(self, *args, **kwargs):
        return self.result.plot_scores(*args, **kwargs)

    def summary(self, html=False):
        return self.result.summary(html)


class ClusteringScoresMixin(object):

    @cached_property
    def entropy(self):
        already_run(self)
        return entropy(self.get_labels())

    @cached_property
    def homogeneity(self):
        already_run(self)
        true_labels_set(self)
        return homogeneity_score(self.true_labels, self.get_labels())

    @cached_property
    def v_measure(self):
        already_run(self)
        true_labels_set(self)
        return v_measure_score(self.true_labels, self.get_labels())

    @cached_property
    def adj_rand_index(self):
        already_run(self)
        true_labels_set(self)
        return adjusted_rand_score(self.true_labels, self.get_labels())

    @cached_property
    def silhouette_coefficient(self):
        already_run(self)
        true_labels_set(self)
        return silhouette_score(self.preprocessed_data, self.get_labels())

    @cached_property
    def completeness(self):
        already_run(self)
        true_labels_set(self)
        return completeness_score(self.true_labels, self.get_labels())

    @cached_property
    def adjusted_mutual_info_score(self):
        already_run(self)
        true_labels_set(self)
        return adjusted_mutual_info_score(self.true_labels, self.get_labels())

    @cached_property
    def normalized_mutual_info_score(self):
        already_run(self)
        true_labels_set(self)
        return normalized_mutual_info_score(self.true_labels, self.get_labels())

    @cached_property
    def mutual_info_score(self):
        already_run(self)
        true_labels_set(self)
        return mutual_info_score(self.true_labels, self.get_labels())

    @cached_property
    def fowlkes_mallows_score(self):
        already_run(self)
        true_labels_set(self)
        return fowlkes_mallows_score(self.true_labels, self.get_labels())

    @cached_property
    def calinski_harabaz_score(self):
        already_run(self)
        true_labels_set(self)
        return calinski_harabaz_score(self.preprocessed_data, self.get_labels())


class ClassificationScoresMixin(object):
    @cached_property
    def precision_score(self):
        already_run(self)
        true_labels_set(self)
        return precision_score(self.true_labels, self.get_labels())

    @cached_property
    def recall_score(self):
        already_run(self)
        true_labels_set(self)
        return recall_score(self.true_labels, self.get_labels())

    @cached_property
    def f1_score(self):
        already_run(self)
        true_labels_set(self)
        return f1_score(self.true_labels, self.get_labels())

    @cached_property
    def accuracy_score(self):
        already_run(self)
        true_labels_set(self)
        return accuracy_score(self.true_labels, self.get_labels())
