import itertools
import logging
import time

import pandas as pd
import numpy as np

from texch.mixins import (
    ExperimentMixin, ClusteringScoresMixin,
    ClassificationScoresMixin
)
from texch.utils import already_run
from texch.clustering.base import BaseClusterer
from texch.classification.base import BaseClassifier
from texch.exceptions import NoInputDataException, NoMethodSetException


class SingleExperimentResult(object):
    def __init__(self, experiment, extra_info=None):
        self.experiment = experiment
        self.extra_info = extra_info or ''
        self._df = pd.DataFrame(
            {
                'ExperimentID': experiment.id,
                'ExperimentName': experiment.verbose_name,
                'PreprocessorSpent': experiment.preprocessor.total_spent,
                'PrepareFuncSpent': experiment.prepare_func_spent,
                'MethodSpent': experiment.method.spent,
                'TotalSpent': experiment.total_spent
            },
            index=np.arange(1)
        )

    def __getattr__(self, item):
        return getattr(self._df, item)

    def __getitem__(self, val):
        return self._df.__getitem__(val)

    @property
    def spent(self):
        return self.experiment.spent

    @property
    def info(self):
        return """
            Experiment name:  {name}.\n
            Preprocessor: {preprocessor}\n
            Method: {method}\n
        """.format(
            name=self.experiment.verbose_name,
            preprocessor=self.experiment.preprocessor,
            method=self.experiment.method
        )

    def compute_score(self, score):
        error = None

        try:
            score_result = getattr(self.experiment, score, None)
            if score_result is None:
                error = 'Such score does not supported'
        except Exception as err:
            error = err
            score_result = None

        if error is None:
            self._df[score] = [score_result]
        else:
            logging.warning(
                'Cannot compute score {0}. Error: {1}. Available scores: {2}\n'.format(
                    score,
                    repr(error),
                    self.experiment.scores
                )
            )

        return score_result

    def compute_scores(self, scores='all'):

        if scores == 'all':
            scores = self.experiment.scores
        map(self.compute_score, scores)

        return self._df

    @property
    def scores(self):
        return self._df

    @property
    def info_html(self):
        return """
            <center>
            <h1> Experiment Summary </h1><br>
            </center>
            Experiment name: <br><b>{name}</b><br>
            <ul>
            <li>
            <b>Preprocessor</b>: <br> {preprocessor}
            </li>
            <li>
            <b>Method</b>: <br>{method}
            </li>
            </ul>
        """.format(
            name=self.experiment.verbose_name,
            preprocessor=self.experiment.preprocessor._repr_html_(),
            method=self.experiment.method
        )

    @property
    def total_spent(self):
        return self.experiment.spent

    def _repr_html_(self):
        return self.summary(html=True)

    def summary(self, html=False):

        if not html:
            return self.__repr__()

        info_text = self.info_html

        if self.extra_info is not None:
            info_text += '<br>' + self.extra_info.replace('\n', '<br>')

        info_text += '<br><br>Computed scores:<br><br>' \
                     + self._df._repr_html_()

        return info_text

    def __repr__(self):

        info_text = self.info

        if self.extra_info is not None:
            info_text = '\n\n' + self.extra_info

        return info_text + '\n\nScores:\n\n' + unicode(self._df)

    __str__ = __repr__


