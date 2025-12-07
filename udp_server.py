#!/usr/bin/env python3
import socket

PORT = 5002

clients = set()          # set of addresses (ip, port)
alias_by_addr = {}       # (ip, port) -> alias


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", PORT))

    print(f"UDP chat server listening on port {PORT}")

    while True:
        data, addr = server.recvfrom(1024)

        try:
            text = data.decode("utf-8", errors="replace")
        except Exception:
            text = ""

        # Expected format: [Alias] message
        alias = "?"
        msg = text
        if text.startswith("[") and "] " in text:
            close = text.find("] ")
            alias = text[1:close]
            msg = text[close + 2 :]

        # Register client in the set
        if addr not in clients:
            clients.add(addr)

        # Store alias associated with this address
        alias_by_addr[addr] = alias

        # ---- Join control ----
        if msg == "__HELLO__":
            # Log in server
            ip, port = addr
            print(f"New client connected: {alias} ({ip}:{port})")

            # Notify the others by forwarding the __HELLO__
            for client in clients:
                if client != addr:
                    server.sendto(data, client)

            # Send the NEW client the list of already connected users
            other_aliases = sorted(
                {a for a_addr, a in alias_by_addr.items() if a_addr != addr and a != "?"}
            )
            if other_aliases:
                user_list = ",".join(other_aliases)
                users_message = f"[System] __USERS__ {user_list}"
                server.sendto(users_message.encode("utf-8"), addr)

            continue

        # ---- Leave control ----
        if msg == "__LEAVE__":
            # Log in server
            ip, port = addr
            print(f"Client disconnected: {alias} ({ip}:{port})")

            # Notify the others by forwarding the __LEAVE__
            for client in clients:
                if client != addr:
                    server.sendto(data, client)

            # Clean up records
            if addr in clients:
                clients.remove(addr)
            if addr in alias_by_addr:
                del alias_by_addr[addr]

            continue

        # ---- Normal message: forward to everyone except sender ----
        for client in clients:
            if client != addr:
                server.sendto(data, client)


if __name__ == "__main__":
    main()
