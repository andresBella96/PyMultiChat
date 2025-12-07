#!/usr/bin/env python3
import socket
import threading
import sys
import os
from datetime import datetime

PORT = 5002

# === ANSI CODES (no colorama needed) ===
RESET  = "\033[0m"
BRIGHT = "\033[1m"
DIM    = "\033[2m"

FG_GREEN   = "\033[32m"
FG_MAGENTA = "\033[35m"
FG_RED     = "\033[31m"
FG_YELLOW  = "\033[33m"
FG_CYAN    = "\033[36m"
FG_BLUE    = "\033[34m"
FG_WHITE   = "\033[37m"

# Chat colors
COLOR_ME   = FG_GREEN
COLOR_INFO = FG_MAGENTA

# System colors
COLOR_JOIN   = FG_GREEN + BRIGHT
COLOR_LEAVE  = FG_RED   + DIM
COLOR_SYSTEM = FG_YELLOW + DIM

# Color palette for unique users
COLOR_PALETTE = [FG_CYAN, FG_MAGENTA, FG_YELLOW, FG_BLUE, FG_WHITE]

alias_colors = {}
color_index = 0
lock = threading.Lock()

connected_users = set()  # users known by this client


def get_color_for(alias):
    """Return fixed color per alias."""
    global color_index
    with lock:
        if alias in alias_colors:
            return alias_colors[alias]
        color = COLOR_PALETTE[color_index % len(COLOR_PALETTE)]
        alias_colors[alias] = color
        color_index += 1
        return color


def play_sound():
    """Terminal bell sound"""
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            print("\a", end="", flush=True)
    except:
        pass


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_message(time, alias, text, own=False):
    if own:
        formatted = f"{DIM}[{time}] {COLOR_ME}You:{RESET} {text}"
        print(formatted.rjust(80))
    else:
        color = get_color_for(alias)
        print(f"{DIM}[{time}] {color}{alias}:{RESET} {text}")


def print_system(time, text):
    if "joined" in text:
        color = COLOR_JOIN
    elif "left" in text:
        color = COLOR_LEAVE
    else:
        color = COLOR_SYSTEM

    print(f"{DIM}[{time}] {color}{text}{RESET}")


def receiver(sock, my_alias):
    global connected_users

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            text = data.decode("utf-8", errors="replace")

            # Expected format: [Alias] message
            if text.startswith("[") and "] " in text:
                end = text.find("] ")
                alias = text[1:end]
                msg = text[end + 2 :]
            else:
                alias = "?"
                msg = text

            time = datetime.now().strftime("%H:%M")

            # Special user list message
            if alias == "System" and msg.startswith("__USERS__ "):
                raw = msg[len("__USERS__ "):].strip()
                if raw:
                    names = [n for n in raw.split(",") if n]
                    with lock:
                        connected_users.update(names)
                continue

            # skip own echoed messages
            if alias == my_alias:
                continue

            # Add normal users to list
            if alias not in ("?", "System"):
                with lock:
                    connected_users.add(alias)

            # System events
            if msg == "__HELLO__":
                print_system(time, f"{alias} joined the chat")
                continue

            if msg == "__LEAVE__":
                print_system(time, f"{alias} left the chat")
                with lock:
                    if alias in connected_users:
                        connected_users.remove(alias)
                continue

            # Normal message
            play_sound()
            print_message(time, alias, msg)

        except:
            pass


def show_help():
    print(COLOR_INFO + "Available commands:" + RESET)
    print("  /clear  - Clear screen")
    print("  /users  - Show connected users")
    print("  /quit   - Leave chat\n")


def send_leave(sock, server_ip, alias):
    try:
        msg = f"[{alias}] __LEAVE__"
        sock.sendto(msg.encode("utf-8"), (server_ip, PORT))
    except:
        pass


def main():
    global connected_users

    server_ip = input("Server IP: ").strip()
    alias = input("Your alias: ").strip() or "Anon"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))  # auto local port

    # Register client
    hello = f"[{alias}] __HELLO__"
    sock.sendto(hello.encode("utf-8"), (server_ip, PORT))

    with lock:
        connected_users.add(alias)

    clear_screen()
    print(COLOR_INFO + "════════ UDP CHAT ════════" + RESET)
    print(COLOR_INFO + f"Alias: {alias}" + RESET)
    print(COLOR_INFO + f"Server: {server_ip}:{PORT}" + RESET)
    print(COLOR_INFO + "Ctrl+C or /quit to exit\n" + RESET)
    show_help()

    threading.Thread(target=receiver, args=(sock, alias), daemon=True).start()

    while True:
        try:
            text = input()

            if text.startswith("/"):
                cmd = text.strip().lower()
                print("\033[A\033[2K", end="")

                if cmd in ("/quit", "/exit"):
                    send_leave(sock, server_ip, alias)
                    print("Leaving chat...")
                    break

                elif cmd == "/clear":
                    clear_screen()
                    print("Screen cleared\n")
                    continue

                elif cmd == "/users":
                    with lock:
                        users = sorted(list(connected_users))
                    print("Connected users:")
                    for u in users:
                        print("  -", u, "(you)" if u == alias else "")
                    print()
                    continue

                else:
                    print("Unknown command\n")
                    show_help()
                    continue

            if not text.strip():
                continue

            print("\033[A\033[2K", end="")  # erase input
            msg = f"[{alias}] {text}"
            sock.sendto(msg.encode("utf-8"), (server_ip, PORT))

            now = datetime.now().strftime("%H:%M")
            print_message(now, "You", text, own=True)

        except KeyboardInterrupt:
            send_leave(sock, server_ip, alias)
            print("\nLeaving chat...")
            break

    sock.close()


if __name__ == "__main__":
    main()
