#!/usr/bin/env python3
"""Legacy entry point — delegates to the flight_tracker package CLI."""

import sys

from flight_tracker.cli import main

if __name__ == "__main__":
    sys.exit(main())
