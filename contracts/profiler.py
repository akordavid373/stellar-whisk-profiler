"""
Stellar-specific profiling functionality.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging

try:
    import stellar_sdk
    from stellar_sdk.server import Server
    from stellar_sdk.keypair import Keypair
    from stellar_sdk.network import Network
    STELLAR_AVAILABLE = True
except ImportError:
    STELLAR_AVAILABLE = False

from ..whisk.core.profiler import ParallelismProfiler, ProfilingConfig


@dataclass
class StellarConfig:
    """Configuration for Stellar-specific profiling."""
    horizon_url: str = "https://horizon.stellar.org"
    network_passphrase: str = Network.PUBLIC_NETWORK_PASSPHRASE
    enable_transaction_profiling: bool = True
    enable_contract_profiling: bool = True
    enable_network_monitoring: bool = True
    max_transaction_history: int = 1000
    contract_execution_timeout: float = 30.0


class StellarProfiler:
    """Stellar-specific profiler for blockchain operations."""
    
    def __init__(self, config: Optional[StellarConfig] = None):
        self.config = config or StellarConfig()
        self.logger = logging.getLogger(__name__)
        
        if not STELLAR_AVAILABLE:
            self.logger.warning("Stellar SDK not available. Some features will be limited.")
        
        # Initialize Stellar server connection
        self.server = None
        if STELLAR_AVAILABLE:
            try:
                self.server = Server(self.config.horizon_url)
                self.logger.info(f"Connected to Stellar Horizon at {self.config.horizon_url}")
            except Exception as e:
                self.logger.error(f"Failed to connect to Stellar Horizon: {e}")
        
        # Transaction tracking
        self._transaction_count = 0
        self._transaction_times = []
        self._transaction_errors = 0
        self._lock = threading.Lock()
        
        # Contract execution tracking
        self._contract_executions = 0
        self._contract_times = []
        self._contract_errors = 0
        
        # Network metrics
        self._network_latencies = []
        self._api_call_count = 0
        self._api_error_count = 0
    
    def profile_transaction(self, transaction_func: Callable, *args, **kwargs) -> Any:
        """
        Profile a Stellar transaction function.
        
        Args:
            transaction_func: Function that executes a Stellar transaction
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the transaction function
        """
        start_time = time.time()
        
        try:
            result = transaction_func(*args, **kwargs)
            
            with self._lock:
                self._transaction_count += 1
                execution_time = time.time() - start_time
                self._transaction_times.append(execution_time)
            
            return result
            
        except Exception as e:
            with self._lock:
                self._transaction_errors += 1
            
            self.logger.error(f"Transaction failed: {e}")
            raise
    
    def profile_contract_execution(self, contract_func: Callable, *args, **kwargs) -> Any:
        """
        Profile a Stellar smart contract execution.
        
        Args:
            contract_func: Function that executes a contract
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Result of the contract function
        """
        start_time = time.time()
        
        try:
            result = contract_func(*args, **kwargs)
            
            with self._lock:
                self._contract_executions += 1
                execution_time = time.time() - start_time
                self._contract_times.append(execution_time)
            
            return result
            
        except Exception as e:
            with self._lock:
                self._contract_errors += 1
            
            self.logger.error(f"Contract execution failed: {e}")
            raise
    
    def measure_network_latency(self) -> float:
        """Measure latency to Stellar network."""
        if not self.server:
            return 0.0
        
        start_time = time.time()
        try:
            # Make a simple API call to measure latency
            self.server.fetch_base_fee()
            latency = time.time() - start_time
            
            with self._lock:
                self._network_latencies.append(latency)
                self._api_call_count += 1
            
            return latency
            
        except Exception as e:
            with self._lock:
                self._api_error_count += 1
            
            self.logger.error(f"Network latency measurement failed: {e}")
            return 0.0
    
    def get_stellar_metrics(self) -> Dict[str, Any]:
        """Get collected Stellar metrics."""
        with self._lock:
            metrics = {
                "transactions": {
                    "total_count": self._transaction_count,
                    "error_count": self._transaction_errors,
                    "success_rate": (
                        (self._transaction_count - self._transaction_errors) / max(self._transaction_count, 1)
                    ),
                },
                "contracts": {
                    "total_executions": self._contract_executions,
                    "error_count": self._contract_errors,
                    "success_rate": (
                        (self._contract_executions - self._contract_errors) / max(self._contract_executions, 1)
                    ),
                },
                "network": {
                    "total_api_calls": self._api_call_count,
                    "error_count": self._api_error_count,
                    "api_success_rate": (
                        (self._api_call_count - self._api_error_count) / max(self._api_call_count, 1)
                    ),
                },
            }
            
            # Add timing statistics
            if self._transaction_times:
                metrics["transactions"]["avg_time"] = sum(self._transaction_times) / len(self._transaction_times)
                metrics["transactions"]["min_time"] = min(self._transaction_times)
                metrics["transactions"]["max_time"] = max(self._transaction_times)
            
            if self._contract_times:
                metrics["contracts"]["avg_time"] = sum(self._contract_times) / len(self._contract_times)
                metrics["contracts"]["min_time"] = min(self._contract_times)
                metrics["contracts"]["max_time"] = max(self._contract_times)
            
            if self._network_latencies:
                metrics["network"]["avg_latency"] = sum(self._network_latencies) / len(self._network_latencies)
                metrics["network"]["min_latency"] = min(self._network_latencies)
                metrics["network"]["max_latency"] = max(self._network_latencies)
            
            return metrics
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        with self._lock:
            self._transaction_count = 0
            self._transaction_times = []
            self._transaction_errors = 0
            self._contract_executions = 0
            self._contract_times = []
            self._contract_errors = 0
            self._network_latencies = []
            self._api_call_count = 0
            self._api_error_count = 0
    
    def get_account_info(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get account information from Stellar network."""
        if not self.server:
            return None
        
        try:
            start_time = time.time()
            account = self.server.load_account(account_id)
            latency = time.time() - start_time
            
            with self._lock:
                self._network_latencies.append(latency)
                self._api_call_count += 1
            
            return {
                "account_id": account.account_id,
                "sequence": account.sequence,
                "balances": account.balances,
                "signers": account.signers,
                "data": account.data,
                "latency": latency,
            }
            
        except Exception as e:
            with self._lock:
                self._api_error_count += 1
            
            self.logger.error(f"Failed to get account info: {e}")
            return None
    
    def get_transaction_info(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction information from Stellar network."""
        if not self.server:
            return None
        
        try:
            start_time = time.time()
            transaction = self.server.transactions().transaction(transaction_hash).call()
            latency = time.time() - start_time
            
            with self._lock:
                self._network_latencies.append(latency)
                self._api_call_count += 1
            
            return {
                "hash": transaction.get('hash'),
                "successful": transaction.get('successful'),
                "ledger": transaction.get('ledger'),
                "created_at": transaction.get('created_at'),
                "operation_count": len(transaction.get('operations', [])),
                "latency": latency,
            }
            
        except Exception as e:
            with self._lock:
                self._api_error_count += 1
            
            self.logger.error(f"Failed to get transaction info: {e}")
            return None
    
    def monitor_ledger(self, duration: float = 60.0) -> Dict[str, Any]:
        """Monitor Stellar ledger activity for a specified duration."""
        if not self.server:
            return {"error": "Stellar server not available"}
        
        start_time = time.time()
        ledger_count = 0
        transaction_count = 0
        operation_count = 0
        
        try:
            # Get current ledger
            latest_ledger = self.server.ledgers().order(desc=True).limit(1).call()
            if not latest_ledger.get('_embedded', {}).get('records'):
                return {"error": "No ledger data available"}
            
            current_ledger = latest_ledger['_embedded']['records'][0]
            start_sequence = current_ledger['sequence']
            
            self.logger.info(f"Starting ledger monitoring from sequence {start_sequence}")
            
            while time.time() - start_time < duration:
                try:
                    # Get latest ledgers
                    ledgers = self.server.ledgers().order(desc=True).limit(5).call()
                    
                    for ledger in ledgers.get('_embedded', {}).get('records', []):
                        ledger_seq = ledger['sequence']
                        
                        if ledger_seq > start_sequence + ledger_count:
                            # Process new ledger
                            ledger_count += 1
                            transaction_count += ledger.get('transaction_count', 0)
                            operation_count += ledger.get('operation_count', 0)
                    
                    time.sleep(5)  # Poll every 5 seconds
                    
                except Exception as e:
                    self.logger.error(f"Error during ledger monitoring: {e}")
                    time.sleep(10)  # Wait longer on error
            
            end_time = time.time()
            actual_duration = end_time - start_time
            
            return {
                "duration": actual_duration,
                "ledgers_processed": ledger_count,
                "transactions_processed": transaction_count,
                "operations_processed": operation_count,
                "ledger_rate": ledger_count / actual_duration,
                "transaction_rate": transaction_count / actual_duration,
                "operation_rate": operation_count / actual_duration,
            }
            
        except Exception as e:
            self.logger.error(f"Ledger monitoring failed: {e}")
            return {"error": str(e)}


def stellar_transaction_profiler(profiler: StellarProfiler):
    """
    Decorator for profiling Stellar transactions.
    
    Usage:
        @stellar_transaction_profiler(stellar_profiler)
        def my_transaction_function():
            # Your Stellar transaction code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            return profiler.profile_transaction(func, *args, **kwargs)
        return wrapper
    return decorator


def stellar_contract_profiler(profiler: StellarProfiler):
    """
    Decorator for profiling Stellar contract executions.
    
    Usage:
        @stellar_contract_profiler(stellar_profiler)
        def my_contract_function():
            # Your Stellar contract code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            return profiler.profile_contract_execution(func, *args, **kwargs)
        return wrapper
    return decorator
