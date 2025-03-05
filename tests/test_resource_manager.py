import threading
import unittest
from resource_pool import ResourcePool
from resource_manager import ResourceManager

class TestResourceManager(unittest.TestCase):
    
    def setUp(self):
        # Create a fresh manager for each test
        self.manager = ResourceManager()
        
        # Create some sample resource pools
        self.db_resources = ["db_conn_1", "db_conn_2", "db_conn_3"]
        self.file_resources = ["file_1", "file_2"]
        
        self.db_pool = ResourcePool(self.db_resources, max_call=2)
        self.file_pool = ResourcePool(self.file_resources, max_call=1)
    
    def test_register_and_get_pool(self):
        """Test basic registration and retrieval of pools."""
        # Register pools
        self.manager.register_pool("database", self.db_pool)
        self.manager.register_pool("files", self.file_pool)
        
        # Retrieve pools
        retrieved_db_pool = self.manager.get_pool("database")
        retrieved_file_pool = self.manager.get_pool("files")
        
        # Verify correct pools were retrieved
        self.assertEqual(retrieved_db_pool, self.db_pool)
        self.assertEqual(retrieved_file_pool, self.file_pool)
        
        # Test getting a non-existent pool
        self.assertIsNone(self.manager.get_pool("nonexistent"))
    
    def test_unregister_pool(self):
        """Test removing pools from the manager."""
        # Register and then unregister a pool
        self.manager.register_pool("database", self.db_pool)
        self.assertEqual(self.manager.get_pool("database"), self.db_pool)
        
        self.manager.unregister_pool("database")
        self.assertIsNone(self.manager.get_pool("database"))
        
        # Unregistering a non-existent pool should not raise errors
        self.manager.unregister_pool("nonexistent")
    
    def test_thread_safety(self):
        """Test that multiple threads can safely interact with the manager."""
        # Use these lists to track successes/failures from threads
        successes = []
        failures = []
        
        def worker(thread_id):
            try:
                # Register a pool specific to this thread
                thread_resources = [f"resource_{thread_id}_{i}" for i in range(3)]
                thread_pool = ResourcePool(thread_resources, max_call=1)
                pool_name = f"pool_{thread_id}"
                
                # Register it
                self.manager.register_pool(pool_name, thread_pool)
                
                # Retrieve it and verify it's correct
                retrieved_pool = self.manager.get_pool(pool_name)
                if retrieved_pool is thread_pool:
                    successes.append(thread_id)
                else:
                    failures.append(thread_id)
                    
                # Unregister it
                self.manager.unregister_pool(pool_name)
                
                # Verify it's gone
                if self.manager.get_pool(pool_name) is None:
                    successes.append(f"{thread_id}_unregister")
                else:
                    failures.append(f"{thread_id}_unregister")
                    
            except Exception as e:
                failures.append(f"{thread_id}_exception: {str(e)}")
        
        # Start multiple threads that will register/unregister pools
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Verify all operations were successful
        self.assertEqual(len(failures), 0, f"Thread failures: {failures}")
        self.assertEqual(len(successes), 20)  # 10 threads, 2 success points each
    
    def test_integration_with_resource_pool(self):
        """Test that pools registered with the manager work correctly."""
        # Register a pool
        self.manager.register_pool("database", self.db_pool)
        retrieved_pool = self.manager.get_pool("database")
        
        # Use the retrieved pool
        resource = retrieved_pool.acquire()
        self.assertIn(resource, self.db_resources)
        
        # Release the resource
        self.assertTrue(retrieved_pool.release(resource))
        
        # Verify the original pool was affected (they're the same object)
        self.assertIn(resource, self.db_pool.available_resources)

if __name__ == "__main__":
    unittest.main()