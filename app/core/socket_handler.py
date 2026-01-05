#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-01-05

import socket
import sys
import select
import threading


def listen_mode(port, host='0.0.0.0'):
    """Start server and listen for incoming connection."""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        
        print(f"Listening on {host}:{port}")
        print("Waiting for connection...")
        
        conn, addr = server.accept()
        print(f"Connected from {addr[0]}:{addr[1]}")
        
        return conn, server
    except PermissionError:
        print(f"Error: Permission denied. Port {port} may require root/admin.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def connect_mode(host, port):
    """Connect to remote host."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")
        return sock
    except socket.gaierror:
        print(f"Error: Could not resolve hostname '{host}'", file=sys.stderr)
        sys.exit(1)
    except ConnectionRefusedError:
        print(f"Error: Connection refused. Is {host}:{port} listening?", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"Error: Connection timed out to {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def interactive_mode(sock):
    """Interactive bidirectional communication."""
    def receive_messages():
        """Background thread to receive messages."""
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    print("\nConnection closed by remote host.")
                    sock.close()
                    sys.exit(0)
                try:
                    message = data.decode('utf-8')
                    print(f"\r\033[K< {message}", end='', flush=True)
                    print("\n> ", end='', flush=True)
                except UnicodeDecodeError:
                    print(f"\r\033[K< [binary data: {len(data)} bytes]", flush=True)
                    print("> ", end='', flush=True)
        except OSError:
            pass  # Socket closed

    # Start receive thread
    receiver = threading.Thread(target=receive_messages, daemon=True)
    receiver.start()

    # Main send loop
    print("\nType your messages (Ctrl+C or Ctrl+D to exit):")
    print("> ", end='', flush=True)
    
    try:
        while True:
            try:
                message = input()
                if message:
                    sock.sendall((message + '\n').encode('utf-8'))
                    print("> ", end='', flush=True)
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\nClosing connection...")
    finally:
        sock.close()


def send_message(sock, message):
    """Send a single message and close."""
    try:
        sock.sendall((message + '\n').encode('utf-8'))
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Error sending: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        sock.close()


def send_file(sock, filepath):
    """Send a file over the socket."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            sock.sendall(data)
            print(f"Sent file: {filepath} ({len(data)} bytes)")
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        sock.close()

