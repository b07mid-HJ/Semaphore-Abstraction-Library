from decorators import with_resource
from resource_pool import ResourcePool
from resource_manager import global_resource_manager

# Create a resource manager and pool for testing

class TestResourceDecorator():
    def setUp(self):
        
        
        # Create a pool of mock resources
        test_resources = ['resource1', 'resource2', 'resource3']
        self.test_pool = ResourcePool(test_resources, max_call=2)
        
        # Register the pool
        global_resource_manager.register_pool('test_pool', self.test_pool)

    def test_decorator_basic_functionality(self):
        """Test basic decorator functionality"""
        @with_resource('test_pool')
        def example_function(resource, x, y):
            print(f"Worker function called with resource: {resource}")
            return resource, x + y
        
        # Call the decorated function
        result_resource, sum_value = example_function(10, 20)
        print(f"Result: {result_resource}, {sum_value}")


if __name__ == "__main__":
    test = TestResourceDecorator()
    test.setUp()
    test.test_decorator_basic_functionality()
