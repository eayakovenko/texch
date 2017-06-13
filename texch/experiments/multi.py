import logging

import pandas as pd

from matplotlib import pylab as plt
from texch.mixins import ExperimentMixin
from texch.utils import already_run
from .single import SingleExperiment, ClusteringExperiment, ClassificationExperiment


class MultiExperimentResult(object):
    def __init__(self, multi_experiment, extra_info=None):
        self.multi_experiment = multi_experiment
        self.extra_info = extra_info or ''
        self._df = pd.concat(
            [
                experiment.result._df[
                    [
                        'ExperimentID', 'ExperimentName',
                        'PreprocessorSpent',
                        'MethodSpent', 'TotalSpent'
                    ]
                ] for experiment in multi_experiment.experiments
            ],
            ignore_index=True
        )

    def __getattr__(self, item):
        return getattr(self._df, item)

    def __getitem__(self, val):
        return self._df.__getitem__(val)

    @property
    def spent(self):
        return self.multi_experiment.spent

    @property
    def total_spent(self):
        return self.multi_experiment.spent

    def compute_score(self, score):

        values = [
            experiment.result.compute_score(score)
            for experiment in self.multi_experiment.experiments
        ]

        self._df[score] = values

        return values

    def compute_scores(self, scores='all'):

        multi_experiment = self.multi_experiment

        if scores == 'all':
            scores = multi_experiment.scores

        map(self.compute_score, scores)

        return self._df

    def _repr_html_(self):
        return self.summary(html=True)

    @property
    def scores(self):
        return self._df

    def summary(self, html=False):
        if not html:
            return self.__repr__()

        info_text = """
        <center>
        <h1> Multi Experiment {name} </h1><br>
        <h2>Summary</h2>:
        </center>
        <b>Experiments</b>:<br>
        """.format(
            name=self.multi_experiment.verbose_name,
        )
        info_text += '<ul>' + ''.join(
            [
                '<li>{0}</li>'.format(repr(experiment))
                for experiment in self.multi_experiment.experiments
            ]
        ) + '</ul>'

        if self.extra_info is not None:
            info_text += '\n\n' + self.extra_info.replace('\n', '<br>')

        info_text += '<br><br>Computed scores:<br><br>' \
                     + self._df._repr_html_()
        return info_text

    def __repr__(self):
        info_text = """
            Multi Experiment {name}.\n
            Experiments:\n

        """.format(
            name=self.multi_experiment.verbose_name,
            experiments='\n'.join(map(str, self.multi_experiment.experiments))
        )

        if self.extra_info is not None:
            info_text += '\n\n' + self.extra_info

        return info_text + '\n\nScores:\n\n' + unicode(self._df)

    def plot_scores(
            self, columns='all',
            plots_per_row=3, kind='bar',
            legend=False,
            figsize=(10,10),
            sharex=True,
            **kwargs
    ):

        if columns == 'all':
            columns = self._df.drop(
                ['ExperimentID', 'ExperimentName'],
                axis=1
            ).columns
        fig, axes = plt.subplots(
            len(columns) // plots_per_row, plots_per_row + 1,
            figsize=figsize,
            sharex=sharex
        )
        axes = [ax for axis in axes for ax in axis]
        for col_name, ax in zip(columns, axes):
            ax = self._df.plot(
                y=col_name,
                ax=ax,
                title=col_name,
                kind=kind,
                legend=legend,
                **kwargs
            )
            ax.set_xlabel('Experiment #')
            if col_name in (
                    'PreprocessorSpent', 'MethodSpent',
                    'TotalSpent', 'PrepareFuncSpent'
            ):
                ax.set_ylabel('Seconds')
            else:
                ax.set_ylabel('Score')
        plt.tight_layout()

    def best_by(self, by):
        pass

    def fastest(self):
        ind = self._df['TotalSpent'].argmin()
        return self._df.loc[ind:ind]

    __str__ = __repr__


class MultiExperiment(ExperimentMixin):

    sub_experiment_class = SingleExperiment

    def __init__(self, data, experiments, true_labels=None, verbose_name=None):
        self._experiments = []
        self.data = data
        map(self.add_experiment, experiments)
        super(MultiExperiment, self).__init__(
            true_labels,
            verbose_name or 'MultiExperiment'
        )

    def add_experiment(self, experiment):
        if not isinstance(experiment, self.sub_experiment_class):
            raise AttributeError(
                'experiment should be a subclass of a SingleExperiment')
        experiment.set_input_data(self.data)
        self._experiments.append(experiment)

    def set_true_labels(self, true_labels):
        self._true_labels = true_labels
        for experiment in self.experiments:
            experiment.set_true_labels(true_labels)

    @property
    def spent(self):
        already_run(self)
        return {
            'Experiment #{0}: {1}'.format(num, repr(experiment)): experiment.spent
            for num, experiment in enumerate(self._experiments)
        }

    @property
    def total_spent(self):
        already_run(self)
        total = 0
        for experiment in self._experiments:
            total += experiment.total_spent
        return total

    @property
    def experiments(self):
        return self._experiments

    def run(self):
        logging.info(
            'Running multi experiment consisting of %s sub experiments',
            len(self._experiments)
        )
        for num, experiment in enumerate(self._experiments):
            logging.debug('\n' + '-' * 50)
            logging.info(
                '*****Experiment #%s*****',
                num
            )
            experiment.run()
        self._is_run = True
        self._result = MultiExperimentResult(self)
        logging.info(
            'Finished multi experiment in %s sec',
            self.total_spent
        )
        return self._result


class MultiClusteringExperiment(MultiExperiment):
    sub_experiment_class = ClusteringExperiment
    scores = ClusteringExperiment.scores

    def __repr__(self):
        return self.verbose_name or self.__class__.__name__

    __str__ = __repr__


class MultiClassificationExperiment(MultiExperiment):
    sub_experiment_class = ClassificationExperiment
    scores = ClassificationExperiment.scores

    def __repr__(self):
        return self.verbose_name or self.__class__.__name__

    __str__ = __repr__