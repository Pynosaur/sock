# sock

Simple socket communication tool for direct TCP connections.

Version: 0.1.0

## Overview

`sock` is an educational networking tool that enables direct socket communication between two endpoints. Perfect for learning network programming, testing connections, or simple peer-to-peer messaging.

## Features

- **Interactive chat mode** - bidirectional messaging
- **One-shot mode** - send message and exit
- **File transfer** - send files over sockets
- **Network utilities** - show IP info, test ports
- **Pure Python** - stdlib only, no dependencies
- **Cross-platform** - works on Linux, macOS, Windows

## Installation

```bash
# Via pget
pget install sock

# From source
git clone https://github.com/pynosaur/sock.git
cd sock
python app/main.py
```

## Usage

### Server Mode (Listen)

```bash
# Listen on port 8080
sock -l 8080
```

### Client Mode (Connect)

```bash
# Connect to localhost
sock localhost 8080

# Connect to LAN host
sock 192.168.1.10 8080

# Connect over internet (requires port forwarding on server side)
sock your-public-ip.com 8080
```

### Interactive Chat

```bash
# Terminal 1 (Server)
$ sock -l 8080
Listening on 0.0.0.0:8080
Waiting for connection...
Connected from 127.0.0.1:54321

Type your messages (Ctrl+C or Ctrl+D to exit):
> Hello from server!
< Hi from client!
> How are you?

# Terminal 2 (Client)
$ sock localhost 8080
Connected to localhost:8080

Type your messages (Ctrl+C or Ctrl+D to exit):
< Hello from server!
> Hi from client!
< How are you?
> Great!
```

### Send Message and Exit

```bash
sock localhost 8080 -s "Hello, World!"
```

### Send File

```bash
sock localhost 8080 -f document.txt
```

### Network Utilities

```bash
# Show network information
$ sock --info
Network Information:
  Local IP:     192.168.1.100
  Public IP:    85.240.12.34
  Gateway:      192.168.1.1

Status: Behind NAT (home/office network)

To accept connections from the internet:
  1. Configure port forwarding on router (192.168.1.1)
  2. Forward external port → 192.168.1.100:PORT
  3. Run: sock -l PORT
  4. Share: sock 85.240.12.34 PORT

# Test port availability
$ sock --test 8080
Testing port 8080...
[OK] Can bind to port 8080 locally
```

## Use Cases

### Local Testing
- Same machine communication
- Testing applications
- Learning socket programming

### LAN Communication
- Chat between computers on same network
- File transfers within office/home
- Network debugging

### Internet Communication
- Requires port forwarding on one side
- Direct peer-to-peer messaging
- Simple remote access

## Network Requirements

### Same Machine (Localhost)
**Always works** - No configuration needed

```bash
# Terminal 1
sock -l 8080

# Terminal 2  
sock localhost 8080
```

### Same Network (LAN)
**Works easily** - Both devices on same WiFi/network

```bash
# Computer A (192.168.1.10)
sock -l 8080

# Computer B (same network)
sock 192.168.1.10 8080
```

### Different Networks (Internet)
**Requires setup** - Listener needs port forwarding

**Steps:**
1. Find public IP: `sock --info`
2. Configure router port forwarding
3. Allow firewall on listener
4. Run listener: `sock -l 8080`
5. Client connects: `sock PUBLIC_IP 8080`

## Security Notes

**Educational Tool - No Encryption**
- Messages sent in plaintext
- No authentication
- Anyone who can reach your port can connect

**Use responsibly:**
- Don't send sensitive data
- Use on trusted networks
- Close when not in use
- Be aware of firewall implications

## Examples

### File Transfer

```bash
# Receiver
sock -l 9000 > received_file.txt

# Sender
sock 192.168.1.10 9000 -f myfile.txt
```

### Simple Chat Server

```bash
# Host
sock -l 8080

# Multiple clients can connect one at a time
sock HOST 8080
```

### Quick Network Test

```bash
# Check if remote host port is open
sock remote-host.com 80 -s "test"
```

## Troubleshooting

### "Permission denied" on port
- Use ports > 1024 (non-privileged)
- Or run with sudo/admin (not recommended)

### "Connection refused"
- Server not running
- Wrong IP or port
- Firewall blocking

### "Connection timed out"
- Host unreachable
- Network issue
- Port forwarding not configured

### Can't connect from internet
- Check port forwarding configuration
- Verify firewall allows connections
- Confirm public IP with `sock --info`
- Test with online port checker

## Technical Details

- **Protocol**: TCP
- **Default binding**: 0.0.0.0 (all interfaces)
- **Buffer size**: 4096 bytes
- **Threading**: Receive runs in background thread
- **Encoding**: UTF-8 for text, binary for files

## License

MIT License - See LICENSE file

## Author

@spacemany2k38

## Contributing

Part of the Pynosaur ecosystem - simple, focused CLI tools.

