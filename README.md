![PyMultiChat banner](docs/banner_pymultichat.png)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-learning%20project-informational)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20windows%20%7C%20macos-lightgrey)

🌐 **Available languages:** [English](README.md) • [Español](README_ES.md)

---

PyMultiChat is a distributed chat system written in Python, featuring **two independent implementations**:

1. **UDP Chat** — connectionless, fast datagram messaging  
2. **TCP Chat (Multithreaded)** — persistent socket communication per client

It is designed as a learning project for **network programming, sockets, concurrency and terminal UI** in Python, and also as a clean portfolio example.

---

## 🧠 Key design ideas

### 1. Lightweight custom protocol

Both TCP and UDP versions share a simple but powerful message format:

```text
[Alias] message
```

On top of that, a few internal control messages are used:

- `__HELLO__` → a user joined
- `__LEAVE__` → a user left
- `__USERS__` → server sends the list of already connected users

Thanks to this mini‑protocol:

- the client can easily parse who sent each message
- system events (join/leave) are clearly separated from normal chat text
- it’s easy to extend the protocol in the future (rooms, authentication, etc.)

### 2. UDP version – stateless broadcast

**Server (UDP)**

- Uses `socket.AF_INET`, `SOCK_DGRAM` (UDP)
- Keeps a `set` of client addresses and a mapping `(ip, port) -> alias`
- When a client sends `__HELLO__`, the server:
  - logs the new connection
  - broadcasts the `__HELLO__` to everyone else
  - sends back `__USERS__` only to the new client

**Client (UDP)**

- Runs a **receiver thread** so the UI stays responsive while listening
- Uses ANSI escape codes (no external libs) for:
  - per-user colors
  - “system” messages (joins, leaves, info)
- Provides simple commands:
  - `/clear` – clear screen
  - `/users` – show known connected users
  - `/quit` – exit gracefully (sends `__LEAVE__`)

This version is perfect to understand **connectionless** communication and broadcast‑like messaging.

### 3. TCP version – multithreaded server

**Server (TCP)**

- Uses `socket.AF_INET`, `SOCK_STREAM` (TCP)
- For each new connection, spawns a `threading.Thread` running `manejar_cliente`
- Reads from the socket line by line using `makefile("r")`
- First line received from each client is its **alias**
- Maintains a dictionary `socket -> alias`
- Broadcasts to all clients except the sender
- Cleans up sockets and informs others with `__LEAVE__` on disconnect

**Client (TCP)**

- Sends alias as the first line after connecting
- Starts a **receiver thread** that:
  - reads lines from the server
  - parses `[Alias] message`
  - reacts to internal events (`__HELLO__`, `__LEAVE__`, `__USERS__`)
  - plays a sound and prints colored messages
- Main thread handles user input, local “bubble” printing and commands

This version shows a classic **multithreaded TCP chat architecture** in a compact codebase.

---

## 🖼 Visuals

### Client UI (terminal)

Below is a screenshot of the colored client interface:

![Client UI screenshot](docs/captura_chat.png)

---

## ⏳ Requirements

- **Python 3.8+**
- No external dependencies
- Works on Windows / Linux / macOS

Optional on Windows (for sound):

```powershell
pip install winsound   # only if you want to replace the default beep
```

*(On most systems the default implementation already uses the ANSI bell `\a`.)*

---

## ▶ Run instructions

File names below assume something like:

```text
udp_server.py
udp_client.py
tcp_server.py
tcp_client.py
```

### UDP mode

**Server:**

```bash
python3 udp_server.py
```

**Client:**

```bash
python3 udp_client.py
```

The client will ask:

```text
Server IP:
Alias:
```

---

### TCP mode

**Server:**

```bash
python3 tcp_server.py
```

**Client:**

```bash
python3 tcp_client.py
```

Again, the client will request:

```text
Server IP:
Your alias:
```

---

## 💬 Client commands

| Command   | Description                               |
|----------|-------------------------------------------|
| `/clear` | Clear screen                              |
| `/users` | Show connected users (known locally)      |
| `/quit`  | Exit chat (TCP closes, UDP sends LEAVE)   |

---

## 🔥 Ideas for future improvements

| Feature                | Value                                           |
|------------------------|-------------------------------------------------|
| TLS/SSL encryption     | Real secure messaging over public networks     |
| GUI (Tkinter / Qt)     | User‑friendly visual interface                 |
| Login/auth system      | Identity and permissions                       |
| Rooms / channels       | Scalable, multi‑channel architecture          |
| Message history        | Persistence and debug/logging                  |
| Config file / CLI opts | Flexible ports, host, colors, sound, etc.      |

---

## 📁 Repository structure (suggested)

```text
.
├── udp_server.py
├── udp_client.py
├── tcp_server.py
├── tcp_client.py
├── README.md
├── README_ES.md
└── docs/
    └── banner_pymultichat.png   # optional project banner
    └── captura_cliente.png      # client UI screenshot
```

---

## 🌍 Languages

- 🇬🇧 **English** — this file (`README.md`)  
- 🇪🇸 **Español** — [README_ES.md](README_ES.md)

---

## 📜 License

This project is released under the **MIT License** (recommended for learning/portfolio projects).

---

⭐ If you find this project useful or educational, consider giving it a star on GitHub!
