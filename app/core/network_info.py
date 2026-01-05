#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-01-05

import socket
import urllib.request
import urllib.error


def get_local_ip():
    """Get the local IP address."""
    try:
        # Create a dummy socket to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_public_ip():
    """Get the public IP address."""
    services = [
        "https://api.ipify.org",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]
    
    for service in services:
        try:
            with urllib.request.urlopen(service, timeout=3) as response:
                return response.read().decode('utf-8').strip()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            continue
    
    return "Unable to determine"


def get_default_gateway():
    """Get the default gateway (router) IP."""
    try:
        # Read from routing table (works on Linux/macOS)
        import subprocess
        if sys.platform.startswith('linux'):
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if len(parts) > 2:
                        return parts[2]
        elif sys.platform == 'darwin':  # macOS
            result = subprocess.run(['netstat', '-nr'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]
    except Exception:
        pass
    return "Unknown"


def show_network_info():
    """Display comprehensive network information."""
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    gateway = get_default_gateway()
    
    print("Network Information:")
    print(f"  Local IP:     {local_ip}")
    print(f"  Public IP:    {public_ip}")
    print(f"  Gateway:      {gateway}")
    print()
    
    if public_ip == "Unable to determine":
        print("WARNING: Could not determine public IP (no internet?)")
    elif local_ip.startswith("192.168.") or local_ip.startswith("10.") or local_ip.startswith("172."):
        print("Status: Behind NAT (home/office network)")
        print()
        print("To accept connections from the internet:")
        print(f"  1. Configure port forwarding on router ({gateway})")
        print(f"  2. Forward external port -> {local_ip}:PORT")
        print(f"  3. Run: sock -l PORT")
        print(f"  4. Share: sock {public_ip} PORT")
    else:
        print(f"Status: Direct internet connection (public IP: {public_ip})")
        print()
        print("You can accept connections directly:")
        print(f"  sock -l PORT")
        print(f"  Share: sock {public_ip} PORT")


def test_port(port):
    """Test if a port is reachable from the internet."""
    print(f"Testing port {port}...")
    print("This tests if the port is open on your public IP.")
    print()
    
    # Try to create a server on the port
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', port))
        test_socket.listen(1)
        test_socket.settimeout(0.1)
        print(f"[OK] Can bind to port {port} locally")
        test_socket.close()
    except PermissionError:
        print(f"[ERROR] Permission denied on port {port}")
        print(f"  Try a port > 1024 or run with elevated privileges")
        return
    except OSError as e:
        print(f"[ERROR] Cannot bind to port {port}: {e}")
        return
    
    print()
    print("Note: This tool cannot test external reachability automatically.")
    print("To test if others can connect:")
    print(f"  1. Run: sock -l {port}")
    print("  2. Have someone try: sock YOUR_PUBLIC_IP {port}")
    print()
    print("Or use online port checker: https://www.yougetsignal.com/tools/open-ports/")


import sys

