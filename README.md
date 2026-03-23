# sock

Pure Python socket communication tool for sending and receiving messages and files over TCP.

Reimagines `netcat`/`telnet` for the [Pynosaur](https://pynosaur.org) ecosystem.

## Features

- **Three modes** — `rec` (receive), `sen` (send), `mult` (full duplex)
- **Structured protocol** — length-prefixed JSON headers + binary payload
- **File transfer** — send and receive files with metadata
- **Network utilities** — show IP info, test ports
- **Pure Python** — stdlib only, no dependencies
- **Cross-platform** — Linux, macOS, Windows

## Installation

```bash
pget install sock
```

Or from source:

```bash
git clone https://github.com/pynosaur/sock.git
cd sock
python app/main.py --help
```

## Usage

### Receive (`rec`)

Listen on a port and receive messages or files:

```bash
sock rec 8080
```

Save received files to a directory:

```bash
sock rec 8080 -d ~/Downloads
```

### Send (`sen`)

Send a message:

```bash
sock sen 192.168.1.10 8080 -m "hello"
```

Send a file:

```bash
sock sen 192.168.1.10 8080 -f document.txt
```

### Full Duplex (`mult`)

Both sides can send text and files interactively.

Listen side:

```bash
sock mult -l 8080
```

Connect side:

```bash
sock mult 192.168.1.10 8080
```

Interactive commands inside `mult`:

```
> hello                    (send text)
/file notes.txt            (send a file)
/ping                      (ping remote)
/quit                      (close connection)
```

### Network Utilities

```bash
sock info                  # Show local IP, public IP, gateway
sock test 8080             # Test if port can be bound
```

## Examples

### Local testing

```bash
# Terminal 1
sock rec 9000

# Terminal 2
sock sen localhost 9000 -m "hello from terminal 2"
```

### File transfer over LAN

```bash
# Computer A (192.168.1.10)
sock rec 9000 -d ~/received

# Computer B
sock sen 192.168.1.10 9000 -f report.pdf
```

### Interactive chat

```bash
# Terminal 1
sock mult -l 8080

# Terminal 2
sock mult localhost 8080
```

## Protocol

sock uses a simple binary framing protocol over TCP:

```
[4 bytes: payload length (network byte order)]
[JSON header]\n[binary payload]
```

Packet types:

| Type | Purpose |
|------|---------|
| `msg` | Text message |
| `file` | File transfer (header includes `name` and `size`) |
| `ping` | Ping |
| `pong` | Pong |

## Security

This is an **educational tool** with **no encryption** and **no authentication**.

- Messages are sent in plaintext
- Anyone who can reach the port can connect
- Do not send sensitive data
- Use on trusted networks

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT

