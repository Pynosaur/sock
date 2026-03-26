import subprocess
import sys
import socket
import threading
import json
import struct
import time
import unittest


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


class TestSockCLI(unittest.TestCase):

    def test_help(self):
        result = subprocess.run([sys.executable, "app/main.py", "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("sock", result.stdout)
        self.assertIn("rec", result.stdout)
        self.assertIn("sen", result.stdout)
        self.assertIn("mult", result.stdout)

    def test_version(self):
        result = subprocess.run([sys.executable, "app/main.py", "--version"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("0.1.1", result.stdout)

    def test_info(self):
        result = subprocess.run([sys.executable, "app/main.py", "info"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Network Information", result.stdout)

    def test_port_test(self):
        result = subprocess.run([sys.executable, "app/main.py", "test", "9999"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Testing port", result.stdout)


class TestSockProtocol(unittest.TestCase):

    def test_protocol_msg(self):
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
        self.assertEqual(header["type"], "msg")
        self.assertEqual(payload, b"hello")
        conn.close()
        server.close()
        t.join(timeout=2)

    def test_protocol_file(self):
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
        self.assertEqual(header["type"], "file")
        self.assertEqual(header["name"], "test.txt")
        self.assertEqual(header["size"], len(content))
        self.assertEqual(payload, content)
        conn.close()
        server.close()
        t.join(timeout=2)

