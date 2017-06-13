from nltk.cluster import (
    KMeansClusterer as _NLTKKMeansClusterer,
    EMClusterer as _NLTKKEMClusterer,
    GAAClusterer as _NLTKGAAClusterer
)
from .base import NLTKClusterer

KMeansClusterer = NLTKClusterer(
    _NLTKKMeansClusterer,
    proxy=True,
    verbose_name='KMeans'
)
EMClusterer = NLTKClusterer(
    _NLTKKEMClusterer,
    proxy=True,
    verbose_name='EM Clustering'
)
GAAClusterer = NLTKClusterer(
    _NLTKGAAClusterer,
    proxy=True,
    verbose_name='GAAC Clustering'
)
