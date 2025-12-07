#!/usr/bin/env python3
import socket
import threading
import sys
import os
from datetime import datetime

PORT = 5002

# === ANSI codes (no colorama required) ===
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

# System message colors
COLOR_JOIN   = FG_GREEN + BRIGHT   # user joined
COLOR_LEAVE  = FG_RED   + DIM      # user left
COLOR_SYSTEM = FG_YELLOW + DIM     # notifications / system info

# Palette for other users
COLOR_PALETTE = [
    FG_CYAN,
    FG_MAGENTA,
    FG_YELLOW,
    FG_BLUE,
    FG_WHITE,
]

alias_colors = {}
color_index = 0
lock = threading.Lock()  # synchronize shared structures

# Connected users known by THIS client
connected_users = set()


def get_color_for(alias):
    """Returns a fixed color for each alias (except 'You')."""
    global color_index
    with lock:
        if alias in alias_colors:
            return alias_colors[alias]
        color = COLOR_PALETTE[color_index % len(COLOR_PALETTE)]
        alias_colors[alias] = color
        color_index += 1
        return color


def play_sound():
    """Small notification sound when receiving messages."""
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            print("\a", end="", flush=True)  # ANSI bell
    except Exception:
        pass


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_message(time, alias, text, own=False):
    """Prints formatted chat message."""
    if own:
        msg = f"{DIM}[{time}] {COLOR_ME}You:{RESET} {text}"
        print(msg.rjust(80))
    else:
        color = get_color_for(alias)
        print(f"{DIM}[{time}] {color}{alias}:{RESET} {text}")


def print_system(time, text):
    """Shows system messages like 'X joined the chat', 'X left', etc."""
    if "joined" in text:
        color = COLOR_JOIN
    elif "left" in text:
        color = COLOR_LEAVE
    else:
        color = COLOR_SYSTEM

    print(f"{DIM}[{time}] {color}{text}{RESET}")


def receiver(sock: socket.socket, my_alias: str):
    """Thread that listens for server messages and prints them."""
    global connected_users

    f = sock.makefile("r", encoding="utf-8", newline="\n")

    while True:
        try:
            line = f.readline()
            if not line:
                print("\n[!] Connection closed by server.")
                break

            text = line.rstrip("\n")

            # Expected format: [Alias] message
            if text.startswith("[") and "] " in text:
                end = text.find("] ")
                alias = text[1:end]
                msg = text[end + 2:]
            else:
                alias = "?"
                msg = text

            time = datetime.now().strftime("%H:%M")

            # Special message: server sending user list
            if alias == "System" and msg.startswith("__USERS__ "):
                raw = msg[len("__USERS__ "):].strip()
                if raw:
                    names = [n for n in raw.split(",") if n]
                    with lock:
                        connected_users.update(names)
                continue

            # Ignore my own messages (already printed locally)
            if alias == my_alias:
                continue

            # Add normal users to local list
            if alias not in ("?", "System"):
                with lock:
                    connected_users.add(alias)

            # Join message
            if msg == "__HELLO__":
                print_system(time, f"{alias} joined the chat")
                continue

            # Leave message
            if msg == "__LEAVE__":
                print_system(time, f"{alias} left the chat")
                with lock:
                    if alias in connected_users:
                        connected_users.remove(alias)
                continue

            # Normal chat message
            play_sound()
            print_message(time, alias, msg, own=False)

        except Exception:
            break


def show_help():
    print(COLOR_INFO + "Available commands:" + RESET)
    print("  /clear   - Clear screen")
    print("  /users   - Show connected users")
    print("  /quit    - Exit chat")
    print()


def main():
    global connected_users

    server_ip = input("Server IP: ").strip()
    alias = input("Your alias: ").strip() or "Anon"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, PORT))

    # Send our alias first
    sock.sendall((alias + "\n").encode("utf-8"))

    # Add ourselves to known users
    with lock:
        connected_users.add(alias)

    clear_screen()
    print(COLOR_INFO + "════════ TCP CHAT ════════" + RESET)
    print(COLOR_INFO + f"Alias: {alias}" + RESET)
    print(COLOR_INFO + f"Server: {server_ip}:{PORT}" + RESET)
    print(COLOR_INFO + "Ctrl+C or /quit to exit" + RESET)
    print()
    show_help()

    # Start receiver thread
    thread = threading.Thread(target=receiver, args=(sock, alias), daemon=True)
    thread.start()

    try:
        while True:
            text = input()

            # Commands
            if text.startswith("/"):
                cmd = text.strip().lower()

                print("\033[A\033[2K", end="")  # Clear input line

                if cmd in ("/quit", "/exit"):
                    print("Exiting chat...")
                    break

                elif cmd == "/clear":
                    clear_screen()
                    print(COLOR_INFO + "Screen cleared.\n" + RESET)
                    continue

                elif cmd == "/users":
                    with lock:
                        users = sorted(list(connected_users))
                    print(COLOR_INFO + "Connected users:" + RESET)
                    for u in users:
                        if u == alias:
                            print(f"  - {u} (you)")
                        else:
                            color = get_color_for(u)
                            print(f"  - {color}{u}{RESET}")
                    print()
                    continue

                else:
                    print(COLOR_INFO + "Unknown command." + RESET)
                    show_help()
                    continue

            if not text.strip():
                continue

            print("\033[A\033[2K", end="")  # erase user raw line

            # Normal message
            line = f"{text}\n"
            sock.sendall(line.encode("utf-8"))

            # Local message bubble
            time = datetime.now().strftime("%H:%M")
            print_message(time, "You", text, own=True)

    except KeyboardInterrupt:
        print("\nExiting chat...")

    finally:
        try:
            sock.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