class SingleExperiment(ExperimentMixin):

    _ids = itertools.count(0)
    method_class = object

    def __init__(self, data=None, method=None, preprocessor=None,
                 true_labels=None, verbose_name=None, prepare_func=None):
        if not isinstance(method, self.method_class):
            raise AttributeError(
                'method should be a subclass of {0}'.format(
                    self.method_class
                )
            )
        self._input_data = data
        self.preprocessor = preprocessor
        self.method = method
        self.preprocessed_data = None
        self.preprocessed_features = None
        self._result = None
        super(SingleExperiment, self).__init__(
            true_labels,
            verbose_name or
            '\nPreprocessor: ' + repr(preprocessor) +
            '\nMethod: ' + repr(method)
        )
        self.id = self._ids.next()
        self.prepare_func = prepare_func
        self.prepare_func_spent = 0

    @property
    def data(self):
        return self._input_data

    def set_input_data(self, data):
        self._input_data = data

    @property
    def spent(self):
        already_run(self)
        return {
            'preprocessor': self.preprocessor.spent,
            'prepare_function': self.prepare_func_spent,
            'method': self.method.spent
        }

    @property
    def total_spent(self):
        already_run(self)
        return (
            self.method.spent +
            self.preprocessor.total_spent +
            self.prepare_func_spent
        )

    def run_method(self, data):
        logging.info('Running method...')

        result = self.method.run(data)
        logging.info('Finished method in %s sec', self.method.spent)
        return result

    def run(self):
        if self._input_data is None:
            raise NoInputDataException
        if self.method is None:
            raise NoMethodSetException
        logging.info('Running experiment "{0}"...'.format(self))
        if self.preprocessor is not None:
            self.run_preprocessing()
            data = self.preprocessed_data
        else:
            data = self._input_data
        if self.prepare_func is not None:
            logging.debug('Running in-middle prepare function...')
            start_time = time.time()
            data = self.preprocessed_data = self.prepare_func(data)
            self.prepare_func_spent = time.time() - start_time
            logging.info(
                'Finished in-middle prepare function in %s sec',
                self.prepare_func_spent
            )
        self._is_run = True
        self.run_method(data)
        self._result = SingleExperimentResult(
            experiment=self,
            extra_info=self.get_extra_info()
        )
        logging.info('Finished experiment in %s sec', self.total_spent)
        return self._result

    def run_preprocessing(self):
        logging.info('Running preprocessing...')
        self.preprocessor.set_input_data(self._input_data)
        self.preprocessor.run()
        self.preprocessed_data = self.preprocessor.result
        self.preprocessed_features = self.preprocessor.features
        logging.info('Finished preprocessing in %s', self.preprocessor.total_spent)

    def get_labels(self):
        raise NotImplementedError

    def get_extra_info(self):
        return None

    def __repr__(self):
        return (self.verbose_name or self.__class__.__name__) + ' (id={})'.format(self.id)

    __str__ = __repr__


class ClusteringExperiment(SingleExperiment, ClusteringScoresMixin):
    scores = (
        'entropy', 'homogeneity', 'v_measure',
        'adj_rand_index', 'completeness',
        'mutual_info_score', 'normalized_mutual_info_score',
        'adjusted_mutual_info_score', 'fowlkes_mallows_score'
    )
    method_class = BaseClusterer

    @property
    def is_run(self):
        return self._is_run

    def get_clusters(self):
        already_run(self)
        return self.method.clusters

    def get_labels(self):
        already_run(self)
        return self.method.labels

    def get_extra_info(self):
        labels = self.get_labels()
        clusters = self.get_clusters()
        result_text = """
            Total objects to cluster: {len_labels}\n
            Total clusters found: {len_clusters}
        """.format(
            len_labels=len(labels),
            len_clusters=len(clusters)
        )
        for num, cluster in clusters.items()[:5]:
            result_text += 'Cluster #{0}: {1} objects\n'.format(num, len(cluster))
        return result_text


class ClassificationExperiment(SingleExperiment, ClassificationScoresMixin):
    scores = (
        'precision_score', 'recall_score',
        'f1_score', 'accuracy_score'
    )
    method_class = BaseClassifier

    def get_labels(self):
        return self.method.labels

    def run_method(self, data):
        logging.info('Running method...')

        result = self.method.run(*data)
        logging.info('Finished method in %s sec', self.method.spent)
        return result

    def run(self):
        if self._input_data is None:
            raise NoInputDataException
        if self.method is None:
            raise NoMethodSetException
        logging.info('Running experiment "{0}"...'.format(self))
        if self.preprocessor is not None:
            self.run_preprocessing()
            data = self.preprocessed_data
        else:
            data = self._input_data
        if self.prepare_func is not None:
            logging.debug('Running in-middle prepare function...')
            start_time = time.time()
            data = self.preprocessed_data = self.prepare_func(data)
            self.prepare_func_spent = time.time() - start_time
            logging.info(
                'Finished in-middle prepare function in %s sec',
                self.prepare_func_spent
            )
        self._is_run = True
        self.run_method(data)
        self._result = SingleExperimentResult(
            experiment=self,
            extra_info=self.get_extra_info()
        )
        logging.info('Finished experiment in %s sec', self.total_spent)
        return self._result

    @property
    def is_run(self):
        return self._is_run

    def predict(self, data, *args, **kwargs):
        already_run(self)
        return self.method.predict(data, *args, **kwargs)
