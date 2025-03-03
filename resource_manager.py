from typing import Dict, Optional
from resource_pool import ResourcePool
import threading

class ResourceManager:

    def __init__(self):
        self.pools: Dict[str, ResourcePool]={}
        self.pools_lock= threading.RLock()

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