"""
Load Test Tool - HTTP load/stress testing.
"""

import asyncio
import time
import statistics
from typing import Optional, Callable
import httpx


class LoadTestTool:
    """HTTP load testing tool."""
    
    def __init__(self):
        pass
    
    async def run(
        self,
        url: str,
        requests: int = 100,
        concurrent: int = 10,
        timeout: int = 30,
        method: str = "GET",
        headers: Optional[dict] = None,
        body: Optional[str] = None,
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> dict:
        """
        Run load test against a URL.
        
        Args:
            url: Target URL
            requests: Total number of requests
            concurrent: Number of concurrent workers
            timeout: Request timeout in seconds
            method: HTTP method
            headers: Custom headers
            body: Request body for POST/PUT
            progress_callback: Callback for progress updates
        
        Returns:
            Dict with load test results
        """
        
        # Results storage
        response_times: list[float] = []
        status_codes: dict[int, int] = {}
        errors: list[str] = []
        completed = 0
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent)
        
        async def make_request(request_id: int):
            nonlocal completed
            
            async with semaphore:
                start_time = time.perf_counter()
                
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        if method.upper() == "GET":
                            response = await client.get(url, headers=headers)
                        elif method.upper() == "POST":
                            response = await client.post(url, headers=headers, content=body)
                        elif method.upper() == "PUT":
                            response = await client.put(url, headers=headers, content=body)
                        elif method.upper() == "DELETE":
                            response = await client.delete(url, headers=headers)
                        else:
                            response = await client.request(method, url, headers=headers, content=body)
                        
                        elapsed = (time.perf_counter() - start_time) * 1000  # ms
                        response_times.append(elapsed)
                        
                        code = response.status_code
                        status_codes[code] = status_codes.get(code, 0) + 1
                        
                except httpx.TimeoutException:
                    errors.append(f"Request {request_id}: Timeout")
                except httpx.ConnectError as e:
                    errors.append(f"Request {request_id}: Connection error")
                except Exception as e:
                    errors.append(f"Request {request_id}: {str(e)}")
                
                finally:
                    completed += 1
                    if progress_callback:
                        progress_callback(completed)
        
        # Record start time
        test_start = time.perf_counter()
        
        # Create all request tasks
        tasks = [make_request(i) for i in range(requests)]
        
        # Run all requests
        await asyncio.gather(*tasks)
        
        # Calculate duration
        test_duration = time.perf_counter() - test_start
        
        # Calculate statistics
        return self._calculate_stats(
            response_times=response_times,
            status_codes=status_codes,
            errors=errors,
            total_requests=requests,
            duration=test_duration,
        )
    
    def _calculate_stats(
        self,
        response_times: list[float],
        status_codes: dict[int, int],
        errors: list[str],
        total_requests: int,
        duration: float,
    ) -> dict:
        """Calculate load test statistics."""
        
        successful = len(response_times)
        failed = total_requests - successful
        
        result = {
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_requests * 100) if total_requests > 0 else 0,
            "status_codes": status_codes,
            "errors": errors[:10],  # Limit errors to first 10
            "duration": duration,
            "rps": total_requests / duration if duration > 0 else 0,
        }
        
        if response_times:
            sorted_times = sorted(response_times)
            
            result.update({
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times),
                "stdev_response_time": statistics.stdev(response_times) if len(response_times) > 1 else 0,
                "p95_response_time": self._percentile(sorted_times, 95),
                "p99_response_time": self._percentile(sorted_times, 99),
            })
        else:
            result.update({
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "median_response_time": 0,
                "stdev_response_time": 0,
                "p95_response_time": 0,
                "p99_response_time": 0,
            })
        
        return result
    
    def _percentile(self, sorted_data: list[float], percentile: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0
        
        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        
        if f == c:
            return sorted_data[f]
        
        return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)
