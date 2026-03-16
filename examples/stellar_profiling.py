#!/usr/bin/env python3
"""
Stellar-specific profiling examples for the Stellar Whisk Parallelism Profiler.
"""

import time
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random

# Try to import Stellar SDK
try:
    import stellar_sdk
    from stellar_sdk.server import Server
    from stellar_sdk.keypair import Keypair
    from stellar_sdk.network import Network
    from stellar_sdk.transaction_builder import TransactionBuilder
    from stellar_sdk.exceptions import StellarSdkError
    STELLAR_AVAILABLE = True
except ImportError:
    STELLAR_AVAILABLE = False
    print("Stellar SDK not available. Some examples will be simulated.")

from stellar.whisk.core.profiler import ParallelismProfiler, ProfilingConfig
from stellar.stellar.profiler import StellarProfiler, stellar_transaction_profiler, stellar_contract_profiler


def simulate_stellar_transaction():
    """Simulate a Stellar transaction for demonstration."""
    # Simulate transaction processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    # Simulate transaction success/failure
    success = random.random() > 0.1  # 90% success rate
    
    if not success:
        raise Exception("Transaction failed")
    
    return {
        "hash": f"tx_{int(time.time())}_{random.randint(1000, 9999)}",
        "operations": random.randint(1, 5),
        "fee": random.randint(100, 500),
    }


def simulate_stellar_contract_execution():
    """Simulate a Stellar smart contract execution."""
    # Simulate contract execution time
    time.sleep(random.uniform(0.05, 0.3))
    
    # Simulate gas usage
    gas_used = random.randint(1000, 10000)
    
    # Simulate success/failure
    success = random.random() > 0.05  # 95% success rate
    
    if not success:
        raise Exception("Contract execution failed")
    
    return {
        "contract_id": f"contract_{random.randint(1, 10)}",
        "function": "execute",
        "gas_used": gas_used,
    }


def basic_stellar_profiling():
    """Basic Stellar profiling example."""
    print("Basic Stellar Profiling Example")
    print("=" * 40)
    
    config = ProfilingConfig(
        sampling_interval=0.05,
        stellar_profiling=True,
        transaction_tracking=True,
        contract_profiling=True,
        network_monitoring=True,
        track_memory=True,
        track_threads=True,
    )
    
    profiler = ParallelismProfiler(config)
    stellar_profiler = StellarProfiler()
    
    def stellar_workload():
        """Simulate a Stellar workload."""
        print("Starting Stellar workload simulation...")
        
        # Simulate multiple transactions
        for i in range(10):
            try:
                result = stellar_profiler.profile_transaction(simulate_stellar_transaction)
                print(f"Transaction {i+1} completed: {result['hash']}")
            except Exception as e:
                print(f"Transaction {i+1} failed: {e}")
            
            time.sleep(0.1)  # Small delay between transactions
        
        # Simulate contract executions
        for i in range(5):
            try:
                result = stellar_profiler.profile_contract_execution(simulate_stellar_contract_execution)
                print(f"Contract execution {i+1} completed: {result['contract_id']}")
            except Exception as e:
                print(f"Contract execution {i+1} failed: {e}")
            
            time.sleep(0.2)  # Delay between contract calls
        
        print("Stellar workload completed")
    
    # Profile the workload
    results = profiler.start(stellar_workload)
    
    # Display results
    print(f"\nProfiling Results:")
    print(f"Duration: {results['execution']['duration']:.2f}s")
    
    if "parallelism_metrics" in results:
        metrics = results["parallelism_metrics"]
        
        if "cpu_metrics" in metrics:
            cpu = metrics["cpu_metrics"]
            print(f"Average CPU Usage: {cpu['average_usage']:.1f}%")
            print(f"CPU Efficiency: {cpu['efficiency']:.3f}")
        
        if "stellar_metrics" in metrics and "error" not in metrics["stellar_metrics"]:
            stellar = metrics["stellar_metrics"]
            print(f"Total Transactions: {stellar['total_transactions']}")
            print(f"Average Transaction Rate: {stellar['average_transaction_rate']:.2f} tx/s")
            print(f"Total Contract Executions: {stellar['total_contract_executions']}")
            print(f"Stellar Efficiency: {stellar['stellar_efficiency']:.3f}")
        
        print(f"Overall Parallelism Score: {metrics['overall_parallelism_score']:.3f}")
    
    # Save results
    profiler.save_results("basic_stellar_profiling.json")
    print("\nResults saved to basic_stellar_profiling.json")
    
    return results


