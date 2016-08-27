"""Feed you YouTube addiction, locally."""
__version__ = '0.1.0-dev'

__title__ = 'youtube_feeder'
# keep the __description__ synchronized with the module docstring
__description__ = 'Feed you YouTube addiction, locally.'
__url__ = 'https://github.com/scolby33/youtube_feeder'

__author__ = 'Scott Colby'
__email__ = 'scolby33@gmail.com'

__license__ = 'MIT License'
__copyright__ = 'Copyright (c) 2016 Scott Colby'

# perform project imports here, e.g.
# from . import a_module
# from .b_module import Class, function
from .cli import main as cli

__all__ = [cli]
