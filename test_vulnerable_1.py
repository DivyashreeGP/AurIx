#!/usr/bin/env python3
"""
Test file 1: Pickle Deserialization
Paste this code and trigger analysis (save file or Ctrl+Shift+A)
Then paste code from test_vulnerable_2.py and analyze again
UI should show different results each time
"""

import pickle
import socket

def deserialize_data(data):
    """VULNERABLE: Using pickle to deserialize untrusted data"""
    obj = pickle.loads(data)
    return obj

if __name__ == "__main__":
    malicious_data = b"some_data"
    obj = deserialize_data(malicious_data)
    print(f"Deserialized: {obj}")
