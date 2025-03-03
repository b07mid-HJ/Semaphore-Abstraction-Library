import threading
from typing import Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')  


class ResourcePool (Generic[T]):
    
    def __init__(self, resources: List[T], max_call: int=1):

        self.resources=resources
        self.available_resources= resources.copy()
        self.semaphore= threading.Semaphore(value= max_call)
        self.resource_lock= threading.RLock()
        self.in_use: Dict[T, threading.Thread]={}

    def acquire (self, timeout : Optional[float]=None) -> Optional[T]:

        if not self.semaphore.acquire(blocking=True, timeout=timeout):
            return None

        with self.resource_lock:
            if not self.available_resources:
                self.semaphore.release()
                return None
            res=self.available_resources.pop(0)
            self.in_use[res]=threading.current_thread()
            return res
    
    def release (self,resource: T) -> bool:

        with self.resource_lock:
            if resource not in self.in_use:
                return False
            del self.in_use[resource]
            self.available_resources.append(resource)
            self.semaphore.release()
            return True
    
    def __enter__(self) -> 'ResourcePool[T]':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        thread = threading.current_thread()
        with self.resource_lock:
            resources_to_release = [r for r, t in self.in_use.items() if t == thread]
            
        for resource in resources_to_release:
            self.release(resource)
    
    
            
     