def concurrent_stellar_operations():
    """Example of concurrent Stellar operations."""
    print("\nConcurrent Stellar Operations Example")
    print("=" * 40)
    
    config = ProfilingConfig(
        sampling_interval=0.02,
        stellar_profiling=True,
        transaction_tracking=True,
        track_threads=True,
        track_memory=True,
    )
    
    profiler = ParallelismProfiler(config)
    stellar_profiler = StellarProfiler()
    
    def concurrent_transaction_worker(worker_id):
        """Worker function for concurrent transactions."""
        results = []
        for i in range(5):
            try:
                result = stellar_profiler.profile_transaction(simulate_stellar_transaction)
                results.append(result)
                print(f"Worker {worker_id}: Transaction {i+1} completed")
            except Exception as e:
                print(f"Worker {worker_id}: Transaction {i+1} failed: {e}")
            
            time.sleep(random.uniform(0.05, 0.15))
        
        return results
    
    def concurrent_workload():
        """Execute concurrent Stellar operations."""
        print("Starting concurrent Stellar operations...")
        
        # Use ThreadPoolExecutor for concurrent operations
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit multiple worker tasks
            futures = [
                executor.submit(concurrent_transaction_worker, i) 
                for i in range(3)
            ]
            
            # Wait for all to complete
            all_results = []
            for future in futures:
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    print(f"Worker failed: {e}")
        
        print(f"Concurrent operations completed. Total transactions: {len(all_results)}")
    
    # Profile the concurrent workload
    results = profiler.start(concurrent_workload)
    
    # Display results
    print(f"\nConcurrent Operations Results:")
    print(f"Duration: {results['execution']['duration']:.2f}s")
    
    if "parallelism_metrics" in results:
        metrics = results["parallelism_metrics"]
        
        if "thread_metrics" in metrics:
            threads = metrics["thread_metrics"]
            print(f"Maximum Thread Count: {threads['maximum_thread_count']}")
            print(f"Thread Efficiency: {threads['thread_efficiency']:.3f}")
        
        if "stellar_metrics" in metrics and "error" not in metrics["stellar_metrics"]:
            stellar = metrics["stellar_metrics"]
            print(f"Total Transactions: {stellar['total_transactions']}")
            print(f"Average Transaction Rate: {stellar['average_transaction_rate']:.2f} tx/s")
        
        print(f"Overall Parallelism Score: {metrics['overall_parallelism_score']:.3f}")
    
    # Save results
    profiler.save_results("concurrent_stellar_operations.json")
    print("\nResults saved to concurrent_stellar_operations.json")
    
    return results


