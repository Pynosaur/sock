#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2026-01-05

import sys
from pathlib import Path

# Allow running both as module and as script
if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app import __version__
from app.core.socket_handler import (
    listen_mode,
    connect_mode,
    interactive_mode,
    send_message,
    send_file,
)
from app.core.network_info import show_network_info, test_port
from app.utils.doc_reader import read_app_doc


def print_help():
    """Print help message."""
    doc = read_app_doc('sock')
    
    desc = doc.get('description', 'Simple socket communication tool')
    
    print(f"sock - {desc}")
    print("\nUSAGE:")
    print("    sock -l PORT                  Listen on port (server mode)")
    print("    sock HOST PORT                Connect to host:port (client mode)")
    print("    sock --info                   Show network information")
    print("    sock --test PORT              Test if port is accessible")
    print("    sock --help                   Show this help")
    print("    sock --version                Show version")
    print("\nOPTIONS:")
    print("    -l, --listen PORT             Start server and listen for connections")
    print("    -s, --send MESSAGE            Send message and exit")
    print("    -f, --file FILE               Send file contents")
    print("    --info                        Display network information")
    print("    --test PORT                   Test port accessibility")
    print("    -h, --help                    Show help message")
    print("    -v, --version                 Show version")
    print("\nEXAMPLES:")
    print("    # Server mode")
    print("    sock -l 8080")
    print()
    print("    # Client mode")
    print("    sock localhost 8080")
    print("    sock 192.168.1.10 8080")
    print()
    print("    # Send message and exit")
    print("    sock localhost 8080 -s \"Hello!\"")
    print()
    print("    # Send file")
    print("    sock localhost 8080 -f document.txt")
    print()
    print("    # Network utilities")
    print("    sock --info")
    print("    sock --test 8080")


def print_version():
    """Print version."""
    doc = read_app_doc('sock')
    print(doc.get('version', __version__))


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print_help()
        return 0

    if args[0] in ("-v", "--version"):
        print_version()
        return 0

    if args[0] == "--info":
        show_network_info()
        return 0

    if args[0] == "--test":
        if len(args) < 2:
            print("Error: --test requires a port number", file=sys.stderr)
            return 1
        try:
            port = int(args[1])
            test_port(port)
            return 0
        except ValueError:
            print(f"Error: Invalid port number: {args[1]}", file=sys.stderr)
            return 1

    # Listen mode
    if args[0] in ("-l", "--listen"):
        if len(args) < 2:
            print("Error: -l requires a port number", file=sys.stderr)
            return 1
        try:
            port = int(args[1])
            conn, server = listen_mode(port)
            interactive_mode(conn)
            server.close()
            return 0
        except ValueError:
            print(f"Error: Invalid port number: {args[1]}", file=sys.stderr)
            return 1

    # Connect mode
    if len(args) >= 2:
        host = args[0]
        try:
            port = int(args[1])
        except ValueError:
            print(f"Error: Invalid port number: {args[1]}", file=sys.stderr)
            return 1

        # Check for additional options
        send_msg = None
        send_file_path = None
        
        i = 2
        while i < len(args):
            if args[i] in ("-s", "--send") and i + 1 < len(args):
                send_msg = args[i + 1]
                i += 2
            elif args[i] in ("-f", "--file") and i + 1 < len(args):
                send_file_path = args[i + 1]
                i += 2
            else:
                print(f"Unknown option: {args[i]}", file=sys.stderr)
                return 1

        sock = connect_mode(host, port)

        if send_msg:
            send_message(sock, send_msg)
        elif send_file_path:
            send_file(sock, send_file_path)
        else:
            interactive_mode(sock)
        
        return 0

    print("Error: Invalid arguments. Use --help for usage information.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

