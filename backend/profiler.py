"""
Main parallelism profiling engine for Stellar applications.
"""

import time
import threading
import multiprocessing
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from collections import defaultdict
import psutil
import logging

from .metrics import ParallelismMetrics
from .collector import DataCollector
from .sampler import SamplingEngine


@dataclass
class ProfilingConfig:
    """Configuration for parallelism profiling."""
    sampling_interval: float = 0.1  # seconds
    max_duration: Optional[float] = None  # seconds
    track_memory: bool = True
    track_cpu: bool = True
    track_threads: bool = True
    track_processes: bool = True
    enable_call_stack: bool = False
    output_format: str = "json"  # json, csv, html
    
    # Stellar-specific options
    stellar_profiling: bool = True
    transaction_tracking: bool = True
    contract_profiling: bool = True
    network_monitoring: bool = True
    
    # Advanced options
    gpu_profiling: bool = False
    network_profiling: bool = False
    io_profiling: bool = False


class ParallelismProfiler:
    """Main parallelism profiling engine for Stellar applications."""
    
    def __init__(self, config: Optional[ProfilingConfig] = None):
        self.config = config or ProfilingConfig()
        self.metrics = ParallelismMetrics()
        self.collector = DataCollector(self.config)
        self.sampler = SamplingEngine(self.config)
        
        self._is_running = False
        self._start_time = None
        self._end_time = None
        self._profiling_thread = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def start(self, target_function: Callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Start profiling the target function.
        
        Args:
            target_function: Function to profile
            *args: Arguments to pass to target function
            **kwargs: Keyword arguments to pass to target function
            
        Returns:
            Dictionary containing profiling results
        """
        if self._is_running:
            raise RuntimeError("Profiler is already running")
        
        self._is_running = True
        self._start_time = time.time()
        
        # Start data collection in background thread
        self._profiling_thread = threading.Thread(
            target=self._collect_data,
            daemon=True
        )
        self._profiling_thread.start()
        
        try:
            # Execute target function
            result = target_function(*args, **kwargs)
            return result
        finally:
            self.stop()
    
    def stop(self) -> Dict[str, Any]:
        """Stop profiling and return results."""
        if not self._is_running:
            return self.get_results()
        
        self._is_running = False
        self._end_time = time.time()
        
        # Wait for profiling thread to finish
        if self._profiling_thread:
            self._profiling_thread.join(timeout=1.0)
        
        return self.get_results()
    
    def _collect_data(self):
        """Background data collection loop."""
        while self._is_running:
            timestamp = time.time()
            
            # Collect system metrics
            cpu_data = self.collector.collect_cpu_metrics(timestamp)
            memory_data = self.collector.collect_memory_metrics(timestamp)
            thread_data = self.collector.collect_thread_metrics(timestamp)
            process_data = self.collector.collect_process_metrics(timestamp)
            
            # Collect Stellar-specific metrics if enabled
            stellar_data = None
            if self.config.stellar_profiling:
                stellar_data = self.collector.collect_stellar_metrics(timestamp)
            
            # Store metrics
            self.metrics.add_cpu_data(cpu_data)
            self.metrics.add_memory_data(memory_data)
            self.metrics.add_thread_data(thread_data)
            self.metrics.add_process_data(process_data)
            
            if stellar_data:
                self.metrics.add_stellar_data(stellar_data)
            
            # Check duration limit
            if (self.config.max_duration and 
                timestamp - self._start_time > self.config.max_duration):
                self._is_running = False
                break
            
            # Sleep until next sample
            time.sleep(self.config.sampling_interval)
    
    def get_results(self) -> Dict[str, Any]:
        """Get profiling results."""
        if self._start_time is None:
            return {"error": "No profiling data available"}
        
        duration = (self._end_time or time.time()) - self._start_time
        
        # Calculate parallelism metrics
        parallelism_analysis = self.metrics.calculate_parallelism_metrics(duration)
        
        return {
            "config": {
                "sampling_interval": self.config.sampling_interval,
                "max_duration": self.config.max_duration,
                "tracking": {
                    "memory": self.config.track_memory,
                    "cpu": self.config.track_cpu,
                    "threads": self.config.track_threads,
                    "processes": self.config.track_processes,
                    "stellar": self.config.stellar_profiling,
                }
            },
            "execution": {
                "start_time": self._start_time,
                "end_time": self._end_time,
                "duration": duration,
            },
            "parallelism_metrics": parallelism_analysis,
            "raw_data": self.metrics.get_raw_data(),
        }
    
    def save_results(self, filename: str, format: Optional[str] = None):
        """Save profiling results to file."""
        results = self.get_results()
        output_format = format or self.config.output_format
        
        if output_format == "json":
            import json
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        elif output_format == "csv":
            import pandas as pd
            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(results["raw_data"])
            df.to_csv(filename, index=False)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        self.logger.info(f"Results saved to {filename}")


def profile_function(config: Optional[ProfilingConfig] = None):
    """
    Decorator for profiling functions.
    
    Usage:
        @profile_function()
        def my_function():
            # Your code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = ParallelismProfiler(config)
            return profiler.start(func, *args, **kwargs)
        return wrapper
    return decorator
