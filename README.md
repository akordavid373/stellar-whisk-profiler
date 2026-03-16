# Stellar Whisk Parallelism Profiler

A comprehensive infrastructure for profiling and analyzing parallelism in Stellar blockchain applications.

## Overview

The Stellar Whisk Parallelism Profiler is designed to help developers and researchers understand the parallel characteristics of their Stellar applications, identify bottlenecks, and optimize performance for multi-core and distributed systems.

## Architecture

```
stellar-whisk-profiler/
├── frontend/                # Web dashboard and UI
├── backend/                 # Core profiling engine and API
├── contracts/               # Stellar smart contracts and integration
├── examples/                # Usage examples
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## Components

### Frontend
- **Web Dashboard**: Interactive visualization of profiling results
- **Real-time Charts**: CPU, memory, threads, and Stellar metrics
- **Stellar Analytics**: Transaction and contract performance insights
- **Responsive Design**: Modern UI with TailwindCSS and Plotly

### Backend
- **Profiling Engine**: Core parallelism monitoring system
- **Data Collection**: System and Stellar-specific metrics
- **REST API**: FastAPI-based data access endpoints
- **Adaptive Sampling**: Intelligent data collection algorithms

### Contracts
- **Stellar Integration**: Horizon API and Soroban support
- **Transaction Profiling**: Monitor transaction performance
- **Contract Analysis**: Smart contract execution metrics
- **Network Monitoring**: Latency and throughput analysis

## Features

- **Real-time Parallelism Monitoring**: Track thread utilization, synchronization patterns, and resource contention
- **Stellar-Specific Metrics**: Monitor transaction processing, smart contract execution, and network operations
- **Performance Analytics**: Detailed analysis of parallel efficiency, speedup, and scalability
- **Interactive Dashboard**: Web-based visualization with charts and insights
- **Integration Support**: Compatible with Stellar SDK and Soroban smart contracts
- **Export Capabilities**: Generate reports in multiple formats (JSON, CSV, HTML)

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Run Examples**
   ```bash
   make run-examples
   ```

3. **Start Dashboard**
   ```bash
   make start-dashboard
   ```

4. **Profile Your App**
   ```bash
   stellar-whisk-profiler profile --module your_stellar_app.py --stellar
   ```

## Stellar Integration

The profiler includes specialized agents for Stellar ecosystem:

- **Transaction Profiling**: Monitor parallel transaction processing
- **Smart Contract Analysis**: Profile Soroban contract execution
- **Network Metrics**: Track Stellar network operations and latency
- **Resource Usage**: Monitor CPU, memory, and network during Stellar operations

## Documentation

- [Installation Guide](docs/installation.md)
- [Frontend Guide](docs/frontend.md)
- [Backend API](docs/backend-api.md)
- [Contract Integration](docs/contracts.md)
- [User Manual](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Contributing Guide](docs/contributing.md)

## Repository

**Repository**: https://github.com/stellar/stellar-whisk-profiler

**Organization**: [Stellar Development Foundation](https://github.com/stellar)

## License

MIT License - see [LICENSE](LICENSE) file for details.
