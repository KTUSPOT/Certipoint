"""
Quick test runner for Person 3 module.
"""
import unittest

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(".", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
