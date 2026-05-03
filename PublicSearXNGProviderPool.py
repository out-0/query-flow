"""
Public SearXNG Provider Pool

This module provides public SearXNG instances pool with health scoring and dynamic selection.

Dependencies:
    - httpx: For making HTTP requests
    - beautifulsoup4: For parsing HTML content
    - time: For health tracking timestamps

Usage:
    from PublicSearXNGProviderPool import PublicSearXNGPool
    pool = PublicSearXNGPool()
    results = pool.search("python programming")
"""

import httpx
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class InstanceHealth:
    """Health metrics for a SearXNG instance."""
    url: str
    success_count: int = 0
    failure_count: int = 0
    total_latency: float = 0.0
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def avg_latency(self) -> float:
        """Calculate average latency in milliseconds."""
        return self.total_latency / self.success_count if self.success_count > 0 else 0.0
    
    @property
    def health_score(self) -> float:
        """
        Calculate overall health score (0.0 to 1.0).
        Combines success rate (70%) and latency performance (30%).
        """
        success_weight = 0.7
        latency_weight = 0.3
        
        # Normalize latency (lower is better, target < 500ms)
        latency_score = max(0, 1 - (self.avg_latency / 1000))
        
        return (self.success_rate * success_weight) + (latency_score * latency_weight)
    
    def record_success(self, latency: float):
        """Record a successful request."""
        self.success_count += 1
        self.total_latency += latency
        self.last_success = time.time()
    
    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure = time.time()


class SearXNGProvider:
    """Base class for SearXNG providers."""
    
    def __init__(self, url: str):
        self.url = url
    
    def search(self, query: str) -> Tuple[List[Dict], float]:
        """
        Perform search and return results with latency.
        
        Args:
            query: Search query string
            
        Returns:
            Tuple of (results_list, latency_ms)
            
        Raises:
            httpx.HTTPError: If request fails
        """
        start_time = time.time()
        
        try:
            response = httpx.get(
                f"{self.url}/search",
                params={"q": query},
                timeout=10.0,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            for item in soup.select("article.result"):
                a = item.select_one("a[href]")
                if not a:
                    continue
                
                link = a.get("href")
                title = a.get_text(strip=True)
                
                if not link or not link.startswith("http"):
                    continue
                
                results.append({
                    "title": title,
                    "url": link
                })
            
            latency = (time.time() - start_time) * 1000  # Convert to ms
            return results, latency
            
        except httpx.HTTPError as e:
            latency = (time.time() - start_time) * 1000
            raise e


class PublicSearXNGPool:
    """
    Public SearXNG instances pool with health scoring and dynamic selection.
    
    Manages multiple public SearXNG instances, tracks their health,
    and provides intelligent fallback routing.
    """
    
    def __init__(self):
        # Public instances list
        self.public_instances = [
            "https://searxng.org",
            "https://search.brave4u7o2dfr7j.onion",  # Tor instance
            "https://searx.be",
            "https://searx.tiekoetter.com",
            "https://search.snopyta.org"
        ]
        
        # Health tracking for public instances
        self.instance_health: Dict[str, InstanceHealth] = {
            url: InstanceHealth(url=url) 
            for url in self.public_instances
        }
    
    def search(self, query: str) -> List[Dict]:
        """
        Perform search using public instances with health scoring.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results (title, url dictionaries)
        """
        print("🔄 Using public instances pool...")
        
        # Sort instances by health score (best first)
        sorted_instances = sorted(
            self.instance_health.items(),
            key=lambda x: x[1].health_score,
            reverse=True
        )
        
        # Try instances in order of health score
        for url, health in sorted_instances:
            provider = SearXNGProvider(url)
            
            try:
                results, latency = provider.search(query)
                health.record_success(latency)
                print(f"✅ Public instance {url} successful ({latency:.0f}ms, score: {health.health_score:.2f})")
                return results
                
            except httpx.HTTPError as e:
                health.record_failure()
                print(f"❌ Public instance {url} failed: {e}")
                continue
        
        # All instances failed
        print("💥 All public instances failed!")
        return []
    
    def get_health_report(self) -> Dict[str, Dict]:
        """Get health metrics for all instances."""
        return {
            url: {
                "success_rate": health.success_rate,
                "avg_latency": health.avg_latency,
                "health_score": health.health_score,
                "success_count": health.success_count,
                "failure_count": health.failure_count
            }
            for url, health in self.instance_health.items()
        }
    
    def reset_health_stats(self):
        """Reset all health statistics."""
        for health in self.instance_health.values():
            health.success_count = 0
            health.failure_count = 0
            health.total_latency = 0.0
            health.last_success = None
            health.last_failure = None


# Test the public instances pool
if __name__ == "__main__":
    pool = PublicSearXNGPool()
    
    # Test search
    results = pool.search("python programming")
    
    # Display results
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results[:5], 1):
        print(f"{i}. {result['title']}")
    
    # Show health report
    print("\n📊 Health Report:")
    health_report = pool.get_health_report()
    for url, metrics in health_report.items():
        print(f"{url}: score={metrics['health_score']:.2f}, "
              f"success_rate={metrics['success_rate']:.2f}, "
              f"latency={metrics['avg_latency']:.0f}ms")
