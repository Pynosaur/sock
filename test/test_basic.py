import subprocess
import sys
import socket
import threading
import json
import struct
import time


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
    raw_len = b""
    while len(raw_len) < HEADER_SIZE:
        chunk = sock.recv(HEADER_SIZE - len(raw_len))
        if not chunk:
            return None, None
        raw_len += chunk
    length = struct.unpack(HEADER_FMT, raw_len)[0]
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return None, None
        data += chunk
    sep = data.index(b"\n")
    header = json.loads(data[:sep].decode("utf-8"))
    payload = data[sep + 1:]
    return header, payload


def test_help():
    result = subprocess.run([sys.executable, "app/main.py", "--help"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "sock" in result.stdout
    assert "rec" in result.stdout
    assert "sen" in result.stdout
    assert "mult" in result.stdout
    print("[PASS] --help works")


def test_version():
    result = subprocess.run([sys.executable, "app/main.py", "--version"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
    print("[PASS] --version works")


def test_info():
    result = subprocess.run([sys.executable, "app/main.py", "info"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "Network Information" in result.stdout
    print("[PASS] info works")


def test_port_test():
    result = subprocess.run([sys.executable, "app/main.py", "test", "9999"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "Testing port" in result.stdout
    print("[PASS] test works")


def test_protocol_msg():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    port = server.getsockname()[1]
    server.listen(1)

    def sender():
        time.sleep(0.2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", port))
        _send_packet(s, "msg", "hello")
        s.close()

    t = threading.Thread(target=sender, daemon=True)
    t.start()

    conn, _ = server.accept()
    header, payload = _recv_packet(conn)
    assert header["type"] == "msg"
    assert payload == b"hello"
    conn.close()
    server.close()
    t.join(timeout=2)
    print("[PASS] protocol msg packet works")


def test_protocol_file():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    port = server.getsockname()[1]
    server.listen(1)

    content = b"file content here"

    def sender():
        time.sleep(0.2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", port))
        _send_packet(s, "file", content, {"name": "test.txt", "size": len(content)})
        s.close()

    t = threading.Thread(target=sender, daemon=True)
    t.start()

    conn, _ = server.accept()
    header, payload = _recv_packet(conn)
    assert header["type"] == "file"
    assert header["name"] == "test.txt"
    assert header["size"] == len(content)
    assert payload == content
    conn.close()
    server.close()
    t.join(timeout=2)
    print("[PASS] protocol file packet works")


if __name__ == "__main__":
    print("Running tests...")
    test_help()
    test_version()
    test_info()
    test_port_test()
    test_protocol_msg()
    test_protocol_file()
    print("\nAll tests passed!")

