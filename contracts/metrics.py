"""
Stellar-specific metrics collection and analysis.
"""

import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import numpy as np


@dataclass
class StellarTransactionMetrics:
    """Metrics for Stellar transactions."""
    timestamp: float
    transaction_hash: str
    execution_time: float
    success: bool
    operation_count: int
    fee_paid: int
    ledger_sequence: int


@dataclass
class StellarContractMetrics:
    """Metrics for Stellar smart contract executions."""
    timestamp: float
    contract_id: str
    function_name: str
    execution_time: float
    success: bool
    gas_used: int
    memory_usage: int


@dataclass
class StellarNetworkMetrics:
    """Metrics for Stellar network operations."""
    timestamp: float
    api_endpoint: str
    latency: float
    success: bool
    response_size: int
    error_type: Optional[str] = None


class StellarMetricsCollector:
    """Collects and analyzes Stellar-specific metrics."""
    
    def __init__(self):
        self.transaction_metrics: List[StellarTransactionMetrics] = []
        self.contract_metrics: List[StellarContractMetrics] = []
        self.network_metrics: List[StellarNetworkMetrics] = []
        
        self._lock = threading.Lock()
        
        # Performance counters
        self._total_transactions = 0
        self._successful_transactions = 0
        self._total_contract_calls = 0
        self._successful_contract_calls = 0
        self._total_api_calls = 0
        self._successful_api_calls = 0
    
    def add_transaction_metric(self, metric: StellarTransactionMetrics):
        """Add a transaction metric."""
        with self._lock:
            self.transaction_metrics.append(metric)
            self._total_transactions += 1
            if metric.success:
                self._successful_transactions += 1
    
    def add_contract_metric(self, metric: StellarContractMetrics):
        """Add a contract execution metric."""
        with self._lock:
            self.contract_metrics.append(metric)
            self._total_contract_calls += 1
            if metric.success:
                self._successful_contract_calls += 1
    
    def add_network_metric(self, metric: StellarNetworkMetrics):
        """Add a network operation metric."""
        with self._lock:
            self.network_metrics.append(metric)
            self._total_api_calls += 1
            if metric.success:
                self._successful_api_calls += 1
    
    def get_transaction_analysis(self) -> Dict[str, Any]:
        """Analyze transaction metrics."""
        if not self.transaction_metrics:
            return {"error": "No transaction data available"}
        
        execution_times = [m.execution_time for m in self.transaction_metrics]
        operation_counts = [m.operation_count for m in self.transaction_metrics]
        fees = [m.fee_paid for m in self.transaction_metrics]
        
        successful_tx = [m for m in self.transaction_metrics if m.success]
        failed_tx = [m for m in self.transaction_metrics if not m.success]
        
        return {
            "total_transactions": len(self.transaction_metrics),
            "successful_transactions": len(successful_tx),
            "failed_transactions": len(failed_tx),
            "success_rate": len(successful_tx) / len(self.transaction_metrics),
            "execution_time": {
                "average": np.mean(execution_times),
                "minimum": np.min(execution_times),
                "maximum": np.max(execution_times),
                "std_dev": np.std(execution_times),
                "percentile_95": np.percentile(execution_times, 95),
            },
            "operations": {
                "average_per_tx": np.mean(operation_counts),
                "total_operations": sum(operation_counts),
                "max_operations": np.max(operation_counts),
            },
            "fees": {
                "average_fee": np.mean(fees),
                "total_fees": sum(fees),
                "min_fee": np.min(fees),
                "max_fee": np.max(fees),
            },
            "throughput": self._calculate_transaction_throughput(),
        }
    
    def get_contract_analysis(self) -> Dict[str, Any]:
        """Analyze contract execution metrics."""
        if not self.contract_metrics:
            return {"error": "No contract data available"}
        
        execution_times = [m.execution_time for m in self.contract_metrics]
        gas_usage = [m.gas_used for m in self.contract_metrics]
        memory_usage = [m.memory_usage for m in self.contract_metrics]
        
        successful_calls = [m for m in self.contract_metrics if m.success]
        failed_calls = [m for m in self.contract_metrics if not m.success]
        
        # Group by contract
        contract_stats = {}
        for metric in self.contract_metrics:
            if metric.contract_id not in contract_stats:
                contract_stats[metric.contract_id] = {
                    "calls": 0,
                    "successful": 0,
                    "total_time": 0,
                    "total_gas": 0,
                    "functions": set(),
                }
            
            stats = contract_stats[metric.contract_id]
            stats["calls"] += 1
            stats["total_time"] += metric.execution_time
            stats["total_gas"] += metric.gas_used
            stats["functions"].add(metric.function_name)
            
            if metric.success:
                stats["successful"] += 1
        
        # Calculate per-contract averages
        for contract_id, stats in contract_stats.items():
            stats["success_rate"] = stats["successful"] / stats["calls"]
            stats["avg_execution_time"] = stats["total_time"] / stats["calls"]
            stats["avg_gas_usage"] = stats["total_gas"] / stats["calls"]
            stats["unique_functions"] = len(stats["functions"])
        
        return {
            "total_contract_calls": len(self.contract_metrics),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "success_rate": len(successful_calls) / len(self.contract_metrics),
            "execution_time": {
                "average": np.mean(execution_times),
                "minimum": np.min(execution_times),
                "maximum": np.max(execution_times),
                "std_dev": np.std(execution_times),
            },
            "gas_usage": {
                "average": np.mean(gas_usage),
                "total": sum(gas_usage),
                "minimum": np.min(gas_usage),
                "maximum": np.max(gas_usage),
            },
            "memory_usage": {
                "average": np.mean(memory_usage),
                "total": sum(memory_usage),
                "minimum": np.min(memory_usage),
                "maximum": np.max(memory_usage),
            },
            "contract_breakdown": contract_stats,
            "throughput": self._calculate_contract_throughput(),
        }
    
    def get_network_analysis(self) -> Dict[str, Any]:
        """Analyze network operation metrics."""
        if not self.network_metrics:
            return {"error": "No network data available"}
        
        latencies = [m.latency for m in self.network_metrics if m.success]
        response_sizes = [m.response_size for m in self.network_metrics if m.success]
        
        successful_calls = [m for m in self.network_metrics if m.success]
        failed_calls = [m for m in self.network_metrics if not m.success]
        
        # Group by endpoint
        endpoint_stats = {}
        for metric in self.network_metrics:
            if metric.api_endpoint not in endpoint_stats:
                endpoint_stats[metric.api_endpoint] = {
                    "calls": 0,
                    "successful": 0,
                    "total_latency": 0,
                    "total_size": 0,
                }
            
            stats = endpoint_stats[metric.api_endpoint]
            stats["calls"] += 1
            stats["total_latency"] += metric.latency
            stats["total_size"] += metric.response_size
            
            if metric.success:
                stats["successful"] += 1
        
        # Calculate per-endpoint averages
        for endpoint, stats in endpoint_stats.items():
            stats["success_rate"] = stats["successful"] / stats["calls"]
            stats["avg_latency"] = stats["total_latency"] / stats["calls"]
            stats["avg_response_size"] = stats["total_size"] / stats["calls"]
        
        return {
            "total_api_calls": len(self.network_metrics),
            "successful_calls": len(successful_calls),
            "failed_calls": len(failed_calls),
            "success_rate": len(successful_calls) / len(self.network_metrics),
            "latency": {
                "average": np.mean(latencies) if latencies else 0,
                "minimum": np.min(latencies) if latencies else 0,
                "maximum": np.max(latencies) if latencies else 0,
                "std_dev": np.std(latencies) if latencies else 0,
                "percentile_95": np.percentile(latencies, 95) if latencies else 0,
            },
            "response_size": {
                "average": np.mean(response_sizes) if response_sizes else 0,
                "total": sum(response_sizes),
                "minimum": np.min(response_sizes) if response_sizes else 0,
                "maximum": np.max(response_sizes) if response_sizes else 0,
            },
            "endpoint_breakdown": endpoint_stats,
            "error_types": self._analyze_error_types(),
        }
    
    def _calculate_transaction_throughput(self) -> Dict[str, float]:
        """Calculate transaction throughput metrics."""
        if not self.transaction_metrics:
            return {"transactions_per_second": 0, "operations_per_second": 0}
        
        timestamps = [m.timestamp for m in self.transaction_metrics]
        time_span = max(timestamps) - min(timestamps)
        
        if time_span == 0:
            return {"transactions_per_second": 0, "operations_per_second": 0}
        
        tx_rate = len(self.transaction_metrics) / time_span
        total_ops = sum(m.operation_count for m in self.transaction_metrics)
        op_rate = total_ops / time_span
        
        return {
            "transactions_per_second": tx_rate,
            "operations_per_second": op_rate,
            "time_span_seconds": time_span,
        }
    
    def _calculate_contract_throughput(self) -> Dict[str, float]:
        """Calculate contract execution throughput metrics."""
        if not self.contract_metrics:
            return {"calls_per_second": 0}
        
        timestamps = [m.timestamp for m in self.contract_metrics]
        time_span = max(timestamps) - min(timestamps)
        
        if time_span == 0:
            return {"calls_per_second": 0}
        
        call_rate = len(self.contract_metrics) / time_span
        return {
            "calls_per_second": call_rate,
            "time_span_seconds": time_span,
        }
    
    def _analyze_error_types(self) -> Dict[str, int]:
        """Analyze error types in failed operations."""
        error_counts = {}
        
        for metric in self.network_metrics:
            if not metric.success and metric.error_type:
                error_counts[metric.error_type] = error_counts.get(metric.error_type, 0) + 1
        
        return error_counts
    
    def get_overall_stellar_metrics(self) -> Dict[str, Any]:
        """Get comprehensive Stellar metrics analysis."""
        return {
            "transactions": self.get_transaction_analysis(),
            "contracts": self.get_contract_analysis(),
            "network": self.get_network_analysis(),
            "summary": {
                "total_operations": self._total_transactions + self._total_contract_calls + self._total_api_calls,
                "overall_success_rate": (
                    (self._successful_transactions + self._successful_contract_calls + self._successful_api_calls) /
                    max(self._total_transactions + self._total_contract_calls + self._total_api_calls, 1)
                ),
                "collection_duration": self._get_collection_duration(),
            },
        }
    
    def _get_collection_duration(self) -> float:
        """Get the duration of metrics collection."""
        all_timestamps = []
        
        if self.transaction_metrics:
            all_timestamps.extend(m.timestamp for m in self.transaction_metrics)
        
        if self.contract_metrics:
            all_timestamps.extend(m.timestamp for m in self.contract_metrics)
        
        if self.network_metrics:
            all_timestamps.extend(m.timestamp for m in self.network_metrics)
        
        if not all_timestamps:
            return 0.0
        
        return max(all_timestamps) - min(all_timestamps)
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        with self._lock:
            self.transaction_metrics.clear()
            self.contract_metrics.clear()
            self.network_metrics.clear()
            
            self._total_transactions = 0
            self._successful_transactions = 0
            self._total_contract_calls = 0
            self._successful_contract_calls = 0
            self._total_api_calls = 0
            self._successful_api_calls = 0
    
    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        data = self.get_overall_stellar_metrics()
        
        if format == "json":
            import json
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
