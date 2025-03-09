import threading
import time
import random
from typing import List

class MockDatabase:
    def __init__(self):
        self.data = []
        self.counter = 0  # A shared counter to demonstrate race conditions
        
    def execute_query(self, query: str, thread_name: str):
        # Simulate database operation
        time.sleep(random.uniform(0.01, 0.03))  # Small delay to simulate work
        
        # Unsafe counter increment - demonstrates race condition
        current = self.counter
        time.sleep(0.01)  # Deliberately add delay to make race condition more likely
        self.counter = current + 1
        
        # Unsafe data append
        self.data.append(query)
        print(f"[{thread_name}] Executing: {query}")
        print(f"[{thread_name}] Counter value: {self.counter}")

def worker(db: MockDatabase, thread_name: str):
    # Simulate multiple queries from each thread
    for i in range(3):
        query = f"INSERT data from {thread_name} - {i}"
        db.execute_query(query, thread_name)

def main():
    # Create a single database instance
    db = MockDatabase()
    
    # Create multiple threads all trying to access the database
    threads: List[threading.Thread] = []
    for i in range(10):
        thread_name = f"Thread-{i}"
        t = threading.Thread(target=worker, args=(db, thread_name))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    print("\nFinal database state:")
    print(f"Total records: {len(db.data)}")
    print(f"Counter value: {db.counter}")
    print(f"Expected counter value: {len(db.data)}")  # Should match counter but won't due to race condition

if __name__ == "__main__":
    main() 