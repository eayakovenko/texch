import time


from texch.utils import not_proxied


class BaseClusterer(object):

    def __init__(self, cluster_class, *args, **kwargs):
        self._start_time, self._end_time = None, None
        self.clusters = None
        self.labels = None
        self.cluster_class = cluster_class
        self.clusterer = None
        self.args = None
        self.kwargs = None
        self._is_proxy = kwargs.pop('proxy', False)
        self.verbose_name = kwargs.pop('verbose_name', None)
        self.fit_args = ()
        self.fit_kwargs = {}
        self._is_run = False
        if not self._is_proxy:
            self._init_clusterer(*args, **kwargs)

    @property
    def is_proxy(self):
        return self._is_proxy

    def _init_clusterer(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.clusterer = self.cluster_class(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if not self._is_proxy:
            raise TypeError(
                self.__class__.__name__ + ' object is not callable'
            )

        return self.__class__(
            self.cluster_class,
            proxy=False,
            *args,
            **kwargs
        )

    def __getattr__(self, item):
        if self._is_proxy or self.clusterer is None:
            raise AttributeError
        else:
            return getattr(self.clusterer, item)

    @property
    def is_run(self):
        not_proxied(self)
        return self._is_run

    def set_fit_params(self, *args, **kwargs):
        not_proxied(self)
        self.fit_args = args
        self.fit_kwargs = kwargs

    def run(self, data):
        not_proxied(self)
        self._start_time = time.time()
        self.fit(data, *self.fit_args, **self.fit_kwargs)
        self._end_time = time.time()

    @property
    def spent(self):
        not_proxied(self)
        if not self._end_time or not self._start_time:
            return None
        return self._end_time - self._start_time

    def fit(self, data, *fit_args, **fit_kwargs):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__ + ': ' + (self.verbose_name or '')

    __str__ = __repr__
