"""
Tests for Stellar-specific profiling functionality.
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
import os

from stellar.stellar.profiler import StellarProfiler, StellarConfig
from stellar.stellar.metrics import (
    StellarMetricsCollector,
    StellarTransactionMetrics,
    StellarContractMetrics,
    StellarNetworkMetrics,
)
from stellar.stellar.collector import StellarCollector


class TestStellarConfig(unittest.TestCase):
    """Test Stellar configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = StellarConfig()
        
        self.assertEqual(config.horizon_url, "https://horizon.stellar.org")
        self.assertTrue(config.enable_transaction_profiling)
        self.assertTrue(config.enable_contract_profiling)
        self.assertTrue(config.enable_network_monitoring)
        self.assertEqual(config.max_transaction_history, 1000)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = StellarConfig(
            horizon_url="https://testnet.stellar.org",
            enable_transaction_profiling=False,
            max_transaction_history=500
        )
        
        self.assertEqual(config.horizon_url, "https://testnet.stellar.org")
        self.assertFalse(config.enable_transaction_profiling)
        self.assertEqual(config.max_transaction_history, 500)


class TestStellarMetricsCollector(unittest.TestCase):
    """Test Stellar metrics collection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = StellarMetricsCollector()
    
    def test_add_transaction_metric(self):
        """Test adding transaction metrics."""
        metric = StellarTransactionMetrics(
            timestamp=time.time(),
            transaction_hash="test_hash",
            execution_time=0.5,
            success=True,
            operation_count=3,
            fee_paid=100,
            ledger_sequence=12345
        )
        
        self.collector.add_transaction_metric(metric)
        
        self.assertEqual(len(self.collector.transaction_metrics), 1)
        self.assertEqual(self.collector._total_transactions, 1)
        self.assertEqual(self.collector._successful_transactions, 1)
    
    def test_add_contract_metric(self):
        """Test adding contract metrics."""
        metric = StellarContractMetrics(
            timestamp=time.time(),
            contract_id="test_contract",
            function_name="test_function",
            execution_time=0.2,
            success=True,
            gas_used=5000,
            memory_usage=1024
        )
        
        self.collector.add_contract_metric(metric)
        
        self.assertEqual(len(self.collector.contract_metrics), 1)
        self.assertEqual(self.collector._total_contract_calls, 1)
        self.assertEqual(self.collector._successful_contract_calls, 1)
    
    def test_add_network_metric(self):
        """Test adding network metrics."""
        metric = StellarNetworkMetrics(
            timestamp=time.time(),
            api_endpoint="test_endpoint",
            latency=0.1,
            success=True,
            response_size=1024
        )
        
        self.collector.add_network_metric(metric)
        
        self.assertEqual(len(self.collector.network_metrics), 1)
        self.assertEqual(self.collector._total_api_calls, 1)
        self.assertEqual(self.collector._successful_api_calls, 1)
    
    def test_get_transaction_analysis(self):
        """Test transaction analysis."""
        # Add sample transaction metrics
        for i in range(5):
            metric = StellarTransactionMetrics(
                timestamp=time.time() + i,
                transaction_hash=f"hash_{i}",
                execution_time=0.1 + i * 0.05,
                success=i < 4,  # 4 successful, 1 failed
                operation_count=2 + i,
                fee_paid=100 + i * 10,
                ledger_sequence=12345 + i
            )
            self.collector.add_transaction_metric(metric)
        
        analysis = self.collector.get_transaction_analysis()
        
        self.assertEqual(analysis["total_transactions"], 5)
        self.assertEqual(analysis["successful_transactions"], 4)
        self.assertEqual(analysis["failed_transactions"], 1)
        self.assertAlmostEqual(analysis["success_rate"], 0.8, places=2)
        self.assertIn("execution_time", analysis)
        self.assertIn("operations", analysis)
        self.assertIn("fees", analysis)
    
    def test_get_contract_analysis(self):
        """Test contract analysis."""
        # Add sample contract metrics
        for i in range(3):
            metric = StellarContractMetrics(
                timestamp=time.time() + i,
                contract_id=f"contract_{i % 2}",  # 2 different contracts
                function_name=f"function_{i}",
                execution_time=0.1 + i * 0.02,
                success=True,
                gas_used=1000 + i * 500,
                memory_usage=512 + i * 256
            )
            self.collector.add_contract_metric(metric)
        
        analysis = self.collector.get_contract_analysis()
        
        self.assertEqual(analysis["total_contract_calls"], 3)
        self.assertEqual(analysis["successful_calls"], 3)
        self.assertEqual(analysis["failed_calls"], 0)
        self.assertAlmostEqual(analysis["success_rate"], 1.0, places=2)
        self.assertIn("execution_time", analysis)
        self.assertIn("gas_usage", analysis)
        self.assertIn("contract_breakdown", analysis)
    
    def test_get_network_analysis(self):
        """Test network analysis."""
        # Add sample network metrics
        for i in range(4):
            metric = StellarNetworkMetrics(
                timestamp=time.time() + i,
                api_endpoint=f"endpoint_{i % 2}",  # 2 different endpoints
                latency=0.05 + i * 0.02,
                success=i < 3,  # 3 successful, 1 failed
                response_size=512 + i * 256,
                error_type=None if i < 3 else "timeout"
            )
            self.collector.add_network_metric(metric)
        
        analysis = self.collector.get_network_analysis()
        
        self.assertEqual(analysis["total_api_calls"], 4)
        self.assertEqual(analysis["successful_calls"], 3)
        self.assertEqual(analysis["failed_calls"], 1)
        self.assertAlmostEqual(analysis["success_rate"], 0.75, places=2)
        self.assertIn("latency", analysis)
        self.assertIn("endpoint_breakdown", analysis)
        self.assertIn("error_types", analysis)
    
    def test_reset_metrics(self):
        """Test resetting metrics."""
        # Add some metrics
        self.collector.add_transaction_metric(StellarTransactionMetrics(
            timestamp=time.time(),
            transaction_hash="test",
            execution_time=0.1,
            success=True,
            operation_count=1,
            fee_paid=100,
            ledger_sequence=1
        ))
        
        self.assertEqual(len(self.collector.transaction_metrics), 1)
        self.assertEqual(self.collector._total_transactions, 1)
        
        # Reset
        self.collector.reset_metrics()
        
        self.assertEqual(len(self.collector.transaction_metrics), 0)
        self.assertEqual(self.collector._total_transactions, 0)
        self.assertEqual(self.collector._successful_transactions, 0)


class TestStellarProfiler(unittest.TestCase):
    """Test Stellar profiler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = StellarConfig()
        self.profiler = StellarProfiler(self.config)
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        self.assertIsNotNone(self.profiler.config)
        self.assertIsNotNone(self.profiler.logger)
        self.assertEqual(self.profiler._transaction_count, 0)
        self.assertEqual(self.profiler._contract_executions, 0)
    
    def test_profile_transaction_success(self):
        """Test profiling a successful transaction."""
        def mock_transaction():
            time.sleep(0.1)
            return {"hash": "test_hash", "operations": 3, "fee": 200}
        
        result = self.profiler.profile_transaction(mock_transaction)
        
        self.assertEqual(result["hash"], "test_hash")
        self.assertEqual(self.profiler._transaction_count, 1)
        self.assertEqual(self.profiler._transaction_errors, 0)
        self.assertEqual(len(self.profiler._transaction_times), 1)
    
    def test_profile_transaction_failure(self):
        """Test profiling a failed transaction."""
        def failing_transaction():
            time.sleep(0.05)
            raise Exception("Transaction failed")
        
        with self.assertRaises(Exception):
            self.profiler.profile_transaction(failing_transaction)
        
        self.assertEqual(self.profiler._transaction_count, 1)
        self.assertEqual(self.profiler._transaction_errors, 1)
    
    def test_profile_contract_execution_success(self):
        """Test profiling a successful contract execution."""
        def mock_contract():
            time.sleep(0.1)
            return {"gas_used": 5000, "success": True}
        
        result = self.profiler.profile_contract_execution(mock_contract)
        
        self.assertTrue(result["success"])
        self.assertEqual(self.profiler._contract_executions, 1)
        self.assertEqual(self.profiler._contract_errors, 0)
        self.assertEqual(len(self.profiler._contract_times), 1)
    
    def test_profile_contract_execution_failure(self):
        """Test profiling a failed contract execution."""
        def failing_contract():
            time.sleep(0.05)
            raise Exception("Contract execution failed")
        
        with self.assertRaises(Exception):
            self.profiler.profile_contract_execution(failing_contract)
        
        self.assertEqual(self.profiler._contract_executions, 1)
        self.assertEqual(self.profiler._contract_errors, 1)
    
    def test_get_stellar_metrics(self):
        """Test getting Stellar metrics."""
        # Add some transaction and contract data
        self.profiler._transaction_count = 10
        self.profiler._transaction_errors = 2
        self.profiler._transaction_times = [0.1, 0.2, 0.15]
        
        self.profiler._contract_executions = 5
        self.profiler._contract_errors = 1
        self.profiler._contract_times = [0.05, 0.08]
        
        self.profiler._network_latencies = [0.02, 0.03, 0.025]
        self.profiler._api_call_count = 8
        self.profiler._api_error_count = 1
        
        metrics = self.profiler.get_stellar_metrics()
        
        self.assertEqual(metrics["transactions"]["total_count"], 10)
        self.assertEqual(metrics["transactions"]["error_count"], 2)
        self.assertAlmostEqual(metrics["transactions"]["success_rate"], 0.8, places=2)
        
        self.assertEqual(metrics["contracts"]["total_executions"], 5)
        self.assertEqual(metrics["contracts"]["error_count"], 1)
        self.assertAlmostEqual(metrics["contracts"]["success_rate"], 0.8, places=2)
        
        self.assertEqual(metrics["network"]["total_api_calls"], 8)
        self.assertEqual(metrics["network"]["error_count"], 1)
        self.assertAlmostEqual(metrics["network"]["api_success_rate"], 0.875, places=2)
    
    def test_reset_metrics(self):
        """Test resetting profiler metrics."""
        # Set some metrics
        self.profiler._transaction_count = 5
        self.profiler._contract_executions = 3
        self.profiler._api_call_count = 10
        
        # Reset
        self.profiler.reset_metrics()
        
        self.assertEqual(self.profiler._transaction_count, 0)
        self.assertEqual(self.profiler._contract_executions, 0)
        self.assertEqual(self.profiler._api_call_count, 0)
        self.assertEqual(len(self.profiler._transaction_times), 0)
        self.assertEqual(len(self.profiler._contract_times), 0)
        self.assertEqual(len(self.profiler._network_latencies), 0)
    
    @patch('stellar.stellar.profiler.STELLAR_AVAILABLE', True)
    @patch('stellar.stellar.profiler.Server')
    def test_measure_network_latency(self, mock_server_class):
        """Test measuring network latency."""
        mock_server = Mock()
        mock_server_class.return_value = mock_server
        
        # Mock successful API call
        mock_server.fetch_base_fee.return_value = {"fee": 100}
        
        latency = self.profiler.measure_network_latency()
        
        self.assertGreater(latency, 0)
        self.assertEqual(self.profiler._api_call_count, 1)
        self.assertEqual(self.profiler._api_error_count, 0)
        self.assertEqual(len(self.profiler._network_latencies), 1)
    
    @patch('stellar.stellar.profiler.STELLAR_AVAILABLE', False)
    def test_measure_network_latency_no_stellar(self):
        """Test measuring network latency when Stellar is not available."""
        latency = self.profiler.measure_network_latency()
        
        self.assertEqual(latency, 0.0)
        self.assertEqual(self.profiler._api_call_count, 0)


