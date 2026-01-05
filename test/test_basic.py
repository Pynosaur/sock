#!/usr/bin/env python3
"""Basic smoke tests for sock"""

import subprocess
import time
import sys

def test_help():
    """Test --help flag"""
    result = subprocess.run([sys.executable, 'app/main.py', '--help'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'sock -' in result.stdout
    print("[PASS] --help works")

def test_version():
    """Test --version flag"""
    result = subprocess.run([sys.executable, 'app/main.py', '--version'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert '0.1.0' in result.stdout
    print("[PASS] --version works")

def test_info():
    """Test --info flag"""
    result = subprocess.run([sys.executable, 'app/main.py', '--info'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Network Information' in result.stdout
    print("[PASS] --info works")

def test_port_test():
    """Test --test flag"""
    result = subprocess.run([sys.executable, 'app/main.py', '--test', '9999'], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert 'Testing port' in result.stdout
    print("[PASS] --test works")

if __name__ == '__main__':
    print("Running basic tests...")
    test_help()
    test_version()
    test_info()
    test_port_test()
    print("\nAll tests passed!")

