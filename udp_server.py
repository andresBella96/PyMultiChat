#!/usr/bin/env python3
import socket

PORT = 5002

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", PORT))

    print(f"UDP Chat Server listening on port {PORT}...")

    while True:
        data, addr = server.recvfrom(1024)
        ip, port = addr
        try:
            text = data.decode().strip()
        except UnicodeDecodeError:
            text = repr(data)
        print(f"[{ip}:{port}] {text}")

if __name__ == "__main__":
    main()
