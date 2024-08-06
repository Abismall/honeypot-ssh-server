from datetime import datetime
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import paramiko
import io
from dotenv import load_dotenv
from shell import Shell

load_dotenv()

LOG_DIR = os.getenv("LOG_DIR", "logs")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 3020))

def generate_rsa_key_in_memory():
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return paramiko.RSAKey(file_obj=io.StringIO(private_key.decode('utf-8')))
def handle_connection(server, client, addr):
    transport = None
    channel = None
    try:
        host_key = generate_rsa_key_in_memory()
        transport = paramiko.Transport(client)
        transport.add_server_key(host_key)
        try:
            transport.start_server(server=server)
        except paramiko.SSHException:
            return

        channel = transport.accept()
        if channel is None:
            return

        if addr[0]:
            logfile = os.path.join(
                LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{addr[0]}.txt")
        else:
            logfile = os.path.join(
                LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_unknown.txt")

        shell = Shell(channel, server.username, addr, logfile)
        shell.start()
    except Exception:
        channel and channel.close()
        transport and transport.close()

