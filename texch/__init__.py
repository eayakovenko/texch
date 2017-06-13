import logging
import sys
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.basicConfig(
    format='%(message)s',
    level=logging.DEBUG,
    stream=sys.stdout
)

logging.getLogger(__name__).addHandler(NullHandler())
