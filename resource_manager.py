from typing import Dict, Optional
from resource_pool import ResourcePool
import threading

class ResourceManager:

    # Class variable to hold the singleton instance
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        # Only initialize once
        if not hasattr(self, 'initialized'):
            self.pools: Dict[str, ResourcePool] = {}
            self.pools_lock = threading.RLock()
            self.initialized = True

    def register_pool(self, name: str, pool: ResourcePool) -> None:
        """Register a resource pool with a name."""
        with self.pools_lock:
            self.pools[name] = pool
            
    def get_pool(self, name: str) -> Optional[ResourcePool]:
        """Get a resource pool by name."""
        with self.pools_lock:
            return self.pools.get(name)
            
    def unregister_pool(self, name: str) -> None:
        """Unregister a resource pool."""
        with self.pools_lock:
            if name in self.pools:
                del self.pools[name] 

# Create a global instance that can be imported
global_resource_manager = ResourceManager()