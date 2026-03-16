"""
Stellar-specific data collection module.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
import logging

try:
    import stellar_sdk
    from stellar_sdk.server import Server
    from stellar_sdk.exceptions import StellarSdkError
    STELLAR_AVAILABLE = True
except ImportError:
    STELLAR_AVAILABLE = False

from .metrics import (
    StellarTransactionMetrics,
    StellarContractMetrics,
    StellarNetworkMetrics,
    StellarMetricsCollector,
)


class StellarCollector:
    """Collects Stellar-specific metrics for profiling."""
    
    def __init__(self, horizon_url: str = "https://horizon.stellar.org"):
        self.horizon_url = horizon_url
        self.logger = logging.getLogger(__name__)
        
        # Initialize Stellar server
        self.server = None
        if STELLAR_AVAILABLE:
            try:
                self.server = Server(horizon_url)
                self.logger.info(f"Stellar collector initialized with {horizon_url}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Stellar server: {e}")
        
        # Metrics collector
        self.metrics_collector = StellarMetricsCollector()
        
        # Collection state
        self._is_collecting = False
        self._collection_thread = None
        self._stop_event = threading.Event()
        
        # Callbacks for manual instrumentation
        self._transaction_callbacks = []
        self._contract_callbacks = []
        self._network_callbacks = []
    
    def start_collection(self, interval: float = 1.0):
        """Start automatic metrics collection."""
        if self._is_collecting:
            raise RuntimeError("Collection already started")
        
        self._is_collecting = True
        self._stop_event.clear()
        
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(interval,),
            daemon=True
        )
        self._collection_thread.start()
        
        self.logger.info("Stellar metrics collection started")
    
    def stop_collection(self):
        """Stop automatic metrics collection."""
        if not self._is_collecting:
            return
        
        self._is_collecting = False
        self._stop_event.set()
        
        if self._collection_thread:
            self._collection_thread.join(timeout=5.0)
        
        self.logger.info("Stellar metrics collection stopped")
    
    def _collection_loop(self, interval: float):
        """Main collection loop."""
        while not self._stop_event.is_set():
            try:
                # Collect network metrics
                self._collect_network_metrics()
                
                # Wait for next collection
                self._stop_event.wait(interval)
                
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")
                self._stop_event.wait(5.0)  # Wait longer on error
    
    def _collect_network_metrics(self):
        """Collect network performance metrics."""
        if not self.server:
            return
        
        try:
            # Measure latency to different endpoints
            endpoints = [
                ("base_fee", lambda: self.server.fetch_base_fee()),
                ("latest_ledger", lambda: self.server.ledgers().order(desc=True).limit(1).call()),
                ("transactions", lambda: self.server.transactions().limit(1).call()),
            ]
            
            for endpoint_name, endpoint_func in endpoints:
                start_time = time.time()
                success = True
                error_type = None
                response_size = 0
                
                try:
                    result = endpoint_func()
                    response_size = len(str(result))
                    
                except StellarSdkError as e:
                    success = False
                    error_type = "stellar_sdk_error"
                    
                except Exception as e:
                    success = False
                    error_type = "unknown_error"
                
                latency = time.time() - start_time
                
                metric = StellarNetworkMetrics(
                    timestamp=time.time(),
                    api_endpoint=endpoint_name,
                    latency=latency,
                    success=success,
                    response_size=response_size,
                    error_type=error_type,
                )
                
                self.metrics_collector.add_network_metric(metric)
                
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
    
    def track_transaction(self, transaction_hash: str, execution_time: float, 
                         success: bool, operation_count: int, fee_paid: int,
                         ledger_sequence: Optional[int] = None):
        """Manually track a transaction."""
        metric = StellarTransactionMetrics(
            timestamp=time.time(),
            transaction_hash=transaction_hash,
            execution_time=execution_time,
            success=success,
            operation_count=operation_count,
            fee_paid=fee_paid,
            ledger_sequence=ledger_sequence or 0,
        )
        
        self.metrics_collector.add_transaction_metric(metric)
        
        # Trigger callbacks
        for callback in self._transaction_callbacks:
            try:
                callback(metric)
            except Exception as e:
                self.logger.error(f"Error in transaction callback: {e}")
    
    def track_contract_execution(self, contract_id: str, function_name: str,
                               execution_time: float, success: bool, gas_used: int,
                               memory_usage: int = 0):
        """Manually track a contract execution."""
        metric = StellarContractMetrics(
            timestamp=time.time(),
            contract_id=contract_id,
            function_name=function_name,
            execution_time=execution_time,
            success=success,
            gas_used=gas_used,
            memory_usage=memory_usage,
        )
        
        self.metrics_collector.add_contract_metric(metric)
        
        # Trigger callbacks
        for callback in self._contract_callbacks:
            try:
                callback(metric)
            except Exception as e:
                self.logger.error(f"Error in contract callback: {e}")
    
    def track_network_call(self, endpoint: str, latency: float, success: bool,
                          response_size: int = 0, error_type: Optional[str] = None):
        """Manually track a network call."""
        metric = StellarNetworkMetrics(
            timestamp=time.time(),
            api_endpoint=endpoint,
            latency=latency,
            success=success,
            response_size=response_size,
            error_type=error_type,
        )
        
        self.metrics_collector.add_network_metric(metric)
        
        # Trigger callbacks
        for callback in self._network_callbacks:
            try:
                callback(metric)
            except Exception as e:
                self.logger.error(f"Error in network callback: {e}")
    
    def add_transaction_callback(self, callback: Callable[[StellarTransactionMetrics], None]):
        """Add a callback for transaction metrics."""
        self._transaction_callbacks.append(callback)
    
    def add_contract_callback(self, callback: Callable[[StellarContractMetrics], None]):
        """Add a callback for contract metrics."""
        self._contract_callbacks.append(callback)
    
    def add_network_callback(self, callback: Callable[[StellarNetworkMetrics], None]):
        """Add a callback for network metrics."""
        self._network_callbacks.append(callback)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return self.metrics_collector.get_overall_stellar_metrics()
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        self.metrics_collector.reset_metrics()
    
    def monitor_account(self, account_id: str, duration: float = 60.0) -> Dict[str, Any]:
        """Monitor a specific account for activity."""
        if not self.server:
            return {"error": "Stellar server not available"}
        
        start_time = time.time()
        transactions = []
        operations = []
        
        try:
            while time.time() - start_time < duration:
                try:
                    # Get recent transactions for account
                    tx_response = self.server.transactions().for_account(account_id).limit(10).call()
                    
                    for tx in tx_response.get('_embedded', {}).get('records', []):
                        tx_hash = tx.get('hash')
                        if tx_hash and not any(t['hash'] == tx_hash for t in transactions):
                            transactions.append({
                                'hash': tx_hash,
                                'created_at': tx.get('created_at'),
                                'successful': tx.get('successful'),
                                'operation_count': len(tx.get('operations', [])),
                            })
                            
                            # Track this transaction
                            self.track_transaction(
                                transaction_hash=tx_hash,
                                execution_time=0.0,  # Not available from horizon
                                success=tx.get('successful', False),
                                operation_count=len(tx.get('operations', [])),
                                fee_paid=int(tx.get('fee_paid', 0)),
                            )
                    
                    time.sleep(5)  # Poll every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error monitoring account: {e}")
                    time.sleep(10)
            
            return {
                "account_id": account_id,
                "monitoring_duration": time.time() - start_time,
                "transactions_found": len(transactions),
                "transactions": transactions,
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def monitor_ledger(self, duration: float = 60.0) -> Dict[str, Any]:
        """Monitor ledger activity."""
        if not self.server:
            return {"error": "Stellar server not available"}
        
        start_time = time.time()
        ledgers = []
        
        try:
            while time.time() - start_time < duration:
                try:
                    # Get recent ledgers
                    ledger_response = self.server.ledgers().order(desc=True).limit(5).call()
                    
                    for ledger in ledger_response.get('_embedded', {}).get('records', []):
                        ledger_seq = ledger.get('sequence')
                        if ledger_seq and not any(l['sequence'] == ledger_seq for l in ledgers):
                            ledgers.append({
                                'sequence': ledger_seq,
                                'created_at': ledger.get('created_at'),
                                'transaction_count': ledger.get('transaction_count', 0),
                                'operation_count': ledger.get('operation_count', 0),
                                'base_fee': ledger.get('base_fee', 0),
                            })
                    
                    time.sleep(5)  # Poll every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error monitoring ledger: {e}")
                    time.sleep(10)
            
            return {
                "monitoring_duration": time.time() - start_time,
                "ledgers_found": len(ledgers),
                "ledgers": ledgers,
            }
            
        except Exception as e:
            return {"error": str(e)}


class StellarInstrumentation:
    """Helper class for instrumenting Stellar applications."""
    
    def __init__(self, collector: StellarCollector):
        self.collector = collector
    
    def transaction_profiler(self, transaction_hash: str = None):
        """Decorator for profiling Stellar transactions."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                operation_count = 0
                fee_paid = 0
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Try to extract transaction info from result
                    if hasattr(result, 'hash'):
                        transaction_hash = result.hash
                    if hasattr(result, 'operations'):
                        operation_count = len(result.operations)
                    if hasattr(result, 'fee'):
                        fee_paid = result.fee
                    
                    return result
                    
                except Exception as e:
                    success = False
                    raise
                    
                finally:
                    execution_time = time.time() - start_time
                    tx_hash = transaction_hash or f"manual_{int(time.time())}"
                    
                    self.collector.track_transaction(
                        transaction_hash=tx_hash,
                        execution_time=execution_time,
                        success=success,
                        operation_count=operation_count,
                        fee_paid=fee_paid,
                    )
            
            return wrapper
        return decorator
    
    def contract_profiler(self, contract_id: str, function_name: str = None):
        """Decorator for profiling Stellar contract executions."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                func_name = function_name or func.__name__
                start_time = time.time()
                success = True
                gas_used = 0
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Try to extract gas usage from result
                    if hasattr(result, 'gas_used'):
                        gas_used = result.gas_used
                    
                    return result
                    
                except Exception as e:
                    success = False
                    raise
                    
                finally:
                    execution_time = time.time() - start_time
                    
                    self.collector.track_contract_execution(
                        contract_id=contract_id,
                        function_name=func_name,
                        execution_time=execution_time,
                        success=success,
                        gas_used=gas_used,
                    )
            
            return wrapper
        return decorator
