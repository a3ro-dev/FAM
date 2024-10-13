import unittest

def hello_world():
    return "Hello, world!"

class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(hello_world(), "Hello, world!")

if __name__ == '__main__':
    unittest.main()