from ..base import PreprocessClass
from sklearn.feature_extraction.text import (
    TfidfVectorizer as _SklearnTfidfVectorizer
)


TfidfVectorizer = PreprocessClass(
    process_class=_SklearnTfidfVectorizer,
    preprocess_method_name='fit_transform',
    proxy=True
)
