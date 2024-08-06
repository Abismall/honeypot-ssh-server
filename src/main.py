import os
from server import Server
import socket
import threading
from utils import HOST, LOG_DIR, PORT, handle_connection


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, int(PORT)))
    server_socket.listen(100)

    while True:
        try:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_connection, args=(Server(), client_socket, addr)).start()
        except Exception:
            continue

if __name__ == "__main__":
    main()
