import json
import os
import socket
import struct
import sys
import threading


BUFFER_SIZE = 4096
HEADER_FMT = "!I"
HEADER_SIZE = struct.calcsize(HEADER_FMT)


def _send_packet(sock, packet_type, payload=b"", meta=None):
    header = {"type": packet_type}
    if meta:
        header.update(meta)
    header_bytes = json.dumps(header).encode("utf-8")
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    frame = header_bytes + b"\n" + payload
    sock.sendall(struct.pack(HEADER_FMT, len(frame)) + frame)


def _recv_packet(sock):
    raw_len = _recv_exact(sock, HEADER_SIZE)
    if not raw_len:
        return None, None
    length = struct.unpack(HEADER_FMT, raw_len)[0]
    frame = _recv_exact(sock, length)
    if not frame:
        return None, None
    sep = frame.index(b"\n")
    header = json.loads(frame[:sep].decode("utf-8"))
    payload = frame[sep + 1:]
    return header, payload


def _recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            return None
        data += chunk
    return data


def listen(port, host="0.0.0.0"):
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
        print(f"Error: Permission denied on port {port}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def connect(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"Connected to {host}:{port}")
        return sock
    except socket.gaierror:
        print(f"Error: Could not resolve '{host}'", file=sys.stderr)
        sys.exit(1)
    except ConnectionRefusedError:
        print(f"Error: Connection refused at {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"Error: Connection timed out to {host}:{port}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def send_message(sock, message):
    _send_packet(sock, "msg", message)
    print(f"Sent: {message}")
    sock.close()


def send_file(sock, filepath):
    if not os.path.isfile(filepath):
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    filename = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        data = f.read()
    _send_packet(sock, "file", data, {"name": filename, "size": len(data)})
    print(f"Sent file: {filename} ({len(data)} bytes)")
    sock.close()


def receive_loop(sock, save_dir=None):
    try:
        while True:
            header, payload = _recv_packet(sock)
            if header is None:
                print("\nConnection closed.")
                break
            ptype = header.get("type", "")
            if ptype == "msg":
                print(f"< {payload.decode('utf-8')}")
            elif ptype == "file":
                name = header.get("name", "received_file")
                size = header.get("size", len(payload))
                dest_dir = save_dir or "."
                os.makedirs(dest_dir, exist_ok=True)
                dest = os.path.join(dest_dir, name)
                with open(dest, "wb") as f:
                    f.write(payload)
                print(f"< File received: {dest} ({size} bytes)")
            elif ptype == "ping":
                _send_packet(sock, "pong")
            else:
                print(f"< [{ptype}] {payload.decode('utf-8', errors='replace')}")
    except OSError:
        pass
    finally:
        sock.close()


def interactive_mode(sock, save_dir=None):
    running = threading.Event()
    running.set()

    def receiver():
        try:
            while running.is_set():
                header, payload = _recv_packet(sock)
                if header is None:
                    print("\nConnection closed by remote host.")
                    running.clear()
                    break
                ptype = header.get("type", "")
                if ptype == "msg":
                    print(f"\r\033[K< {payload.decode('utf-8')}")
                    print("> ", end="", flush=True)
                elif ptype == "file":
                    name = header.get("name", "received_file")
                    size = header.get("size", len(payload))
                    dest_dir = save_dir or "."
                    os.makedirs(dest_dir, exist_ok=True)
                    dest = os.path.join(dest_dir, name)
                    with open(dest, "wb") as f:
                        f.write(payload)
                    print(f"\r\033[K< File received: {dest} ({size} bytes)")
                    print("> ", end="", flush=True)
                elif ptype == "pong":
                    print("\r\033[K< pong")
                    print("> ", end="", flush=True)
                else:
                    print(f"\r\033[K< [{ptype}] {payload.decode('utf-8', errors='replace')}")
                    print("> ", end="", flush=True)
        except OSError:
            running.clear()

    recv_thread = threading.Thread(target=receiver, daemon=True)
    recv_thread.start()

    print("\nCommands: type text to send, /file PATH, /ping, /quit")
    print("> ", end="", flush=True)

    try:
        while running.is_set():
            try:
                line = input()
            except EOFError:
                break
            if not line:
                print("> ", end="", flush=True)
                continue
            if line == "/quit":
                break
            elif line == "/ping":
                _send_packet(sock, "ping")
                print("> ", end="", flush=True)
            elif line.startswith("/file "):
                path = line[6:].strip()
                if not os.path.isfile(path):
                    print(f"Error: File not found: {path}")
                    print("> ", end="", flush=True)
                    continue
                name = os.path.basename(path)
                with open(path, "rb") as f:
                    data = f.read()
                _send_packet(sock, "file", data, {"name": name, "size": len(data)})
                print(f"Sent file: {name} ({len(data)} bytes)")
                print("> ", end="", flush=True)
            else:
                _send_packet(sock, "msg", line)
                print("> ", end="", flush=True)
    except KeyboardInterrupt:
        print("\nClosing...")
    finally:
        running.clear()
        sock.close()

