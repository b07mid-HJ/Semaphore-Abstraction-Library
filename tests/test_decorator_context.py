import threading
import time
import unittest
from unittest.mock import Mock

from decorators import with_resource
from resource_manager import global_resource_manager
from resource_pool import ResourcePool


class TestResourceDecorator(unittest.TestCase):
    def setUp(self):
        # Create a resource manager and pool for testing
        
        # Create a pool of mock resources
        test_resources = ['resource1', 'resource2', 'resource33']
        self.test_pool = ResourcePool(test_resources, max_call=2)
        
        # Register the pool
        global_resource_manager.register_pool('test_pool', self.test_pool)
    
    def test_decorator_basic_functionality(self):
        """Test basic decorator functionality"""
        @with_resource('test_pool')
        def example_function(resource, x, y):
            return resource, x + y
        
        # Call the decorated function
        result_resource, sum_value = example_function(10, 20)
        
        # Verify the function works and a resource was used
        self.assertIn(result_resource, ['resource1', 'resource2', 'resource33'])
        self.assertEqual(sum_value, 30)
    
    def test_decorator_concurrent_access(self):
        """Test concurrent access with decorator"""
        # Track resources used by threads
        used_resources = []
        
        @with_resource('test_pool')
        def worker_function(resource):
            print(f"Worker function called with resource: {resource}")
            used_resources.append(resource)
            time.sleep(0.1)  # Simulate some work
        
        # Create and start multiple threads
        threads = []
        for _ in range(6):  # More threads than available resources
            t = threading.Thread(target=worker_function)
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify unique resources were used
        self.assertEqual(len(set(used_resources)), 3)
        self.assertEqual(len(used_resources), 6)
    
    def test_decorator_timeout(self):
        """Test timeout functionality between concurrent threads"""
        @with_resource('test_pool', timeout=0.1)
        def slow_function(resource):
            time.sleep(0.5)  # Hold the resource for a while
            return resource

        # Start first thread that will hold resources
        thread1 = threading.Thread(target=slow_function)
        thread2 = threading.Thread(target=slow_function)
        thread1.start()
        thread2.start()

        # Give thread1 time to acquire resources
        time.sleep(0.1)
        
        # Second thread should timeout waiting for resources
        with self.assertRaises(TimeoutError):
            slow_function()

        thread1.join()
        thread2.join()

if __name__ == '__main__':
    unittest.main()