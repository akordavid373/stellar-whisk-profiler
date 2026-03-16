"""
Sampling engine for controlled data collection.
"""

import time
import threading
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from queue import Queue, Empty
import logging

from .collector import DataCollector


@dataclass
class SamplingConfig:
    """Configuration for sampling behavior."""
    interval: float = 0.1  # seconds between samples
    buffer_size: int = 1000  # maximum samples to buffer
    adaptive_sampling: bool = True  # enable adaptive sampling
    min_interval: float = 0.01  # minimum sampling interval
    max_interval: float = 1.0  # maximum sampling interval
    cpu_threshold: float = 80.0  # CPU threshold for adaptive sampling


class SamplingEngine:
    """Advanced sampling engine with adaptive capabilities."""
    
    def __init__(self, config):
        self.config = config
        self.collector = DataCollector(config)
        
        self._sampling_thread = None
        self._stop_event = threading.Event()
        self._sample_queue = Queue(maxsize=1000)
        
        # Adaptive sampling state
        self._current_interval = config.sampling_interval
        self._last_cpu_usage = 0.0
        self._sampling_history = []
        
        self.logger = logging.getLogger(__name__)
    
    def start_sampling(self) -> None:
        """Start the sampling thread."""
        if self._sampling_thread and self._sampling_thread.is_alive():
            raise RuntimeError("Sampling already started")
        
        self._stop_event.clear()
        self._sampling_thread = threading.Thread(
            target=self._sampling_loop,
            daemon=True
        )
        self._sampling_thread.start()
        self.logger.info("Sampling started")
    
    def stop_sampling(self) -> None:
        """Stop the sampling thread."""
        if self._sampling_thread:
            self._stop_event.set()
            self._sampling_thread.join(timeout=2.0)
            self.logger.info("Sampling stopped")
    
    def _sampling_loop(self) -> None:
        """Main sampling loop."""
        while not self._stop_event.is_set():
            start_time = time.time()
            
            try:
                # Collect all metrics
                timestamp = start_time
                sample = self._collect_sample(timestamp)
                
                # Add to queue (non-blocking)
                try:
                    self._sample_queue.put(sample, block=False)
                except:
                    # Queue is full, remove oldest sample
                    try:
                        self._sample_queue.get(block=False)
                        self._sample_queue.put(sample, block=False)
                    except Empty:
                        pass
                
                # Update adaptive sampling if enabled
                if self.config.adaptive_sampling:
                    self._update_sampling_interval(sample)
                
            except Exception as e:
                self.logger.error(f"Error in sampling loop: {e}")
            
            # Calculate sleep time
            elapsed = time.time() - start_time
            sleep_time = max(0, self._current_interval - elapsed)
            
            # Sleep with interruptible wait
            self._stop_event.wait(sleep_time)
    
    def _collect_sample(self, timestamp: float) -> Dict[str, Any]:
        """Collect a complete sample of all metrics."""
        sample = {
            "timestamp": timestamp,
        }
        
        # Basic metrics (always collected)
        sample["cpu"] = self.collector.collect_cpu_metrics(timestamp)
        sample["memory"] = self.collector.collect_memory_metrics(timestamp)
        sample["threads"] = self.collector.collect_thread_metrics(timestamp)
        sample["processes"] = self.collector.collect_process_metrics(timestamp)
        
        # Stellar metrics (if enabled)
        if self.config.stellar_profiling:
            sample["stellar"] = self.collector.collect_stellar_metrics(timestamp)
        
        # Optional metrics based on configuration
        if self.config.track_memory:
            sample["detailed_process"] = self.collector.collect_detailed_process_metrics(timestamp)
        
        if self.config.gpu_profiling:
            sample["gpu"] = self.collector.collect_gpu_metrics(timestamp)
        
        if self.config.network_profiling:
            sample["network"] = self.collector.collect_network_metrics(timestamp)
        
        if self.config.io_profiling:
            sample["io"] = self.collector.collect_io_metrics(timestamp)
        
        return sample
    
    def _update_sampling_interval(self, sample: Dict[str, Any]) -> None:
        """Update sampling interval based on system activity."""
        if not sample.get("cpu"):
            return
        
        current_cpu = sample["cpu"].cpu_percent
        
        # Store in history
        self._sampling_history.append({
            "timestamp": sample["timestamp"],
            "cpu_usage": current_cpu,
            "interval": self._current_interval,
        })
        
        # Keep history limited
        if len(self._sampling_history) > 100:
            self._sampling_history.pop(0)
        
        # Adaptive logic
        if current_cpu > self.config.cpu_threshold:
            # High CPU usage - sample more frequently
            new_interval = max(
                self.config.min_interval,
                self._current_interval * 0.8
            )
        elif current_cpu < self.config.cpu_threshold / 2:
            # Low CPU usage - sample less frequently
            new_interval = min(
                self.config.max_interval,
                self._current_interval * 1.2
            )
        else:
            # Moderate CPU usage - maintain current interval
            new_interval = self._current_interval
        
        # Apply change if significant
        if abs(new_interval - self._current_interval) > 0.01:
            self._current_interval = new_interval
            self.logger.debug(f"Updated sampling interval to {self._current_interval:.3f}s")
    
    def get_samples(self, max_samples: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get collected samples from the queue."""
        samples = []
        
        while True:
            try:
                sample = self._sample_queue.get(block=False)
                samples.append(sample)
                
                if max_samples and len(samples) >= max_samples:
                    break
            except Empty:
                break
        
        return samples
    
    def get_latest_sample(self) -> Optional[Dict[str, Any]]:
        """Get the most recent sample."""
        samples = self.get_samples(max_samples=1)
        return samples[0] if samples else None
    
    def clear_samples(self) -> None:
        """Clear all samples from the queue."""
        while True:
            try:
                self._sample_queue.get(block=False)
            except Empty:
                break
    
    def get_sampling_stats(self) -> Dict[str, Any]:
        """Get statistics about sampling behavior."""
        if not self._sampling_history:
            return {"error": "No sampling history available"}
        
        cpu_usages = [h["cpu_usage"] for h in self._sampling_history]
        intervals = [h["interval"] for h in self._sampling_history]
        
        return {
            "total_samples": len(self._sampling_history),
            "average_cpu_usage": sum(cpu_usages) / len(cpu_usages),
            "current_interval": self._current_interval,
            "average_interval": sum(intervals) / len(intervals),
            "min_interval": min(intervals),
            "max_interval": max(intervals),
            "adaptive_efficiency": self._calculate_adaptive_efficiency(),
        }
    
    def _calculate_adaptive_efficiency(self) -> float:
        """Calculate how well adaptive sampling is working."""
        if len(self._sampling_history) < 10:
            return 0.0
        
        # Look at correlation between CPU usage and sampling frequency
        recent_history = self._sampling_history[-20:]
        
        # Calculate how often we increased sampling during high CPU
        high_cpu_samples = [h for h in recent_history if h["cpu_usage"] > self.config.cpu_threshold]
        if not high_cpu_samples:
            return 0.5  # No high CPU periods, neutral efficiency
        
        # Check if we reduced intervals during high CPU
        adaptive_responses = 0
        for i in range(1, len(high_cpu_samples)):
            if high_cpu_samples[i]["interval"] < high_cpu_samples[i-1]["interval"]:
                adaptive_responses += 1
        
        if len(high_cpu_samples) <= 1:
            return 0.5
        
        return adaptive_responses / (len(high_cpu_samples) - 1)


class TriggeredSampler:
    """Sampler that can be triggered by specific events."""
    
    def __init__(self, collector: DataCollector):
        self.collector = collector
        self._triggers = {}
        self._trigger_samples = []
    
    def add_trigger(self, name: str, condition: Callable[[Dict[str, Any]], bool]) -> None:
        """Add a trigger condition."""
        self._triggers[name] = condition
    
    def remove_trigger(self, name: str) -> None:
        """Remove a trigger."""
        self._triggers.pop(name, None)
    
    def check_triggers(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check all triggers and collect samples if conditions are met."""
        triggered_samples = []
        
        for trigger_name, condition in self._triggers.items():
            try:
                if condition(current_metrics):
                    # Trigger condition met, collect detailed sample
                    sample = self._collect_detailed_sample()
                    sample["trigger_name"] = trigger_name
                    sample["trigger_time"] = time.time()
                    triggered_samples.append(sample)
                    self._trigger_samples.append(sample)
            except Exception as e:
                logging.error(f"Error checking trigger {trigger_name}: {e}")
        
        return triggered_samples
    
    def _collect_detailed_sample(self) -> Dict[str, Any]:
        """Collect a detailed sample for trigger events."""
        timestamp = time.time()
        
        return {
            "timestamp": timestamp,
            "cpu": self.collector.collect_cpu_metrics(timestamp),
            "memory": self.collector.collect_memory_metrics(timestamp),
            "threads": self.collector.collect_thread_metrics(timestamp),
            "processes": self.collector.collect_process_metrics(timestamp),
            "stellar": self.collector.collect_stellar_metrics(timestamp),
            "detailed_process": self.collector.collect_detailed_process_metrics(timestamp),
            "gpu": self.collector.collect_gpu_metrics(timestamp),
            "network": self.collector.collect_network_metrics(timestamp),
            "io": self.collector.collect_io_metrics(timestamp),
        }
    
    def get_triggered_samples(self) -> List[Dict[str, Any]]:
        """Get all samples collected by triggers."""
        return self._trigger_samples.copy()
    
    def clear_triggered_samples(self) -> None:
        """Clear all triggered samples."""
        self._trigger_samples.clear()
