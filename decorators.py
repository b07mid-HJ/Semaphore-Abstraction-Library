from typing import Optional
from resource_manager import global_resource_manager


def with_resource(pool_name: str, timeout: Optional[float] = None):

    def decorator(func):
        def wrapper(*args, **kwargs):
            pool = global_resource_manager.get_pool(pool_name)
            if pool is None:
                raise ValueError(f"Resource pool '{pool_name}' not found")
                
            resource = pool.acquire(timeout=timeout)
            if resource is None:
                raise TimeoutError(f"Could not acquire resource from pool '{pool_name}'")
                
            try:
                return func(resource, *args, **kwargs)
            finally:
                pool.release(resource)
        return wrapper
    return decorator