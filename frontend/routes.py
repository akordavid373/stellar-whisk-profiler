"""
API routes for the Stellar Whisk dashboard.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import json
import tempfile
import os
from pathlib import Path

router = APIRouter()

# In-memory storage for profiling results (in production, use a database)
profiling_results: Dict[str, Dict[str, Any]] = {}


@router.post("/upload")
async def upload_profiling_results(file: UploadFile = File(...)):
    """Upload profiling results from a file."""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")
    
    try:
        # Read file content
        content = await file.read()
        results = json.loads(content.decode('utf-8'))
        
        # Generate a unique ID for this result
        result_id = f"stellar_result_{len(profiling_results) + 1}"
        profiling_results[result_id] = results
        
        return {
            "id": result_id,
            "message": "Results uploaded successfully",
            "summary": {
                "duration": results.get("execution", {}).get("duration", 0),
                "parallelism_score": results.get("parallelism_metrics", {}).get("overall_parallelism_score", 0),
                "stellar_enabled": results.get("config", {}).get("tracking", {}).get("stellar", False),
            }
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/results")
async def list_profiling_results():
    """List all available profiling results."""
    results_list = []
    
    for result_id, results in profiling_results.items():
        results_list.append({
            "id": result_id,
            "duration": results.get("execution", {}).get("duration", 0),
            "parallelism_score": results.get("parallelism_metrics", {}).get("overall_parallelism_score", 0),
            "stellar_enabled": results.get("config", {}).get("tracking", {}).get("stellar", False),
            "timestamp": results.get("execution", {}).get("start_time", 0),
        })
    
    return {"results": results_list}


@router.get("/results/{result_id}")
async def get_profiling_result(result_id: str):
    """Get a specific profiling result."""
    if result_id not in profiling_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return profiling_results[result_id]


@router.get("/results/{result_id}/summary")
async def get_result_summary(result_id: str):
    """Get a summary of a profiling result."""
    if result_id not in profiling_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    results = profiling_results[result_id]
    metrics = results.get("parallelism_metrics", {})
    
    summary = {
        "execution": results.get("execution", {}),
        "cpu_metrics": metrics.get("cpu_metrics", {}),
        "thread_metrics": metrics.get("thread_metrics", {}),
        "memory_metrics": metrics.get("memory_metrics", {}),
        "stellar_metrics": metrics.get("stellar_metrics", {}),
        "overall_score": metrics.get("overall_parallelism_score", 0),
    }
    
    return summary


@router.get("/results/{result_id}/timeseries")
async def get_timeseries_data(result_id: str, metric: str = "cpu"):
    """Get time series data for a specific metric."""
    if result_id not in profiling_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    results = profiling_results[result_id]
    raw_data = results.get("raw_data", {})
    
    if metric not in raw_data:
        raise HTTPException(status_code=400, detail=f"Metric '{metric}' not available")
    
    return {
        "metric": metric,
        "data": raw_data[metric],
    }


@router.get("/results/{result_id}/stellar-analysis")
async def get_stellar_analysis(result_id: str):
    """Get detailed Stellar analysis of a profiling result."""
    if result_id not in profiling_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    results = profiling_results[result_id]
    metrics = results.get("parallelism_metrics", {})
    stellar_metrics = metrics.get("stellar_metrics", {})
    
    # Generate Stellar-specific insights and recommendations
    insights = []
    recommendations = []
    
    if "error" not in stellar_metrics:
        # Transaction analysis
        total_transactions = stellar_metrics.get("total_transactions", 0)
        avg_tx_rate = stellar_metrics.get("average_transaction_rate", 0)
        
        if total_transactions == 0:
            insights.append("No Stellar transactions detected during profiling")
            recommendations.append("Ensure Stellar SDK integration is properly configured")
        elif avg_tx_rate < 1.0:
            insights.append("Low transaction rate detected")
            recommendations.append("Consider batching transactions or optimizing network calls")
        elif avg_tx_rate > 10.0:
            insights.append("High transaction rate - good for throughput")
            recommendations.append("Monitor for rate limiting and network congestion")
        
        # Contract analysis
        total_contracts = stellar_metrics.get("total_contract_executions", 0)
        if total_contracts > 0:
            insights.append(f"Detected {total_contracts} smart contract executions")
            
            if total_contracts < 5:
                recommendations.append("Consider more frequent contract interactions for better testing")
            else:
                recommendations.append("Good contract activity detected - monitor gas efficiency")
        
        # Network analysis
        avg_latency = stellar_metrics.get("average_network_latency", 0)
        if avg_latency > 2.0:
            insights.append("High network latency detected")
            recommendations.append("Consider using closer Horizon servers or optimizing network configuration")
        elif avg_latency > 0:
            insights.append("Network latency is within acceptable range")
        
        # Stellar efficiency
        stellar_efficiency = stellar_metrics.get("stellar_efficiency", 0)
        if stellar_efficiency < 0.3:
            insights.append("Low Stellar efficiency detected")
            recommendations.append("Review transaction patterns and contract optimization")
        elif stellar_efficiency > 0.7:
            insights.append("Excellent Stellar efficiency")
    
    return {
        "insights": insights,
        "recommendations": recommendations,
        "stellar_metrics": stellar_metrics,
        "stellar_efficiency": stellar_metrics.get("stellar_efficiency", 0) if "error" not in stellar_metrics else 0,
    }


@router.get("/results/{result_id}/analysis")
async def get_analysis(result_id: str):
    """Get detailed analysis of a profiling result."""
    if result_id not in profiling_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    results = profiling_results[result_id]
    metrics = results.get("parallelism_metrics", {})
    
    # Generate insights and recommendations
    insights = []
    recommendations = []
    
    # CPU analysis
    cpu_metrics = metrics.get("cpu_metrics", {})
    if cpu_metrics:
        avg_cpu = cpu_metrics.get("average_usage", 0)
        max_cpu = cpu_metrics.get("maximum_usage", 0)
        efficiency = cpu_metrics.get("efficiency", 0)
        
        if avg_cpu < 30:
            insights.append("Low CPU utilization suggests the application may be I/O bound or not well parallelized")
            recommendations.append("Consider optimizing algorithms for better parallelism")
        elif avg_cpu > 80:
            insights.append("High CPU utilization indicates good parallelism but potential bottlenecks")
            recommendations.append("Monitor for CPU saturation and consider load balancing")
        
        if efficiency < 0.5:
            insights.append("Low CPU efficiency indicates inconsistent utilization")
            recommendations.append("Investigate CPU contention and synchronization issues")
    
    # Thread analysis
    thread_metrics = metrics.get("thread_metrics", {})
    if thread_metrics:
        thread_efficiency = thread_metrics.get("thread_efficiency", 0)
        contention = thread_metrics.get("thread_contention", 0)
        
        if thread_efficiency < 0.6:
            insights.append("Low thread efficiency suggests many threads are idle")
            recommendations.append("Review thread pool sizing and work distribution")
        
        if contention > 0.5:
            insights.append("High thread contention detected")
            recommendations.append("Consider reducing synchronization or using lock-free algorithms")
    
    # Memory analysis
    memory_metrics = metrics.get("memory_metrics", {})
    if memory_metrics:
        memory_efficiency = memory_metrics.get("memory_efficiency", 0)
        avg_memory = memory_metrics.get("average_memory_usage", 0)
        
        if avg_memory > 80:
            insights.append("High memory usage may cause performance degradation")
            recommendations.append("Consider memory optimization techniques")
        
        if memory_efficiency < 0.5:
            insights.append("Inconsistent memory usage patterns detected")
            recommendations.append("Investigate memory allocation patterns and potential leaks")
    
    # Stellar-specific analysis
    stellar_metrics = metrics.get("stellar_metrics", {})
    if "error" not in stellar_metrics:
        total_transactions = stellar_metrics.get("total_transactions", 0)
        if total_transactions > 0:
            insights.append(f"Stellar activity detected: {total_transactions} transactions")
            
            stellar_efficiency = stellar_metrics.get("stellar_efficiency", 0)
            if stellar_efficiency < 0.5:
                recommendations.append("Optimize Stellar transaction patterns for better efficiency")
    
    return {
        "insights": insights,
        "recommendations": recommendations,
        "metrics": {
            "cpu": cpu_metrics,
            "threads": thread_metrics,
            "memory": memory_metrics,
            "stellar": stellar_metrics,
        },
        "overall_score": metrics.get("overall_parallelism_score", 0),
    }


@router.delete("/results/{result_id}")
async def delete_profiling_result(result_id: str):
    """Delete a profiling result."""
    if result_id not in profiling_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    del profiling_results[result_id]
    return {"message": "Result deleted successfully"}


@router.get("/metrics")
async def get_available_metrics():
    """Get list of available metrics types."""
    return {
        "metrics": [
            "cpu",
            "memory", 
            "threads",
            "processes",
            "stellar",
        ],
        "descriptions": {
            "cpu": "CPU utilization and performance metrics",
            "memory": "Memory usage and allocation patterns",
            "threads": "Thread activity and contention metrics",
            "processes": "Process-level parallelism metrics",
            "stellar": "Stellar blockchain-specific metrics",
        }
    }


@router.get("/health")
async def health_check():
    """Health check for the API."""
    return {
        "status": "healthy",
        "service": "stellar-whisk-dashboard-api",
        "results_count": len(profiling_results),
    }