def stellar_network_monitoring():
    """Example of Stellar network monitoring."""
    print("\nStellar Network Monitoring Example")
    print("=" * 40)
    
    config = ProfilingConfig(
        sampling_interval=0.1,
        stellar_profiling=True,
        network_monitoring=True,
        track_memory=True,
    )
    
    profiler = ParallelismProfiler(config)
    stellar_profiler = StellarProfiler()
    
    def network_monitoring_workload():
        """Workload that focuses on network operations."""
        print("Starting network monitoring workload...")
        
        # Simulate network operations with different latencies
        for i in range(20):
            # Measure network latency
            latency = stellar_profiler.measure_network_latency()
            print(f"Network latency measurement {i+1}: {latency:.3f}s")
            
            # Simulate some processing
            time.sleep(random.uniform(0.05, 0.2))
            
            # Occasionally simulate a transaction
            if i % 4 == 0:
                try:
                    result = stellar_profiler.profile_transaction(simulate_stellar_transaction)
                    print(f"  Transaction during monitoring: {result['hash']}")
                except Exception as e:
                    print(f"  Transaction failed: {e}")
        
        print("Network monitoring completed")
        
        # Get Stellar metrics
        stellar_metrics = stellar_profiler.get_stellar_metrics()
        print(f"\nStellar Metrics Summary:")
        print(f"  Total API Calls: {stellar_metrics['network']['total_api_calls']}")
        print(f"  API Success Rate: {stellar_metrics['network']['api_success_rate']:.3f}")
        if stellar_metrics['network']['avg_latency'] > 0:
            print(f"  Average Network Latency: {stellar_metrics['network']['avg_latency']:.3f}s")
    
    # Profile the network monitoring workload
    results = profiler.start(network_monitoring_workload)
    
    # Display results
    print(f"\nNetwork Monitoring Results:")
    print(f"Duration: {results['execution']['duration']:.2f}s")
    
    if "parallelism_metrics" in results:
        metrics = results["parallelism_metrics"]
        
        if "stellar_metrics" in metrics and "error" not in metrics["stellar_metrics"]:
            stellar = metrics["stellar_metrics"]
            print(f"Average Network Latency: {stellar['average_network_latency']:.3f}s")
            print(f"Stellar Efficiency: {stellar['stellar_efficiency']:.3f}")
        
        print(f"Overall Parallelism Score: {metrics['overall_parallelism_score']:.3f}")
    
    # Save results
    profiler.save_results("stellar_network_monitoring.json")
    print("\nResults saved to stellar_network_monitoring.json")
    
    return results


def decorator_based_profiling():
    """Example using decorators for Stellar profiling."""
    print("\nDecorator-Based Profiling Example")
    print("=" * 40)
    
    stellar_profiler = StellarProfiler()
    
    @stellar_transaction_profiler(stellar_profiler)
    def process_payment(from_account, to_account, amount):
        """Simulate processing a payment transaction."""
        time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate transaction details
        return {
            "hash": f"payment_{int(time.time())}",
            "from": from_account,
            "to": to_account,
            "amount": amount,
            "operations": 1,
            "fee": 100,
        }
    
    @stellar_contract_profiler(stellar_profiler, contract_id="token_contract")
    def token_transfer(from_address, to_address, amount):
        """Simulate a token transfer contract call."""
        time.sleep(random.uniform(0.05, 0.2))
        
        # Simulate contract execution
        return {
            "success": True,
            "gas_used": random.randint(2000, 5000),
            "from": from_address,
            "to": to_address,
            "amount": amount,
        }
    
    def decorator_workload():
        """Workload using decorated functions."""
        print("Running decorated Stellar functions...")
        
        # Process multiple payments
        for i in range(5):
            try:
                result = process_payment(f"account_{i}", f"account_{i+1}", 100 + i * 10)
                print(f"Payment processed: {result['hash']}")
            except Exception as e:
                print(f"Payment failed: {e}")
        
        # Execute token transfers
        for i in range(3):
            try:
                result = token_transfer(f"token_{i}", f"token_{i+1}", 50 + i * 5)
                print(f"Token transfer completed: {result['success']}")
            except Exception as e:
                print(f"Token transfer failed: {e}")
        
        print("Decorated workload completed")
        
        # Display Stellar metrics
        stellar_metrics = stellar_profiler.get_stellar_metrics()
        print(f"\nDecorator Profiling Results:")
        print(f"  Total Transactions: {stellar_metrics['transactions']['total_count']}")
        print(f"  Transaction Success Rate: {stellar_metrics['transactions']['success_rate']:.3f}")
        print(f"  Total Contract Calls: {stellar_metrics['contracts']['total_executions']}")
        print(f"  Contract Success Rate: {stellar_metrics['contracts']['success_rate']:.3f}")
        
        if stellar_metrics['transactions']['avg_time'] > 0:
            print(f"  Average Transaction Time: {stellar_metrics['transactions']['avg_time']:.3f}s")
        
        if stellar_metrics['contracts']['avg_time'] > 0:
            print(f"  Average Contract Time: {stellar_metrics['contracts']['avg_time']:.3f}s")
    
    # Run the decorated workload
    decorator_workload()
    
    # Reset metrics for next example
    stellar_profiler.reset_metrics()


