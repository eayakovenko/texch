import nltk

from texch.classification.base import BaseClassifier
from texch.exceptions import NotCorrectEstimatorException
from texch.utils import not_proxied


class NLTKClassifier(BaseClassifier):
    def __init__(self, classifier_class, *args, **kwargs):
        if not issubclass(classifier_class, nltk.classify.api.ClassifierI):
            raise NotCorrectEstimatorException(
                'A subclass of sklearn.base.ClusterMixin is expected as cluster_class'
            )
        super(NLTKClassifier, self).__init__(classifier_class, *args, **kwargs)

    def fit(self, data, *fit_args, **fit_kwargs):
        not_proxied(self)
        if self.classifier is None:
            self.classifier = self.classifier_class(*self.args, **self.kwargs)
        self.classifier.train(data, *fit_args, **fit_kwargs)

    def predict(self, data, *predict_args, **predict_kwargs):
        not_proxied(self)
        self.labels = self.classifier.classify(data)
        return self.labels
