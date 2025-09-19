#!/usr/bin/env python3
"""
Discovery Runner for Bangler Phase 1
Quick script to run sizing stock discovery from project root
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bangler.core.discovery import run_discovery_cli

if __name__ == "__main__":
    run_discovery_cli()