#!/usr/bin/env python3
import socket
import threading

HOST = "0.0.0.0"
PORT = 5002

# Dictionary: socket -> alias
clients = {}
lock = threading.Lock()


def broadcast(message: str, exclude=None):
    """Send 'message' to all connected clients except 'exclude'."""
    with lock:
        sockets = list(clients.keys())
    for conn in sockets:
        if conn is exclude:
            continue
        try:
            conn.sendall(message.encode("utf-8"))
        except Exception:
            # If sending fails, remove the client safely
            with lock:
                alias = clients.pop(conn, None)
            conn.close()


def handle_client(conn: socket.socket, addr):
    alias = "?"
    try:
        # file-like wrapper for line-by-line reading
        f = conn.makefile("r", encoding="utf-8", newline="\n")

        # First line must be alias
        alias_line = f.readline()
        if not alias_line:
            conn.close()
            return

        alias = alias_line.strip() or "Anon"

        # Register client
        with lock:
            clients[conn] = alias

        ip, port = addr
        print(f"New client connected: {alias} ({ip}:{port})")

        # Send existing users to the new client
        with lock:
            other_aliases = sorted(
                {a for c, a in clients.items() if c is not conn and a != "?"}
            )
        if other_aliases:
            joined_list = ",".join(other_aliases)
            msg_users = f"[System] __USERS__ {joined_list}\n"
            conn.sendall(msg_users.encode("utf-8"))

        # Notify others of join
        broadcast(f"[{alias}] __HELLO__\n", exclude=conn)

        # Main message loop
        for line in f:
            text = line.rstrip("\n")
            if not text:
                continue
            broadcast(f"[{alias}] {text}\n", exclude=conn)

    except Exception:
        pass
    finally:
        # Handle disconnect
        with lock:
            if conn in clients:
                ip, port = addr
                print(f"Client disconnected: {alias} ({ip}:{port})")
                clients.pop(conn, None)

        broadcast(f"[{alias}] __LEAVE__\n", exclude=conn)

        try:
            conn.close()
        except Exception:
            pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print(f"TCP Chat Server running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    main()
