#!/usr/bin/env python3
"""
Command-line interface for the Email Assistant.
"""

import typer
from typing import Optional
from rich.console import Console

from main import app

console = Console()

if __name__ == "__main__":
    app()
