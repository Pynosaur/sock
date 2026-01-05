#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-01-05

import os
import sys
import re


def read_app_doc(app_name):
    """Read and parse the application documentation YAML file."""
    # Try to find the doc file
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'doc', f'{app_name}.yaml'),
        os.path.join(os.path.dirname(sys.executable), '..', 'doc', f'{app_name}.yaml'),
        f'/usr/local/share/{app_name}/doc/{app_name}.yaml',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    # Simple YAML parser for our use case
                    doc = {}
                    for line in content.split('\n'):
                        if ':' in line and not line.strip().startswith('-'):
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key.upper() == key:  # Uppercase keys
                                doc[key.lower()] = value
                    return doc
            except Exception:
                pass
    
    # Return minimal default
    return {
        'name': app_name,
        'version': '0.1.0',
        'description': 'Socket communication tool',
    }

