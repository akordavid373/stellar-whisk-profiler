"""
Parallelism metrics collection and analysis for Stellar applications.
"""

import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
import pandas as pd


@dataclass
class CPUMetrics:
    """CPU-related metrics."""
    timestamp: float
    cpu_percent: float
    cpu_count: int
    load_avg: Optional[List[float]] = None
    per_cpu_percent: List[float] = field(default_factory=list)


@dataclass
class MemoryMetrics:
    """Memory-related metrics."""
    timestamp: float
    memory_percent: float
    memory_used: int
    memory_available: int
    memory_total: int


@dataclass
class ThreadMetrics:
    """Thread-related metrics."""
    timestamp: float
    thread_count: int
    active_threads: int
    thread_states: Dict[str, int] = field(default_factory=dict)


@dataclass
class ProcessMetrics:
    """Process-related metrics."""
    timestamp: float
    process_count: int
    running_processes: int
    sleeping_processes: int


@dataclass
class StellarMetrics:
    """Stellar-specific metrics."""
    timestamp: float
    transaction_count: int
    transaction_rate: float
    contract_executions: int
    network_latency: float
    stellar_operations: List[Dict[str, Any]] = field(default_factory=list)


class ParallelismMetrics:
    """Container and analyzer for parallelism metrics."""
    
    def __init__(self):
        self.cpu_data: List[CPUMetrics] = []
        self.memory_data: List[MemoryMetrics] = []
        self.thread_data: List[ThreadMetrics] = []
        self.process_data: List[ProcessMetrics] = []
        self.stellar_data: List[StellarMetrics] = []
        
        self._lock = threading.Lock()
    
    def add_cpu_data(self, data: CPUMetrics):
        """Add CPU metrics."""
        with self._lock:
            self.cpu_data.append(data)
    
    def add_memory_data(self, data: MemoryMetrics):
        """Add memory metrics."""
        with self._lock:
            self.memory_data.append(data)
    
    def add_thread_data(self, data: ThreadMetrics):
        """Add thread metrics."""
        with self._lock:
            self.thread_data.append(data)
    
    def add_process_data(self, data: ProcessMetrics):
        """Add process metrics."""
        with self._lock:
            self.process_data.append(data)
    
    def add_stellar_data(self, data: StellarMetrics):
        """Add Stellar metrics."""
        with self._lock:
            self.stellar_data.append(data)
    
    def calculate_parallelism_metrics(self, duration: float) -> Dict[str, Any]:
        """Calculate comprehensive parallelism metrics."""
        if not self.cpu_data:
            return {"error": "No CPU data available"}
        
        # Extract time series data
        timestamps = [d.timestamp for d in self.cpu_data]
        cpu_usage = [d.cpu_percent for d in self.cpu_data]
        
        # Calculate basic statistics
        avg_cpu_usage = np.mean(cpu_usage)
        max_cpu_usage = np.max(cpu_usage)
        min_cpu_usage = np.min(cpu_usage)
        std_cpu_usage = np.std(cpu_usage)
        
        # Parallelism efficiency metrics
        cpu_efficiency = self._calculate_cpu_efficiency(cpu_usage)
        parallelism_factor = self._calculate_parallelism_factor(cpu_usage)
        scalability_index = self._calculate_scalability_index(cpu_usage, duration)
        
        # Thread metrics
        thread_metrics = self._analyze_thread_metrics()
        
        # Memory metrics
        memory_metrics = self._analyze_memory_metrics()
        
        # Process metrics
        process_metrics = self._analyze_process_metrics()
        
        # Stellar metrics
        stellar_metrics = self._analyze_stellar_metrics()
        
        return {
            "cpu_metrics": {
                "average_usage": avg_cpu_usage,
                "maximum_usage": max_cpu_usage,
                "minimum_usage": min_cpu_usage,
                "standard_deviation": std_cpu_usage,
                "efficiency": cpu_efficiency,
                "parallelism_factor": parallelism_factor,
                "scalability_index": scalability_index,
                "utilization_distribution": self._calculate_utilization_distribution(cpu_usage),
            },
            "thread_metrics": thread_metrics,
            "memory_metrics": memory_metrics,
            "process_metrics": process_metrics,
            "stellar_metrics": stellar_metrics,
            "overall_parallelism_score": self._calculate_overall_score(
                cpu_efficiency, parallelism_factor, thread_metrics, stellar_metrics
            ),
        }
    
    def _calculate_cpu_efficiency(self, cpu_usage: List[float]) -> float:
        """Calculate CPU efficiency (ideal vs actual usage)."""
        if not cpu_usage:
            return 0.0
        
        # Ideal would be 100% utilization when work is available
        # Efficiency = average_usage / max_usage
        max_usage = max(cpu_usage)
        if max_usage == 0:
            return 0.0
        
        return np.mean(cpu_usage) / max_usage
    
    def _calculate_parallelism_factor(self, cpu_usage: List[float]) -> float:
        """
        Calculate parallelism factor.
        Higher values indicate better parallelization.
        """
        if not cpu_usage:
            return 0.0
        
        # Parallelism factor based on variance in CPU usage
        # Lower variance = more consistent parallelism
        variance = np.var(cpu_usage)
        mean_usage = np.mean(cpu_usage)
        
        if mean_usage == 0:
            return 0.0
        
        # Normalize by mean to get relative parallelism
        return mean_usage / (1 + variance)
    
    def _calculate_scalability_index(self, cpu_usage: List[float], duration: float) -> float:
        """Calculate scalability index based on sustained parallelism."""
        if not cpu_usage or len(cpu_usage) < 2:
            return 0.0
        
        # Look at how well parallelism is sustained over time
        sustained_high_usage = sum(1 for usage in cpu_usage if usage > 50)
        sustained_ratio = sustained_high_usage / len(cpu_usage)
        
        # Factor in duration (longer sustained parallelism is better)
        duration_factor = min(duration / 10.0, 1.0)  # Normalize to 10 seconds as reference
        
        return sustained_ratio * duration_factor
    
    def _calculate_utilization_distribution(self, cpu_usage: List[float]) -> Dict[str, float]:
        """Calculate distribution of CPU utilization levels."""
        if not cpu_usage:
            return {}
        
        ranges = {
            "idle": (0, 10),
            "low": (10, 30),
            "medium": (30, 70),
            "high": (70, 90),
            "critical": (90, 100),
        }
        
        distribution = {}
        total_samples = len(cpu_usage)
        
        for range_name, (min_val, max_val) in ranges.items():
            count = sum(1 for usage in cpu_usage if min_val <= usage < max_val)
            distribution[range_name] = count / total_samples
        
        return distribution
    
    def _analyze_thread_metrics(self) -> Dict[str, Any]:
        """Analyze thread-related metrics."""
        if not self.thread_data:
            return {"error": "No thread data available"}
        
        thread_counts = [d.thread_count for d in self.thread_data]
        active_threads = [d.active_threads for d in self.thread_data]
        
        return {
            "average_thread_count": np.mean(thread_counts),
            "maximum_thread_count": np.max(thread_counts),
            "average_active_threads": np.mean(active_threads),
            "maximum_active_threads": np.max(active_threads),
            "thread_efficiency": np.mean(active_threads) / np.mean(thread_counts) if np.mean(thread_counts) > 0 else 0,
            "thread_contention": self._calculate_thread_contention(),
        }
    
    def _calculate_thread_contention(self) -> float:
        """Estimate thread contention based on thread states."""
        if not self.thread_data:
            return 0.0
        
        # Simple contention metric based on ratio of active to total threads
        contention_scores = []
        for data in self.thread_data:
            if data.thread_count > 0:
                contention = 1 - (data.active_threads / data.thread_count)
                contention_scores.append(contention)
        
        return np.mean(contention_scores) if contention_scores else 0.0
    
    def _analyze_memory_metrics(self) -> Dict[str, Any]:
        """Analyze memory-related metrics."""
        if not self.memory_data:
            return {"error": "No memory data available"}
        
        memory_usage = [d.memory_percent for d in self.memory_data]
        memory_used = [d.memory_used for d in self.memory_data]
        
        return {
            "average_memory_usage": np.mean(memory_usage),
            "maximum_memory_usage": np.max(memory_usage),
            "memory_variance": np.var(memory_usage),
            "average_memory_used_mb": np.mean(memory_used) / (1024 * 1024),
            "peak_memory_used_mb": np.max(memory_used) / (1024 * 1024),
            "memory_efficiency": self._calculate_memory_efficiency(memory_usage),
        }
    
    def _calculate_memory_efficiency(self, memory_usage: List[float]) -> float:
        """Calculate memory efficiency."""
        if not memory_usage:
            return 0.0
        
        # Efficiency based on consistent memory usage patterns
        # Lower variance = more efficient memory usage
        variance = np.var(memory_usage)
        mean_usage = np.mean(memory_usage)
        
        if mean_usage == 0:
            return 1.0  # No memory usage is perfectly efficient
        
        return 1 / (1 + variance / mean_usage)
    
    def _analyze_process_metrics(self) -> Dict[str, Any]:
        """Analyze process-related metrics."""
        if not self.process_data:
            return {"error": "No process data available"}
        
        process_counts = [d.process_count for d in self.process_data]
        running_processes = [d.running_processes for d in self.process_data]
        
        return {
            "average_process_count": np.mean(process_counts),
            "maximum_process_count": np.max(process_counts),
            "average_running_processes": np.mean(running_processes),
            "process_parallelism": np.mean(running_processes) / np.mean(process_counts) if np.mean(process_counts) > 0 else 0,
        }
    
    def _analyze_stellar_metrics(self) -> Dict[str, Any]:
        """Analyze Stellar-specific metrics."""
        if not self.stellar_data:
            return {"error": "No Stellar data available"}
        
        transaction_counts = [d.transaction_count for d in self.stellar_data]
        transaction_rates = [d.transaction_rate for d in self.stellar_data]
        contract_executions = [d.contract_executions for d in self.stellar_data]
        network_latencies = [d.network_latency for d in self.stellar_data if d.network_latency > 0]
        
        return {
            "total_transactions": sum(transaction_counts),
            "average_transaction_rate": np.mean(transaction_rates),
            "peak_transaction_rate": np.max(transaction_rates),
            "total_contract_executions": sum(contract_executions),
            "average_network_latency": np.mean(network_latencies) if network_latencies else 0,
            "stellar_efficiency": self._calculate_stellar_efficiency(transaction_rates, network_latencies),
        }
    
    def _calculate_stellar_efficiency(self, transaction_rates: List[float], 
                                    network_latencies: List[float]) -> float:
        """Calculate Stellar-specific efficiency metrics."""
        if not transaction_rates:
            return 0.0
        
        # Efficiency based on transaction throughput vs latency
        avg_rate = np.mean(transaction_rates)
        avg_latency = np.mean(network_latencies) if network_latencies else 1.0
        
        # Higher throughput and lower latency = better efficiency
        throughput_score = min(avg_rate / 100.0, 1.0)  # Normalize to 100 tx/s as reference
        latency_score = max(0, 1.0 - avg_latency / 5.0)  # 5 seconds as poor latency reference
        
        return (throughput_score + latency_score) / 2.0
    
    def _calculate_overall_score(self, cpu_efficiency: float, 
                               parallelism_factor: float, 
                               thread_metrics: Dict[str, Any],
                               stellar_metrics: Dict[str, Any]) -> float:
        """Calculate overall parallelism score including Stellar metrics."""
        thread_efficiency = thread_metrics.get("thread_efficiency", 0)
        stellar_efficiency = stellar_metrics.get("stellar_efficiency", 0) if "error" not in stellar_metrics else 0
        
        # Weighted average of different efficiency metrics
        weights = {
            "cpu": 0.3,
            "parallelism": 0.2,
            "threads": 0.2,
            "stellar": 0.3,
        }
        
        overall_score = (
            weights["cpu"] * cpu_efficiency +
            weights["parallelism"] * parallelism_factor +
            weights["threads"] * thread_efficiency +
            weights["stellar"] * stellar_efficiency
        )
        
        return min(overall_score, 1.0)  # Cap at 1.0
    
    def get_raw_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get raw metrics data as dictionaries."""
        return {
            "cpu": [
                {
                    "timestamp": d.timestamp,
                    "cpu_percent": d.cpu_percent,
                    "cpu_count": d.cpu_count,
                    "load_avg": d.load_avg,
                    "per_cpu_percent": d.per_cpu_percent,
                }
                for d in self.cpu_data
            ],
            "memory": [
                {
                    "timestamp": d.timestamp,
                    "memory_percent": d.memory_percent,
                    "memory_used": d.memory_used,
                    "memory_available": d.memory_available,
                    "memory_total": d.memory_total,
                }
                for d in self.memory_data
            ],
            "threads": [
                {
                    "timestamp": d.timestamp,
                    "thread_count": d.thread_count,
                    "active_threads": d.active_threads,
                    "thread_states": d.thread_states,
                }
                for d in self.thread_data
            ],
            "processes": [
                {
                    "timestamp": d.timestamp,
                    "process_count": d.process_count,
                    "running_processes": d.running_processes,
                    "sleeping_processes": d.sleeping_processes,
                }
                for d in self.process_data
            ],
            "stellar": [
                {
                    "timestamp": d.timestamp,
                    "transaction_count": d.transaction_count,
                    "transaction_rate": d.transaction_rate,
                    "contract_executions": d.contract_executions,
                    "network_latency": d.network_latency,
                    "stellar_operations": d.stellar_operations,
                }
                for d in self.stellar_data
            ],
        }
