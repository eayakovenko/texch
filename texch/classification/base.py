import time


from texch.utils import not_proxied


class BaseClassifier(object):

    def __init__(self, classifier_class, *args, **kwargs):
        self._start_time, self._end_time = None, None
        self.labels = None
        self.classifier_class = classifier_class
        self.classifier = None
        self.args = None
        self.kwargs = None
        self._is_proxy = kwargs.pop('proxy', False)
        self.verbose_name = kwargs.pop('verbose_name', None)
        self.fit_args = ()
        self.fit_kwargs = {}
        self._is_run = False
        if not self._is_proxy:
            self._init_classifier(*args, **kwargs)

    @property
    def is_proxy(self):
        return self._is_proxy

    def _init_classifier(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.classifier = self.classifier_class(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if not self._is_proxy:
            raise TypeError(
                self.__class__.__name__ + ' object is not callable'
            )

        return self.__class__(
            self.classifier_class,
            proxy=False,
            *args,
            **kwargs
        )

    def __getattr__(self, item):
        if self._is_proxy or self.classifier is None:
            raise AttributeError
        else:
            return getattr(self.classifier, item)

    @property
    def is_run(self):
        not_proxied(self)
        return self._is_run

    def set_fit_params(self, *args, **kwargs):
        not_proxied(self)
        self.fit_args = args
        self.fit_kwargs = kwargs

    def run(self, train_X, train_y, test_X, test_y):
        not_proxied(self)
        self._start_time = time.time()
        self.fit(train_X, train_y, *self.fit_args, **self.fit_kwargs)
        self.predict(test_X, test_y)
        self._end_time = time.time()

    @property
    def spent(self):
        not_proxied(self)
        if not self._end_time or not self._start_time:
            return None
        return self._end_time - self._start_time

    def fit(self, X, y, *fit_args, **fit_kwargs):
        raise NotImplementedError

    def predict(self, X, y, *predict_args, **predict_kwargs):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__ + ': ' + (self.verbose_name or '')

    __str__ = __repr__
