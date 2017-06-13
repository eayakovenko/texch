from sklearn.cluster import (
    KMeans as _SklearnKMeans,
    AgglomerativeClustering as _SklearnAgglomerativeClustering,
    MiniBatchKMeans as _SklearnMiniBatchKMeans,
    AffinityPropagation as _SklearnAffinityPropagation,
    DBSCAN as _SklearnDBSCAN,
    FeatureAgglomeration as _SklearnFeatureAgglomeration,
    MeanShift as _SklearnMeanShift,
    SpectralClustering as _SklearnSpectralClustering,
)
from .base import SklearnClusterer


KMeans = SklearnClusterer(
    _SklearnKMeans,
    proxy=True,
    verbose_name='KMeans'
)
AgglomerativeClustering = SklearnClusterer(
    _SklearnAgglomerativeClustering,
    proxy=True,
    verbose_name='AgglomerativeClustering'
)
MiniBatchKMeans = SklearnClusterer(
    _SklearnMiniBatchKMeans,
    proxy=True,
    verbose_name='MiniBatchKMeans'
)
AffinityPropagation = SklearnClusterer(
    _SklearnAffinityPropagation,
    proxy=True,
    verbose_name='AffinityPropagation'
)
DBSCAN = SklearnClusterer(
    _SklearnDBSCAN,
    proxy=True,
    verbose_name='DBSCAN'
)
FeatureAgglomeration = SklearnClusterer(
    _SklearnFeatureAgglomeration,
    proxy=True,
    verbose_name='FeatureAgglomeration'
)
MeanShift = SklearnClusterer(
    _SklearnMeanShift,
    proxy=True,
    verbose_name='MeanShift'
)
SpectralClustering = SklearnClusterer(
    _SklearnSpectralClustering,
    proxy=True,
    verbose_name='SpectralClustering'
)
