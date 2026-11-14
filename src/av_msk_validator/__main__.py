r"""
Точка входа для запуска пакета как модуля:
    python -m av_msk_validator --feed feed.xml --images public_images
"""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())