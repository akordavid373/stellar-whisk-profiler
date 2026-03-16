# Architecture Documentation

## Overview

Stellar Whisk Parallelism Profiler is organized into three main components:

```
stellar-whisk-profiler/
├── frontend/                # Web dashboard and UI
├── backend/                 # Core profiling engine and API
├── contracts/               # Stellar smart contracts and integration
├── stellar_whisk_profiler/  # Main package entry point
├── examples/                # Usage examples
├── tests/                   # Test suite
└── docs/                    # Documentation
```

## Frontend

The frontend provides the web-based user interface for visualizing profiling results.

### Components
- **Dashboard**: Main web interface built with FastAPI
- **Templates**: HTML templates with TailwindCSS styling
- **Static Assets**: JavaScript, CSS, and other static files
- **Routes**: API endpoints for data access

### Key Features
- Real-time charts using Plotly
- Interactive data visualization
- Stellar-specific analytics
- Responsive design

### Technology Stack
- FastAPI for web framework
- Jinja2 for templating
- TailwindCSS for styling
- Plotly for charts
- Vanilla JavaScript for interactions

## Backend

The backend contains the core profiling engine and data collection logic.

### Components
- **Profiler**: Main profiling orchestration
- **Metrics**: Data structures and analysis
- **Collector**: System and Stellar data collection
- **Sampler**: Adaptive sampling engine
- **CLI**: Command-line interface

### Key Features
- Real-time system monitoring
- Adaptive sampling algorithms
- Stellar-specific metrics collection
- Multiple output formats

### Technology Stack
- Python 3.8+
- psutil for system metrics
- Stellar SDK for blockchain integration
- NumPy/Pandas for data processing
- Threading for concurrent operations

## Contracts

The contracts module handles all Stellar blockchain-specific functionality.

### Components
- **Stellar Profiler**: Transaction and contract profiling
- **Metrics Collector**: Stellar-specific metrics
- **Data Collector**: Horizon API integration
- **Instrumentation**: Decorators and helpers

### Key Features
- Transaction performance monitoring
- Smart contract execution analysis
- Network latency measurement
- Horizon API integration

### Technology Stack
- Stellar SDK
- Soroban CLI
- Horizon API
- Async/await for network operations

## Data Flow

```
User Application
       ↓
   Backend Profiler
       ↓
   System + Stellar Metrics
       ↓
   Data Processing & Analysis
       ↓
   Frontend Dashboard
       ↓
   User Visualization
```

## Integration Points

### Backend ↔ Contracts
- Backend calls Contracts for Stellar-specific profiling
- Contracts provide metrics to Backend
- Shared data structures for metrics

### Backend ↔ Frontend
- Backend provides REST API
- Frontend consumes API endpoints
- Real-time data streaming

### Contracts ↔ Stellar Network
- Horizon API calls
- Transaction monitoring
- Network latency measurement

## Configuration

The system uses a layered configuration approach:

1. **Global Config**: Main profiling settings
2. **Stellar Config**: Blockchain-specific settings
3. **Sampling Config**: Data collection parameters
4. **Frontend Config**: Dashboard settings

## Extensibility

The architecture supports extensions through:

1. **Plugin System**: Custom metric collectors
2. **Decorator Pattern**: Easy instrumentation
3. **Callback System**: Event-driven architecture
4. **Modular Design**: Independent components

## Performance Considerations

1. **Adaptive Sampling**: Reduces overhead
2. **Async Operations**: Non-blocking I/O
3. **Memory Management**: Efficient data structures
4. **Caching**: Reduce redundant API calls

## Security

1. **API Authentication**: Secure dashboard access
2. **Data Privacy**: Local processing only
3. **Network Security**: HTTPS for Stellar API
4. **Input Validation**: Prevent injection attacks
