import socket
import subprocess
import sys
import urllib.error
import urllib.request


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_public_ip():
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"):
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                return r.read().decode("utf-8").strip()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
            continue
    return "Unable to determine"


def get_default_gateway():
    try:
        if sys.platform.startswith("linux"):
            result = subprocess.run(["ip", "route"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "default" in line:
                    parts = line.split()
                    if len(parts) > 2:
                        return parts[2]
        elif sys.platform == "darwin":
            result = subprocess.run(["netstat", "-nr"], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if "default" in line:
                    parts = line.split()
                    if len(parts) > 1:
                        return parts[1]
    except Exception:
        pass
    return "Unknown"


def show_network_info():
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
        print(f"  3. Run: sock rec PORT")
        print(f"  4. Share: sock sen {public_ip} PORT")
    else:
        print(f"Status: Direct internet connection (public IP: {public_ip})")
        print()
        print("You can accept connections directly:")
        print(f"  sock rec PORT")
        print(f"  Share: sock sen {public_ip} PORT")


def test_port(port):
    print(f"Testing port {port}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("0.0.0.0", port))
        s.listen(1)
        s.settimeout(0.1)
        print(f"[OK] Can bind to port {port} locally")
        s.close()
    except PermissionError:
        print(f"[ERROR] Permission denied on port {port}")
        print("  Try a port > 1024")
        return
    except OSError as e:
        print(f"[ERROR] Cannot bind to port {port}: {e}")
        return

