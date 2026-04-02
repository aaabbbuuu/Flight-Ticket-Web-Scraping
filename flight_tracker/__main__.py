"""Allow running as `python -m flight_tracker`."""

import sys

from .cli import main

sys.exit(main())
