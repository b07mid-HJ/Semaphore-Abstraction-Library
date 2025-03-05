import threading
import time
import unittest
from resource_pool import ResourcePool  # Import your implementation

class TestResourcePool(unittest.TestCase):
    
    def test_basic_acquire_release(self):
        """Test simple acquire and release functionality."""
        # Create a pool of string resources
        resources = ["resource1", "resource2", "resource3"]
        pool = ResourcePool(resources, max_call=2)
        
        # Acquire a resource
        r1 = pool.acquire()
        self.assertIn(r1, resources)
        self.assertEqual(len(pool.available_resources), 2)
        
        # Acquire another resource
        r2 = pool.acquire()
        self.assertIn(r2, resources)
        self.assertNotEqual(r1, r2)
        self.assertEqual(len(pool.available_resources), 1)
        
        # Release a resource
        result = pool.release(r1)
        self.assertTrue(result)
        self.assertEqual(len(pool.available_resources), 2)
    
    def test_context_manager(self):
        """Test using the ResourcePool as a context manager."""
        resources = ["resource1", "resource2"]
        pool = ResourcePool(resources, max_call=1)
        
        with pool as p:
            r = p.acquire()
            self.assertIn(r, resources)
            self.assertEqual(len(p.available_resources), 1)
            
        # After exiting the context, resource should be released
        self.assertEqual(len(pool.available_resources), 2)
    
    def test_concurrent_access(self):
        """Test that concurrent access is properly limited."""
        resources = ["r1", "r2", "r3", "r4", "r5"]
        pool = ResourcePool(resources, max_call=2)
        
        acquired_resources = []
        release_times = []
        
        def worker(thread_id):
            resource = pool.acquire()
            acquired_resources.append(resource)
            # Hold the resource for a bit
            time.sleep(0.2)
            release_times.append(time.time())
            pool.release(resource)
        
        # Start 5 threads that will compete for resources
        threads = []
        start_time = time.time()
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify that resources were properly managed
        self.assertEqual(len(acquired_resources), 5)
        self.assertEqual(len(release_times), 5)
        
        # Check that we had at most 2 concurrent acquisitions
        # The release times should show at least 3 distinct batches
        # (0.2s per batch with 2 concurrent threads = 0.6s total minimum)
        time_groups = []
        for t in sorted(release_times):
            if not time_groups or t - time_groups[-1][0] > 0.15:
                time_groups.append([t])
            else:
                time_groups[-1].append(t)
        
        self.assertGreaterEqual(len(time_groups), 3)
        for group in time_groups:
            self.assertLessEqual(len(group), 2)

if __name__ == "__main__":
    unittest.main()