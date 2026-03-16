"""
Data collection module for system and Stellar metrics.
"""

import time
import threading
import os
from typing import Dict, List, Optional, Any
import psutil
import platform

from .metrics import CPUMetrics, MemoryMetrics, ThreadMetrics, ProcessMetrics, StellarMetrics


class DataCollector:
    """Collects system and Stellar metrics for parallelism profiling."""
    
    def __init__(self, config):
        self.config = config
        self.system = platform.system()
        self.cpu_count = psutil.cpu_count()
        self.memory_total = psutil.virtual_memory().total
        
        # Track current process for more detailed metrics
        self.current_process = psutil.Process()
        self.current_pid = os.getpid()
        
        # Stellar-specific tracking
        self._stellar_transaction_count = 0
        self._stellar_contract_executions = 0
        self._last_stellar_time = time.time()
        
        # Try to import Stellar SDK
        self.stellar_available = False
        try:
            import stellar_sdk
            self.stellar_available = True
        except ImportError:
            pass
    
    def collect_cpu_metrics(self, timestamp: float) -> CPUMetrics:
        """Collect CPU-related metrics."""
        try:
            # Overall CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Per-CPU usage
            per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
            
            # Load average (Unix-like systems only)
            load_avg = None
            if self.system in ["Linux", "Darwin"]:
                try:
                    load_avg = list(psutil.getloadavg())
                except (AttributeError, OSError):
                    load_avg = None
            
            return CPUMetrics(
                timestamp=timestamp,
                cpu_percent=cpu_percent,
                cpu_count=self.cpu_count,
                load_avg=load_avg,
                per_cpu_percent=per_cpu_percent,
            )
        except Exception as e:
            # Return default values on error
            return CPUMetrics(
                timestamp=timestamp,
                cpu_percent=0.0,
                cpu_count=self.cpu_count,
                load_avg=None,
                per_cpu_percent=[0.0] * self.cpu_count,
            )
    
    def collect_memory_metrics(self, timestamp: float) -> MemoryMetrics:
        """Collect memory-related metrics."""
        try:
            memory_info = psutil.virtual_memory()
            
            return MemoryMetrics(
                timestamp=timestamp,
                memory_percent=memory_info.percent,
                memory_used=memory_info.used,
                memory_available=memory_info.available,
                memory_total=memory_info.total,
            )
        except Exception as e:
            return MemoryMetrics(
                timestamp=timestamp,
                memory_percent=0.0,
                memory_used=0,
                memory_available=self.memory_total,
                memory_total=self.memory_total,
            )
    
    def collect_thread_metrics(self, timestamp: float) -> ThreadMetrics:
        """Collect thread-related metrics."""
        try:
            # Get thread count for current process
            thread_count = self.current_process.num_threads()
            
            # Get all threads and count active ones
            threads = self.current_process.threads()
            active_threads = len([t for t in threads if t.status == "running"])
            
            # Thread states (if available)
            thread_states = {}
            try:
                all_processes = list(psutil.process_iter(['pid', 'num_threads', 'status']))
                for proc in all_processes:
                    try:
                        status = proc.info['status']
                        thread_states[status] = thread_states.get(status, 0) + 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception:
                thread_states = {}
            
            return ThreadMetrics(
                timestamp=timestamp,
                thread_count=thread_count,
                active_threads=active_threads,
                thread_states=thread_states,
            )
        except Exception as e:
            return ThreadMetrics(
                timestamp=timestamp,
                thread_count=0,
                active_threads=0,
                thread_states={},
            )
    
    def collect_process_metrics(self, timestamp: float) -> ProcessMetrics:
        """Collect process-related metrics."""
        try:
            # Count processes by status
            all_processes = list(psutil.process_iter(['status']))
            
            process_count = len(all_processes)
            running_processes = 0
            sleeping_processes = 0
            
            for proc in all_processes:
                try:
                    status = proc.info['status']
                    if status == psutil.STATUS_RUNNING:
                        running_processes += 1
                    elif status in [psutil.STATUS_SLEEPING, psutil.STATUS_DISK_SLEEP]:
                        sleeping_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return ProcessMetrics(
                timestamp=timestamp,
                process_count=process_count,
                running_processes=running_processes,
                sleeping_processes=sleeping_processes,
            )
        except Exception as e:
            return ProcessMetrics(
                timestamp=timestamp,
                process_count=0,
                running_processes=0,
                sleeping_processes=0,
            )
    
    def collect_stellar_metrics(self, timestamp: float) -> Optional[StellarMetrics]:
        """Collect Stellar-specific metrics."""
        if not self.config.stellar_profiling:
            return None
        
        try:
            # Calculate transaction rate
            current_time = time.time()
            time_diff = current_time - self._last_stellar_time
            
            if time_diff > 0:
                transaction_rate = self._stellar_transaction_count / time_diff
            else:
                transaction_rate = 0.0
            
            # Simulate network latency (in real implementation, this would ping Stellar nodes)
            network_latency = self._measure_stellar_network_latency()
            
            # Collect Stellar operations (placeholder for real implementation)
            stellar_operations = self._collect_stellar_operations()
            
            metrics = StellarMetrics(
                timestamp=timestamp,
                transaction_count=self._stellar_transaction_count,
                transaction_rate=transaction_rate,
                contract_executions=self._stellar_contract_executions,
                network_latency=network_latency,
                stellar_operations=stellar_operations,
            )
            
            # Reset counters for next interval
            self._stellar_transaction_count = 0
            self._stellar_contract_executions = 0
            self._last_stellar_time = current_time
            
            return metrics
            
        except Exception as e:
            return StellarMetrics(
                timestamp=timestamp,
                transaction_count=0,
                transaction_rate=0.0,
                contract_executions=0,
                network_latency=0.0,
                stellar_operations=[],
            )
    
    def _measure_stellar_network_latency(self) -> float:
        """Measure latency to Stellar network."""
        if not self.stellar_available:
            return 0.0
        
        try:
            import stellar_sdk
            from stellar_sdk.server import Server
            
            # Use public horizon server for latency measurement
            server = Server("https://horizon.stellar.org")
            
            start_time = time.time()
            # Make a simple request to measure latency
            server.fetch_base_fee()
            end_time = time.time()
            
            return end_time - start_time
            
        except Exception:
            return 0.0
    
    def _collect_stellar_operations(self) -> List[Dict[str, Any]]:
        """Collect recent Stellar operations."""
        if not self.stellar_available:
            return []
        
        try:
            import stellar_sdk
            from stellar_sdk.server import Server
            
            server = Server("https://horizon.stellar.org")
            
            # Get recent operations (limited to avoid too much data)
            operations = server.operations().limit(10).call()
            
            stellar_ops = []
            for op in operations.get('_embedded', {}).get('records', []):
                stellar_ops.append({
                    'id': op.get('id'),
                    'type': op.get('type'),
                    'transaction_hash': op.get('transaction_hash'),
                    'created_at': op.get('created_at'),
                })
            
            return stellar_ops
            
        except Exception:
            return []
    
    def increment_stellar_transaction(self):
        """Increment Stellar transaction counter."""
        self._stellar_transaction_count += 1
    
    def increment_stellar_contract_execution(self):
        """Increment Stellar contract execution counter."""
        self._stellar_contract_executions += 1
    
    def collect_detailed_process_metrics(self, timestamp: float) -> Dict[str, Any]:
        """Collect detailed metrics for the current process."""
        try:
            process = psutil.Process(self.current_pid)
            
            # CPU metrics for current process
            process_cpu = process.cpu_percent()
            process_cpu_times = process.cpu_times()
            
            # Memory metrics for current process
            process_memory = process.memory_info()
            process_memory_percent = process.memory_percent()
            
            # Thread metrics for current process
            process_threads = process.threads()
            process_num_threads = process.num_threads()
            
            # File descriptors (Unix-like systems)
            process_fd_count = None
            if self.system in ["Linux", "Darwin"]:
                try:
                    process_fd_count = process.num_fds()
                except (AttributeError, psutil.AccessDenied):
                    pass
            
            # Context switches (if available)
            process_ctx_switches = None
            try:
                process_ctx_switches = process.num_ctx_switches()
            except (AttributeError, psutil.AccessDenied):
                pass
            
            return {
                "timestamp": timestamp,
                "pid": self.current_pid,
                "cpu": {
                    "percent": process_cpu,
                    "user_time": process_cpu_times.user,
                    "system_time": process_cpu_times.system,
                    "children_user_time": process_cpu_times.children_user,
                    "children_system_time": process_cpu_times.children_system,
                },
                "memory": {
                    "rss": process_memory.rss,
                    "vms": process_memory.vms,
                    "percent": process_memory_percent,
                    "shared": getattr(process_memory, 'shared', 0),
                    "text": getattr(process_memory, 'text', 0),
                    "lib": getattr(process_memory, 'lib', 0),
                    "data": getattr(process_memory, 'data', 0),
                    "dirty": getattr(process_memory, 'dirty', 0),
                },
                "threads": {
                    "count": process_num_threads,
                    "details": [
                        {
                            "id": thread.id,
                            "user_time": thread.user_time,
                            "system_time": thread.system_time,
                        }
                        for thread in process_threads
                    ],
                },
                "file_descriptors": process_fd_count,
                "context_switches": {
                    "voluntary": getattr(process_ctx_switches, 'voluntary', 0) if process_ctx_switches else 0,
                    "involuntary": getattr(process_ctx_switches, 'involuntary', 0) if process_ctx_switches else 0,
                } if process_ctx_switches else None,
            }
        except Exception as e:
            return {
                "timestamp": timestamp,
                "pid": self.current_pid,
                "error": str(e),
            }
    
    def collect_gpu_metrics(self, timestamp: float) -> Optional[Dict[str, Any]]:
        """Collect GPU metrics if available."""
        if not self.config.gpu_profiling:
            return None
        
        try:
            # Try to import GPU monitoring libraries
            import pynvml
            
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            gpu_metrics = []
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # GPU utilization
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = utilization.gpu
                memory_util = utilization.memory
                
                # Memory info
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_used = memory_info.used
                memory_total = memory_info.total
                memory_free = memory_info.free
                
                # Temperature
                try:
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temperature = None
                
                # Power usage
                try:
                    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                except:
                    power_usage = None
                
                gpu_metrics.append({
                    "device_id": i,
                    "gpu_utilization": gpu_util,
                    "memory_utilization": memory_util,
                    "memory_used": memory_used,
                    "memory_total": memory_total,
                    "memory_free": memory_free,
                    "temperature": temperature,
                    "power_usage": power_usage,
                })
            
            return {
                "timestamp": timestamp,
                "devices": gpu_metrics,
            }
        except ImportError:
            # pynvml not available
            return None
        except Exception as e:
            # Error collecting GPU metrics
            return {
                "timestamp": timestamp,
                "error": str(e),
            }
    
    def collect_network_metrics(self, timestamp: float) -> Optional[Dict[str, Any]]:
        """Collect network metrics if enabled."""
        if not self.config.network_profiling:
            return None
        
        try:
            # Network I/O counters
            net_io = psutil.net_io_counters()
            
            # Network connections
            connections = list(psutil.net_connections())
            
            # Count connections by status
            connection_stats = {}
            for conn in connections:
                status = conn.status
                connection_stats[status] = connection_stats.get(status, 0) + 1
            
            return {
                "timestamp": timestamp,
                "io": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout,
                },
                "connections": {
                    "total": len(connections),
                    "by_status": connection_stats,
                },
            }
        except Exception as e:
            return {
                "timestamp": timestamp,
                "error": str(e),
            }
    
    def collect_io_metrics(self, timestamp: float) -> Optional[Dict[str, Any]]:
        """Collect I/O metrics if enabled."""
        if not self.config.io_profiling:
            return None
        
        try:
            # Disk I/O counters
            disk_io = psutil.disk_io_counters()
            
            # Process I/O counters
            process_io = self.current_process.io_counters()
            
            return {
                "timestamp": timestamp,
                "disk": {
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count,
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_time": disk_io.read_time,
                    "write_time": disk_io.write_time,
                } if disk_io else None,
                "process": {
                    "read_count": process_io.read_count,
                    "write_count": process_io.write_count,
                    "read_bytes": process_io.read_bytes,
                    "write_bytes": process_io.write_bytes,
                    "read_chars": getattr(process_io, 'read_chars', 0),
                    "write_chars": getattr(process_io, 'write_chars', 0),
                },
            }
        except Exception as e:
            return {
                "timestamp": timestamp,
                "error": str(e),
            }
