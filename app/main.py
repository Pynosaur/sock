import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app import __version__
from app.core.socket_handler import (
    listen,
    connect,
    send_message,
    send_file,
    receive_loop,
    interactive_mode,
)
from app.core.network_info import show_network_info, test_port
from app.utils.doc_reader import read_app_doc


def print_help():
    doc = read_app_doc("sock")
    desc = doc.get("description", "Pure Python socket communication tool")

    print(f"sock - {desc}")
    print()
    print("USAGE:")
    print("    sock rec PORT                     Listen and receive messages/files")
    print("    sock sen HOST PORT                Connect and send a message or file")
    print("    sock mult -l PORT                 Full duplex (listen)")
    print("    sock mult HOST PORT               Full duplex (connect)")
    print("    sock info                         Show network information")
    print("    sock test PORT                    Test if port is available")
    print()
    print("OPTIONS:")
    print("    -m, --msg MESSAGE                 Message to send (sen mode)")
    print("    -f, --file FILE                   File to send (sen mode)")
    print("    -d, --save-dir DIR                Directory to save received files")
    print("    -l, --listen                      Listen instead of connect (mult)")
    print("    -h, --help                        Show help")
    print("    -v, --version                     Show version")
    print()
    print("EXAMPLES:")
    print("    sock rec 8080")
    print("    sock sen 192.168.1.10 8080 -m 'hello'")
    print("    sock sen 192.168.1.10 8080 -f notes.txt")
    print("    sock mult -l 8080")
    print("    sock mult 192.168.1.10 8080")
    print("    sock info")
    print("    sock test 8080")


def print_version():
    doc = read_app_doc("sock")
    print(doc.get("version", __version__))


def _parse_port(value):
    try:
        return int(value)
    except ValueError:
        print(f"Error: Invalid port number: {value}", file=sys.stderr)
        sys.exit(1)


def main():
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help", "help"):
        print_help()
        return 0

    if args[0] in ("-v", "--version"):
        print_version()
        return 0

    cmd = args[0]
    rest = args[1:]

    if cmd == "info":
        show_network_info()
        return 0

    if cmd == "test":
        if not rest:
            print("Error: test requires a port number", file=sys.stderr)
            return 1
        test_port(_parse_port(rest[0]))
        return 0

    if cmd == "rec":
        if not rest:
            print("Error: rec requires a port number", file=sys.stderr)
            return 1
        port = _parse_port(rest[0])
        save_dir = None
        i = 1
        while i < len(rest):
            if rest[i] in ("-d", "--save-dir") and i + 1 < len(rest):
                save_dir = rest[i + 1]
                i += 2
            else:
                i += 1
        conn, server = listen(port)
        receive_loop(conn, save_dir=save_dir)
        server.close()
        return 0

    if cmd == "sen":
        if len(rest) < 2:
            print("Error: sen requires HOST PORT", file=sys.stderr)
            return 1
        host = rest[0]
        port = _parse_port(rest[1])
        msg = None
        filepath = None
        i = 2
        while i < len(rest):
            if rest[i] in ("-m", "--msg") and i + 1 < len(rest):
                msg = rest[i + 1]
                i += 2
            elif rest[i] in ("-f", "--file") and i + 1 < len(rest):
                filepath = rest[i + 1]
                i += 2
            else:
                print(f"Unknown option: {rest[i]}", file=sys.stderr)
                return 1
        sock = connect(host, port)
        if filepath:
            send_file(sock, filepath)
        elif msg:
            send_message(sock, msg)
        else:
            print("Error: sen requires -m MESSAGE or -f FILE", file=sys.stderr)
            sock.close()
            return 1
        return 0

    if cmd == "mult":
        listen_mode = False
        host = None
        port = None
        save_dir = None
        i = 0
        while i < len(rest):
            if rest[i] in ("-l", "--listen"):
                listen_mode = True
                i += 1
            elif rest[i] in ("-d", "--save-dir") and i + 1 < len(rest):
                save_dir = rest[i + 1]
                i += 2
            elif port is None and not rest[i].startswith("-"):
                if listen_mode:
                    port = _parse_port(rest[i])
                    i += 1
                elif host is None:
                    host = rest[i]
                    i += 1
                else:
                    port = _parse_port(rest[i])
                    i += 1
            else:
                i += 1

        if listen_mode:
            if port is None:
                print("Error: mult -l requires PORT", file=sys.stderr)
                return 1
            conn, server = listen(port)
            interactive_mode(conn, save_dir=save_dir)
            server.close()
        else:
            if not host or port is None:
                print("Error: mult requires HOST PORT", file=sys.stderr)
                return 1
            sock = connect(host, port)
            interactive_mode(sock, save_dir=save_dir)
        return 0

    print(f"Error: Unknown command: {cmd}", file=sys.stderr)
    print("Use --help for usage information", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

