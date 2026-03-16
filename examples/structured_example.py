#!/usr/bin/env python3
"""
Structured example showing the three-tier architecture of Stellar Whisk Profiler.
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Import from the structured components
from stellar_whisk_profiler.backend import ParallelismProfiler, ProfilingConfig
from stellar_whisk_profiler.contracts import StellarProfiler
from stellar_whisk_profiler.frontend import create_app


def backend_example():
    """Example using the backend profiling engine."""
    print("=== Backend Example ===")
    
    # Configure backend profiler
    config = ProfilingConfig(
        sampling_interval=0.05,
        track_memory=True,
        track_threads=True,
        stellar_profiling=True,
        transaction_tracking=True,
    )
    
    # Create backend profiler
    profiler = ParallelismProfiler(config)
    
    def cpu_intensive_task():
        """CPU-intensive workload to profile."""
        result = 0
        for i in range(100000):
            result += i * i
        return result
    
    def thread_workload():
        """Multi-threaded workload."""
        def worker(worker_id):
            time.sleep(0.1)
            return f"Worker {worker_id} completed"
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(worker, i) for i in range(8)]
            results = [future.result() for future in futures]
        
        return results
    
    # Profile CPU-intensive task
    print("Profiling CPU-intensive task...")
    results = profiler.start(cpu_intensive_task)
    
    print(f"Task result: {results}")
    print(f"Profiling duration: {profiler.get_results()['execution']['duration']:.3f}s")
    
    # Profile threaded workload
    print("\nProfiling threaded workload...")
    results = profiler.start(thread_workload)
    
    backend_metrics = profiler.get_results()
    print(f"Thread results: {len(results)} workers completed")
    print(f"Parallelism score: {backend_metrics['parallelism_metrics']['overall_parallelism_score']:.3f}")
    
    return backend_metrics


def contracts_example():
    """Example using the contracts Stellar integration."""
    print("\n=== Contracts Example ===")
    
    # Create Stellar profiler
    stellar_profiler = StellarProfiler()
    
    def simulate_stellar_transaction():
        """Simulate a Stellar transaction."""
        time.sleep(0.1)  # Simulate network latency
        return {
            "hash": f"tx_{int(time.time())}",
            "operations": 3,
            "fee": 100,
            "success": True
        }
    
    def simulate_contract_execution():
        """Simulate a smart contract execution."""
        time.sleep(0.05)  # Simulate computation
        return {
            "contract_id": "token_contract",
            "function": "transfer",
            "gas_used": 5000,
            "success": True
        }
    
    # Profile transactions
    print("Profiling Stellar transactions...")
    for i in range(5):
        try:
            result = stellar_profiler.profile_transaction(simulate_stellar_transaction)
            print(f"Transaction {i+1}: {result['hash']}")
        except Exception as e:
            print(f"Transaction {i+1} failed: {e}")
    
    # Profile contract executions
    print("\nProfiling contract executions...")
    for i in range(3):
        try:
            result = stellar_profiler.profile_contract_execution(simulate_contract_execution)
            print(f"Contract {i+1}: {result['contract_id']}")
        except Exception as e:
            print(f"Contract {i+1} failed: {e}")
    
    # Get Stellar metrics
    stellar_metrics = stellar_profiler.get_stellar_metrics()
    print(f"\nStellar Metrics:")
    print(f"  Total transactions: {stellar_metrics['transactions']['total_count']}")
    print(f"  Transaction success rate: {stellar_metrics['transactions']['success_rate']:.3f}")
    print(f"  Total contract calls: {stellar_metrics['contracts']['total_executions']}")
    print(f"  Contract success rate: {stellar_metrics['contracts']['success_rate']:.3f}")
    
    if stellar_metrics['network']['avg_latency'] > 0:
        print(f"  Average network latency: {stellar_metrics['network']['avg_latency']:.3f}s")
    
    return stellar_metrics


def frontend_example():
    """Example showing frontend dashboard integration."""
    print("\n=== Frontend Example ===")
    
    # Create FastAPI app
    app = create_app()
    
    print("Frontend dashboard created!")
    print("To start the dashboard:")
    print("  1. Run: stellar-whisk-dashboard")
    print("  2. Open: http://localhost:8080")
    print("  3. Upload profiling results for visualization")
    
    # Show available routes
    print("\nAvailable API endpoints:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {list(route.methods)[0] if route.methods else 'GET'} {route.path}")
    
    return app


def integrated_example():
    """Example showing full integration of all three components."""
    print("\n=== Integrated Example ===")
    
    # Configure integrated profiler
    config = ProfilingConfig(
        sampling_interval=0.02,
        stellar_profiling=True,
        transaction_tracking=True,
        contract_profiling=True,
        network_monitoring=True,
        track_memory=True,
        track_threads=True,
    )
    
    # Create profilers
    backend_profiler = ParallelismProfiler(config)
    stellar_profiler = StellarProfiler()
    
    def integrated_workload():
        """Workload that uses all components."""
        print("Starting integrated workload...")
        
        # Phase 1: CPU-intensive work
        def compute_task():
            result = sum(i * i for i in range(50000))
            time.sleep(0.05)
            return result
        
        # Phase 2: Parallel processing
        def parallel_task():
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(compute_task) for _ in range(6)]
                return [future.result() for future in futures]
        
        # Phase 3: Stellar operations
        def stellar_operations():
            results = []
            
            # Simulate transactions
            for i in range(4):
                try:
                    result = stellar_profiler.profile_transaction(lambda: {
                        "hash": f"integrated_tx_{i}",
                        "operations": 2,
                        "fee": 150,
                        "success": True
                    })
                    results.append(result)
                    time.sleep(0.02)
                except Exception as e:
                    print(f"Transaction {i} failed: {e}")
            
            # Simulate contract calls
            for i in range(2):
                try:
                    result = stellar_profiler.profile_contract_execution(lambda: {
                        "contract_id": "integrated_contract",
                        "function": "process",
                        "gas_used": 3000,
                        "success": True
                    })
                    results.append(result)
                    time.sleep(0.03)
                except Exception as e:
                    print(f"Contract {i} failed: {e}")
            
            return results
        
        # Execute all phases
        print("  Phase 1: CPU computation")
        compute_result = compute_task()
        
        print("  Phase 2: Parallel processing")
        parallel_results = parallel_task()
        
        print("  Phase 3: Stellar operations")
        stellar_results = stellar_operations()
        
        print("Integrated workload completed!")
        return {
            "compute": compute_result,
            "parallel": parallel_results,
            "stellar": stellar_results
        }
    
    # Run integrated profiling
    results = backend_profiler.start(integrated_workload)
    
    # Get comprehensive metrics
    backend_metrics = backend_profiler.get_results()
    stellar_metrics = stellar_profiler.get_stellar_metrics()
    
    print(f"\n=== Integrated Results ===")
    print(f"Total duration: {backend_metrics['execution']['duration']:.3f}s")
    
    # Backend metrics
    if "parallelism_metrics" in backend_metrics:
        metrics = backend_metrics["parallelism_metrics"]
        print(f"Overall parallelism score: {metrics['overall_parallelism_score']:.3f}")
        
        if "cpu_metrics" in metrics:
            cpu = metrics["cpu_metrics"]
            print(f"Average CPU usage: {cpu['average_usage']:.1f}%")
        
        if "thread_metrics" in metrics:
            threads = metrics["thread_metrics"]
            print(f"Maximum threads: {threads['maximum_thread_count']}")
    
    # Stellar metrics
    print(f"Stellar transactions: {stellar_metrics['transactions']['total_count']}")
    print(f"Stellar contract calls: {stellar_metrics['contracts']['total_executions']}")
    
    if stellar_metrics['network']['avg_latency'] > 0:
        print(f"Network latency: {stellar_metrics['network']['avg_latency']:.3f}s")
    
    # Save results for dashboard
    backend_profiler.save_results("integrated_profiling_results.json")
    print("\nResults saved to 'integrated_profiling_results.json'")
    print("Upload this file to the dashboard for visualization!")
    
    return backend_metrics, stellar_metrics


def main():
    """Run all structured examples."""
    print("Stellar Whisk Parallelism Profiler - Structured Architecture Examples")
    print("=" * 80)
    
    try:
        # Run individual component examples
        backend_metrics = backend_example()
        stellar_metrics = contracts_example()
        frontend_app = frontend_example()
        
        # Run integrated example
        integrated_backend, integrated_stellar = integrated_example()
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("\nNext steps:")
        print("1. Start the dashboard: stellar-whisk-dashboard")
        print("2. Upload 'integrated_profiling_results.json' for visualization")
        print("3. Explore the three-tier architecture:")
        print("   - Backend: Core profiling engine")
        print("   - Contracts: Stellar blockchain integration")
        print("   - Frontend: Web dashboard and visualization")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -e '.[dev]'")


if __name__ == "__main__":
    main()
