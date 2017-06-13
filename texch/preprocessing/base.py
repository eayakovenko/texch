import time
import itertools
import logging

from texch.utils import already_run, not_proxied
from texch.exceptions import (
    PreprocessingException, NoInputDataException
)


class PreprocessClass(object):
    def __init__(self, process_class, preprocess_method_name, *args, **kwargs):
        self.preprocessor = None
        self.process_class = process_class
        self.preprocess_method_name = preprocess_method_name
        self._method = None
        self._is_proxy = self._is_proxy = kwargs.pop('proxy', False)
        self.args = None
        self.kwargs = None
        if not self._is_proxy:
            self._init_preprocessor(*args, **kwargs)

    def _init_preprocessor(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.preprocessor = self.process_class(*args, **kwargs)
        self._method = getattr(
            self.preprocessor,
            self.preprocess_method_name
        )

    def __call__(self, *args, **kwargs):
        if not self._is_proxy:
            raise TypeError(
                self.__class__.__name__ + ' object is not callable'
            )

        return self.__class__(
            self.process_class,
            self.preprocess_method_name,
            proxy=False,
            *args,
            **kwargs
        )

    @property
    def is_proxy(self):
        return self._is_proxy

    def __getattr__(self, item):
        if self._is_proxy or self.preprocessor is None:
            raise AttributeError
        else:
            return getattr(self.preprocessor, item)

    def as_preprocess_step(self, *args, **kwargs):
        not_proxied(self)
        return PreprocessStep(self._method, *args, **kwargs)


class PreprocessStep(object):

    _ids = itertools.count(0)

    def __init__(self, process_func, *args, **kwargs):
        self._input_data = None
        self._start_time, self._end_time = None, None
        self._input_features = None
        self._result = None
        self.features = None
        self.process_func = process_func
        self.verbose_name = kwargs.pop('verbose_name', None)
        self.args = args
        self.kwargs = kwargs
        self._is_run = False
        self.id = self._ids.next()

    def set_input_data(self, data):
        self._input_data = data

    def set_input_features(self, features):
        self._input_features = features

    @property
    def input_data(self):
        return self._input_data

    @property
    def is_run(self):
        return self._is_run

    @property
    def input_features(self):
        return self._input_features

    def get_features(self):
        already_run(self)
        return self.features

    @property
    def result(self):
        already_run(self)
        return self._result

    @property
    def spent(self):
        already_run(self)
        if not self._end_time or not self._start_time:
            return None
        return self._end_time - self._start_time

    def run(self):
        self._start_time = time.time()
        self._result = self.process(*self.args, **self.kwargs)
        self._end_time = time.time()
        self._is_run = True
        return self._result

    def process(self, *args, **kwargs):
        return self.process_func(self.input_data, *args, **kwargs)

    def __repr__(self):
        return (self.verbose_name or self.__class__.__name__) + ' (id={})'.format(self.id)

    __str__ = __repr__


class Preprocessor(object):

    def __init__(self, steps, verbose_name=None):
        self._steps = []
        map(self.add_step, steps)
        self._result = None
        self._data = None
        self.features = None
        self._is_run = False
        self.verbose_name = verbose_name

    def set_input_data(self, data):
        self._data = data

    @property
    def input_data(self):
        return self._data

    @property
    def is_run(self):
        return self._is_run

    def add_step(self, preprocessing_step):
        if not isinstance(preprocessing_step, PreprocessStep):
            raise AttributeError(
                'preprocessing_step should be a subclass of PreprocessStep'
            )
        self._steps.append(preprocessing_step)

    @property
    def steps(self):
        return self._steps

    def list_steps(self):
        return list(map(repr, self._steps))

    @property
    def spent(self):
        already_run(self)
        return {
            'Step #{0}: {1}'.format(num, repr(step)): step.spent
            for num, step in enumerate(self._steps)
        }

    @property
    def total_spent(self):
        already_run(self)
        total = 0
        for step in self._steps:
            total += step.spent
        return total

    def run(self):
        if self._data is None:
            raise NoInputDataException('Need to set_data for preprocessing')
        data = self._data
        features = self.features
        for num, step in enumerate(self._steps):
            try:
                step.set_input_data(data)
                step.set_input_features(features)
                data = step.run()
                logging.info('Step #{0}: {1}: finished in {2} sec'.format(
                        num,
                        repr(step),
                        step.spent
                    )
                )
                features = step.get_features()
            except Exception as err:
                raise PreprocessingException(
                    'Error during preprocessing step #{0}. {1}: {2}'.format(
                        num + 1,
                        step,
                        repr(err)
                    )
                )
        self._is_run = True
        self._result = data
        self.features = features
        return self._result

    @property
    def result(self):
        already_run(self)
        return self._result

    def __repr__(self):
        return self.verbose_name or \
               '\n'.join(self.list_steps())

    def _repr_html_(self):
        html_steps = '<ul>' + ''.join([
            '<li>{0}</li>'.format(step) for step in self.list_steps()
        ]) + '</ul>'
        return (self.verbose_name or html_steps).replace('\n', '<br>')

    __str__ = __repr__
