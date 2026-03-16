"""
Command-line interface for Stellar Whisk Parallelism Profiler.
"""

import argparse
import sys
import time
import importlib.util
from typing import Optional
from pathlib import Path

from .core.profiler import ParallelismProfiler, ProfilingConfig


def load_target_module(target_path: str):
    """Load a Python module from file path."""
    path = Path(target_path)
    if not path.exists():
        raise FileNotFoundError(f"Target file not found: {target_path}")
    
    spec = importlib.util.spec_from_file_location("target_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module


def create_config_from_args(args) -> ProfilingConfig:
    """Create profiling configuration from command-line arguments."""
    return ProfilingConfig(
        sampling_interval=args.interval,
        max_duration=args.duration,
        track_memory=args.track_memory,
        track_cpu=args.track_cpu,
        track_threads=args.track_threads,
        track_processes=args.track_processes,
        enable_call_stack=args.call_stack,
        output_format=args.format,
        stellar_profiling=args.stellar,
        transaction_tracking=args.transactions,
        contract_profiling=args.contracts,
        network_monitoring=args.network,
        gpu_profiling=args.gpu,
        io_profiling=args.io,
    )


def run_profiling(args):
    """Run profiling on target function."""
    config = create_config_from_args(args)
    profiler = ParallelismProfiler(config)
    
    if args.module:
        # Load module and find main function
        module = load_target_module(args.module)
        target_func = getattr(module, args.function or "main", None)
        if not target_func:
            raise ValueError(f"Function '{args.function or 'main'}' not found in module")
        
        print(f"Profiling function '{args.function or 'main'}' from {args.module}")
        results = profiler.start(target_func)
        
    elif args.command:
        # Run shell command
        import subprocess
        print(f"Profiling command: {args.command}")
        
        def run_command():
            result = subprocess.run(args.command, shell=True, capture_output=True, text=True)
            return result
        
        results = profiler.start(run_command)
        
    else:
        raise ValueError("Either --module or --command must be specified")
    
    # Save results
    if args.output:
        profiler.save_results(args.output, args.format)
        print(f"Results saved to {args.output}")
    else:
        # Print summary
        print("\n=== Stellar Profiling Results ===")
        print(f"Duration: {results['execution']['duration']:.2f} seconds")
        
        if "parallelism_metrics" in results:
            metrics = results["parallelism_metrics"]
            
            if "cpu_metrics" in metrics:
                cpu = metrics["cpu_metrics"]
                print(f"Average CPU Usage: {cpu['average_usage']:.1f}%")
                print(f"Maximum CPU Usage: {cpu['maximum_usage']:.1f}%")
                print(f"CPU Efficiency: {cpu['efficiency']:.3f}")
                print(f"Parallelism Factor: {cpu['parallelism_factor']:.3f}")
            
            if "thread_metrics" in metrics:
                threads = metrics["thread_metrics"]
                print(f"Average Thread Count: {threads['average_thread_count']:.1f}")
                print(f"Maximum Thread Count: {threads['maximum_thread_count']}")
            
            if "stellar_metrics" in metrics and "error" not in metrics["stellar_metrics"]:
                stellar = metrics["stellar_metrics"]
                print(f"Total Transactions: {stellar['total_transactions']}")
                print(f"Average Transaction Rate: {stellar['average_transaction_rate']:.2f} tx/s")
                print(f"Total Contract Executions: {stellar['total_contract_executions']}")
                print(f"Average Network Latency: {stellar['average_network_latency']:.3f}s")
                print(f"Stellar Efficiency: {stellar['stellar_efficiency']:.3f}")
            
            if "overall_parallelism_score" in metrics:
                score = metrics["overall_parallelism_score"]
                print(f"Overall Parallelism Score: {score:.3f}")
    
    return results


def start_dashboard(args):
    """Start the web dashboard."""
    from .dashboard import create_app
    
    app = create_app()
    
    print(f"Starting Stellar Whisk Dashboard on http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop")
    
    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Stellar Whisk Parallelism Profiler - Profile and analyze parallelism in Stellar applications"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Profile a target application")
    
    # Target specification
    target_group = profile_parser.add_mutually_exclusive_group(required=True)
    target_group.add_argument(
        "--module", "-m",
        help="Python module file to profile"
    )
    target_group.add_argument(
        "--command", "-c",
        help="Shell command to profile"
    )
    
    profile_parser.add_argument(
        "--function", "-f",
        help="Function name to profile (default: main)"
    )
    
    # Profiling options
    profile_parser.add_argument(
        "--interval", "-i",
        type=float,
        default=0.1,
        help="Sampling interval in seconds (default: 0.1)"
    )
    
    profile_parser.add_argument(
        "--duration", "-d",
        type=float,
        help="Maximum profiling duration in seconds"
    )
    
    profile_parser.add_argument(
        "--output", "-o",
        help="Output file for results"
    )
    
    profile_parser.add_argument(
        "--format",
        choices=["json", "csv", "html"],
        default="json",
        help="Output format (default: json)"
    )
    
    # Tracking options
    tracking_group = profile_parser.add_argument_group("Tracking Options")
    tracking_group.add_argument(
        "--no-memory",
        dest="track_memory",
        action="store_false",
        default=True,
        help="Disable memory tracking"
    )
    
    tracking_group.add_argument(
        "--no-cpu",
        dest="track_cpu", 
        action="store_false",
        default=True,
        help="Disable CPU tracking"
    )
    
    tracking_group.add_argument(
        "--no-threads",
        dest="track_threads",
        action="store_false", 
        default=True,
        help="Disable thread tracking"
    )
    
    tracking_group.add_argument(
        "--no-processes",
        dest="track_processes",
        action="store_false",
        default=True,
        help="Disable process tracking"
    )
    
    # Stellar-specific options
    stellar_group = profile_parser.add_argument_group("Stellar Options")
    stellar_group.add_argument(
        "--no-stellar",
        dest="stellar",
        action="store_false",
        default=True,
        help="Disable Stellar-specific profiling"
    )
    
    stellar_group.add_argument(
        "--no-transactions",
        dest="transactions",
        action="store_false",
        default=True,
        help="Disable transaction tracking"
    )
    
    stellar_group.add_argument(
        "--no-contracts",
        dest="contracts",
        action="store_false",
        default=True,
        help="Disable contract profiling"
    )
    
    stellar_group.add_argument(
        "--no-network",
        dest="network",
        action="store_false",
        default=True,
        help="Disable network monitoring"
    )
    
    # Advanced options
    advanced_group = profile_parser.add_argument_group("Advanced Options")
    advanced_group.add_argument(
        "--call-stack",
        action="store_true",
        help="Enable call stack profiling"
    )
    
    advanced_group.add_argument(
        "--gpu",
        action="store_true",
        help="Enable GPU profiling"
    )
    
    advanced_group.add_argument(
        "--io",
        action="store_true",
        help="Enable I/O profiling"
    )
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Start web dashboard")
    dashboard_parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind dashboard (default: localhost)"
    )
    dashboard_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind dashboard (default: 8080)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "profile":
            run_profiling(args)
        elif args.command == "dashboard":
            start_dashboard(args)
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nProfiling interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
