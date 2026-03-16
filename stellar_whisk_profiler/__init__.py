"""
Stellar Whisk Parallelism Profiler

A comprehensive infrastructure for profiling and analyzing parallelism in Stellar blockchain applications.
"""

__version__ = "0.1.0"
__author__ = "Stellar Whisk Team"
__email__ = "team@stellar-whisk.org"

from .backend import ParallelismProfiler, ProfilingConfig
from .frontend import create_app
from .contracts import StellarProfiler

__all__ = [
    "ParallelismProfiler",
    "ProfilingConfig", 
    "create_app",
    "StellarProfiler",
]