def real_stellar_integration():
    """Example with real Stellar network (if available)."""
    print("\nReal Stellar Integration Example")
    print("=" * 40)
    
    if not STELLAR_AVAILABLE:
        print("Stellar SDK not available. Skipping real integration example.")
        return
    
    config = ProfilingConfig(
        sampling_interval=0.1,
        stellar_profiling=True,
        network_monitoring=True,
        transaction_tracking=True,
    )
    
    profiler = ParallelismProfiler(config)
    stellar_profiler = StellarProfiler()
    
    def real_stellar_workload():
        """Workload with real Stellar network operations."""
        try:
            print("Connecting to Stellar network...")
            
            # Test network connectivity
            latency = stellar_profiler.measure_network_latency()
            print(f"Network latency: {latency:.3f}s")
            
            # Get some network information
            server = Server("https://horizon.stellar.org")
            
            # Get latest ledger
            start_time = time.time()
            latest_ledger = server.ledgers().order(desc=True).limit(1).call()
            ledger_time = time.time() - start_time
            
            if latest_ledger.get('_embedded', {}).get('records'):
                ledger = latest_ledger['_embedded']['records'][0]
                print(f"Latest ledger: {ledger['sequence']}")
                print(f"Ledger fetch time: {ledger_time:.3f}s")
                
                # Track this as a network operation
                stellar_profiler.track_network_call(
                    endpoint="latest_ledger",
                    latency=ledger_time,
                    success=True,
                    response_size=len(str(ledger))
                )
            
            # Get some recent transactions
            start_time = time.time()
            recent_txs = server.transactions().limit(5).call()
            tx_time = time.time() - start_time
            
            print(f"Fetched {len(recent_txs.get('_embedded', {}).get('records', []))} transactions")
            print(f"Transaction fetch time: {tx_time:.3f}s")
            
            # Track this network operation
            stellar_profiler.track_network_call(
                endpoint="recent_transactions",
                latency=tx_time,
                success=True,
                response_size=len(str(recent_txs))
            )
            
        except Exception as e:
            print(f"Real Stellar integration failed: {e}")
            print("This might be due to network issues or API limits.")
    
    # Profile the real Stellar workload
    results = profiler.start(real_stellar_workload)
    
    # Display results
    print(f"\nReal Stellar Integration Results:")
    print(f"Duration: {results['execution']['duration']:.2f}s")
    
    if "parallelism_metrics" in results:
        metrics = results["parallelism_metrics"]
        
        if "stellar_metrics" in metrics and "error" not in metrics["stellar_metrics"]:
            stellar = metrics["stellar_metrics"]
            print(f"Average Network Latency: {stellar['average_network_latency']:.3f}s")
            print(f"Stellar Efficiency: {stellar['stellar_efficiency']:.3f}")
        
        print(f"Overall Parallelism Score: {metrics['overall_parallelism_score']:.3f}")
    
    # Save results
    profiler.save_results("real_stellar_integration.json")
    print("\nResults saved to real_stellar_integration.json")


def main():
    """Run all Stellar profiling examples."""
    print("Stellar Whisk Parallelism Profiler - Examples")
    print("=" * 60)
    
    if not STELLAR_AVAILABLE:
        print("Note: Stellar SDK is not installed. Examples will use simulated data.")
        print("To install Stellar SDK: pip install stellar-sdk")
        print()
    
    try:
        # Run all examples
        basic_stellar_profiling()
        concurrent_stellar_operations()
        stellar_network_monitoring()
        decorator_based_profiling()
        real_stellar_integration()
        
        print("\n" + "=" * 60)
        print("All Stellar profiling examples completed!")
        print("Check the generated JSON files for detailed results.")
        print("You can upload these files to the dashboard for visualization.")
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()
