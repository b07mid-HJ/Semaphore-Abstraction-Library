import threading
import time
import random
from typing import List
from resource_pool import ResourcePool
from resource_manager import global_resource_manager
from decorators import with_resource

class MockDatabase:
    def __init__(self, name: str):
        self.name = name
        self.data = []
        self.counter = 0
        
    def execute_query(self, query: str, thread_name: str):
        # Simulate database operation
        time.sleep(random.uniform(0.01, 0.03))  # Small delay to simulate work
        
        # Counter increment - Protected by our semaphore
        current = self.counter
        time.sleep(0.01)  # Same delay as uncontrolled version
        self.counter = current + 1
        
        # Data append - Protected by our semaphore
        self.data.append(query)
        print(f"[{thread_name}] Using connection {self.name} - Executing: {query}")
        print(f"[{thread_name}] Counter value: {self.counter}")

# Create a pool of database connections
db_connections = [
    MockDatabase(f"db_conn_{i}") 
    for i in range(1)  # Only one connection to demonstrate thread safety
]

# Create and register the database connection pool
db_pool = ResourcePool(db_connections, max_call=1)  # Only one thread at a time
global_resource_manager.register_pool('database', db_pool)

@with_resource('database', timeout=5.0)
def execute_queries(db_connection: MockDatabase, thread_name: str):
    # Simulate multiple queries from each thread
    for i in range(3):
        query = f"INSERT data from {thread_name} - {i}"
        db_connection.execute_query(query, thread_name)

def main():
    # Create multiple threads all trying to access the database
    threads: List[threading.Thread] = []
    for i in range(10):
        thread_name = f"Thread-{i}"
        t = threading.Thread(target=execute_queries, args=(thread_name,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print("\nFinal database state:")
    total_records = sum(len(conn.data) for conn in db_connections)
    total_counter = sum(conn.counter for conn in db_connections)
    print(f"Total records: {total_records}")
    print(f"Counter value: {total_counter}")
    print(f"Expected counter value: {total_records}")  # Will match because of proper synchronization

if __name__ == "__main__":
    main() 