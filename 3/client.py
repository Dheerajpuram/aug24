import socket, ssl, threading
import base64, hashlib
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 12345

# --- derive Fernet key from shared passphrase ---
def derive_key(passphrase):
    return base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())

def receive_messages(conn, cipher, name):
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
            msg = cipher.decrypt(data).decode()
            print(f"\n{msg}\n> ", end="")
        except Exception as e:
            pass

def main():
    name = input("Your display name: ")
    passphrase = input("Shared passphrase (E2EE): ")
    cipher = Fernet(derive_key(passphrase))

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((HOST, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=HOST) as ssock:
            print("[🔒] Connected via TLS. E2EE enabled with shared passphrase.")
            threading.Thread(target=receive_messages, args=(ssock, cipher, name), daemon=True).start()

            while True:
                msg = input("> ")
                if msg.strip().lower() == "exit":
                    break
                full_msg = f"{name}: {msg}"
                encrypted = cipher.encrypt(full_msg.encode())
                ssock.sendall(encrypted)

if __name__ == "__main__":
    main()