class TestStellarCollector(unittest.TestCase):
    """Test Stellar collector functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = StellarCollector()
    
    def test_collector_initialization(self):
        """Test collector initialization."""
        self.assertIsNotNone(self.collector.metrics_collector)
        self.assertFalse(self.collector._is_collecting)
        self.assertEqual(len(self.collector._transaction_callbacks), 0)
    
    def test_track_transaction(self):
        """Test tracking a transaction."""
        self.collector.track_transaction(
            transaction_hash="test_hash",
            execution_time=0.5,
            success=True,
            operation_count=3,
            fee_paid=100,
            ledger_sequence=12345
        )
        
        self.assertEqual(len(self.collector.metrics_collector.transaction_metrics), 1)
        
        metric = self.collector.metrics_collector.transaction_metrics[0]
        self.assertEqual(metric.transaction_hash, "test_hash")
        self.assertEqual(metric.execution_time, 0.5)
        self.assertTrue(metric.success)
        self.assertEqual(metric.operation_count, 3)
    
    def test_track_contract_execution(self):
        """Test tracking a contract execution."""
        self.collector.track_contract_execution(
            contract_id="test_contract",
            function_name="test_function",
            execution_time=0.2,
            success=True,
            gas_used=5000,
            memory_usage=1024
        )
        
        self.assertEqual(len(self.collector.metrics_collector.contract_metrics), 1)
        
        metric = self.collector.metrics_collector.contract_metrics[0]
        self.assertEqual(metric.contract_id, "test_contract")
        self.assertEqual(metric.function_name, "test_function")
        self.assertEqual(metric.execution_time, 0.2)
        self.assertTrue(metric.success)
    
    def test_track_network_call(self):
        """Test tracking a network call."""
        self.collector.track_network_call(
            endpoint="test_endpoint",
            latency=0.1,
            success=True,
            response_size=1024
        )
        
        self.assertEqual(len(self.collector.metrics_collector.network_metrics), 1)
        
        metric = self.collector.metrics_collector.network_metrics[0]
        self.assertEqual(metric.api_endpoint, "test_endpoint")
        self.assertEqual(metric.latency, 0.1)
        self.assertTrue(metric.success)
        self.assertEqual(metric.response_size, 1024)
    
    def test_add_callbacks(self):
        """Test adding callbacks."""
        callback_count = 0
        
        def test_callback(metric):
            nonlocal callback_count
            callback_count += 1
        
        self.collector.add_transaction_callback(test_callback)
        self.collector.add_contract_callback(test_callback)
        self.collector.add_network_callback(test_callback)
        
        self.assertEqual(len(self.collector._transaction_callbacks), 1)
        self.assertEqual(len(self.collector._contract_callbacks), 1)
        self.assertEqual(len(self.collector._network_callbacks), 1)
        
        # Trigger callbacks
        self.collector.track_transaction(
            transaction_hash="test",
            execution_time=0.1,
            success=True,
            operation_count=1,
            fee_paid=100
        )
        
        self.assertEqual(callback_count, 1)  # Transaction callback should be called
    
    def test_get_metrics(self):
        """Test getting collected metrics."""
        # Add some metrics
        self.collector.track_transaction(
            transaction_hash="test",
            execution_time=0.1,
            success=True,
            operation_count=1,
            fee_paid=100
        )
        
        metrics = self.collector.get_metrics()
        
        self.assertIn("transactions", metrics)
        self.assertIn("contracts", metrics)
        self.assertIn("network", metrics)
        self.assertIn("summary", metrics)


if __name__ == "__main__":
    unittest.main()
